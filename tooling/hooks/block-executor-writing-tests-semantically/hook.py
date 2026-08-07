"""Hook: block-executor-writing-tests-semantically.

Bloqueia o Executor (skill do SLE) de alterar a semântica de testes.
Enforcement do ajuste v4 do SLE: Executor pode fazer refactor não-semântico
em testes (DRY, extração de fixtures, renomeações internas), mas nunca
adicionar/remover casos de teste ou alterar assertions.

Duas subcommands:
  snapshot  — coleta assinatura semântica dos testes numa pasta
  check     — compara snapshot antigo com estado atual, retorna violação
              se detectar mudança semântica quando role=executor

Fluxo esperado no harness:
    # antes de editar arquivo em tests/:
    python hook.py snapshot --tests-dir tests/ --output .sle-snapshot.json

    # depois:
    python hook.py check --tests-dir tests/ --snapshot .sle-snapshot.json \
                         --role executor

Exit codes:
    0 = permitido / snapshot OK
    1 = violação semântica bloqueada
    2 = erro de invocação
    3 = snapshot inexistente ou corrompido

Heurística: extrai identificadores de testes e conjunto de assertions por teste
via padrões textuais para Python (pytest), JS/TS (jest/vitest) e Go. Não roda
a suíte real — as dependências do repositório consumidor são desconhecidas.
Detecta os casos que interessam: adição/remoção de teste, mudança de assertion.
Não detecta bugs sutis dentro da mesma assertion — revisão humana continua
responsável nesse limite.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

TEST_FILE_GLOBS: tuple[str, ...] = (
    "**/test_*.py",
    "**/*_test.py",
    "**/*.test.ts",
    "**/*.test.tsx",
    "**/*.test.js",
    "**/*.test.jsx",
    "**/*.spec.ts",
    "**/*.spec.js",
    "**/*_test.go",
)

TEST_NAME_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^\s*def\s+(test_\w+)\s*\(", re.MULTILINE),
    re.compile(
        r"""(?:^|\s)(?:it|test)\s*\(\s*['"]([^'"]+)['"]""",
        re.MULTILINE,
    ),
    re.compile(r"^\s*func\s+(Test\w+)\s*\(", re.MULTILINE),
)

ASSERTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^\s*assert\s+.+$", re.MULTILINE),
    re.compile(r"\bexpect\s*\([^)]*\)\s*\.\w[\w\.]*\s*\([^)]*\)"),
    re.compile(r"\bself\.assert\w+\s*\([^)]*\)"),
    re.compile(r"\bt\.(?:Errorf|Fatalf|Fail|Error)\s*\([^)]*\)"),
)


@dataclass(frozen=True)
class TestFileSignature:
    """Assinatura semântica de um arquivo de teste.

    Não guarda o texto integral (isso permitiria reconstrução perfeita e
    tornaria diffs verbosos), apenas o conjunto de nomes de testes e a
    contagem/hash agregado das assertions.
    """

    path: str
    test_names: tuple[str, ...]
    assertion_count: int
    assertion_hash: str


@dataclass
class Snapshot:
    files: dict[str, TestFileSignature] = field(default_factory=dict)

    def to_json(self) -> str:
        payload = {
            path: {
                "path": sig.path,
                "test_names": list(sig.test_names),
                "assertion_count": sig.assertion_count,
                "assertion_hash": sig.assertion_hash,
            }
            for path, sig in self.files.items()
        }
        return json.dumps(payload, indent=2, sort_keys=True)

    @classmethod
    def from_json(cls, raw: str) -> "Snapshot":
        data = json.loads(raw)
        snapshot = cls()
        for path, entry in data.items():
            snapshot.files[path] = TestFileSignature(
                path=entry["path"],
                test_names=tuple(entry["test_names"]),
                assertion_count=entry["assertion_count"],
                assertion_hash=entry["assertion_hash"],
            )
        return snapshot


def extract_test_names(content: str) -> tuple[str, ...]:
    names: list[str] = []
    for pattern in TEST_NAME_PATTERNS:
        names.extend(pattern.findall(content))
    return tuple(sorted(names))


def extract_assertions(content: str) -> list[str]:
    matches: list[str] = []
    for pattern in ASSERTION_PATTERNS:
        for match in pattern.findall(content):
            normalized = re.sub(r"\s+", " ", match).strip()
            matches.append(normalized)
    return sorted(matches)


def build_signature(file_path: Path, root: Path) -> TestFileSignature | None:
    if not file_path.is_file():
        return None

    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None

    names = extract_test_names(content)
    assertions = extract_assertions(content)
    joined = "\n".join(assertions)
    digest = hashlib.sha256(joined.encode("utf-8")).hexdigest()

    return TestFileSignature(
        path=str(file_path.relative_to(root)).replace("\\", "/"),
        test_names=names,
        assertion_count=len(assertions),
        assertion_hash=digest,
    )


def iter_test_files(tests_dir: Path) -> Iterable[Path]:
    seen: set[Path] = set()
    for glob in TEST_FILE_GLOBS:
        for candidate in tests_dir.glob(glob):
            resolved = candidate.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            yield candidate


def build_snapshot(tests_dir: Path, root: Path) -> Snapshot:
    snapshot = Snapshot()
    for test_file in iter_test_files(tests_dir):
        signature = build_signature(test_file, root)
        if signature is not None:
            snapshot.files[signature.path] = signature
    return snapshot


@dataclass
class Divergence:
    added_tests: list[str] = field(default_factory=list)
    removed_tests: list[str] = field(default_factory=list)
    changed_assertions: list[str] = field(default_factory=list)
    new_files: list[str] = field(default_factory=list)
    removed_files: list[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (
            self.added_tests
            or self.removed_tests
            or self.changed_assertions
            or self.new_files
            or self.removed_files
        )

    def describe(self) -> str:
        parts: list[str] = []
        if self.new_files:
            parts.append(f"arquivos de teste novos: {self.new_files}")
        if self.removed_files:
            parts.append(f"arquivos de teste removidos: {self.removed_files}")
        if self.added_tests:
            parts.append(f"testes adicionados: {self.added_tests}")
        if self.removed_tests:
            parts.append(f"testes removidos: {self.removed_tests}")
        if self.changed_assertions:
            parts.append(
                f"assertions alteradas em: {self.changed_assertions}"
            )
        return "; ".join(parts)


def compare_snapshots(before: Snapshot, after: Snapshot) -> Divergence:
    divergence = Divergence()

    before_paths = set(before.files)
    after_paths = set(after.files)
    divergence.new_files = sorted(after_paths - before_paths)
    divergence.removed_files = sorted(before_paths - after_paths)

    for path in before_paths & after_paths:
        before_sig = before.files[path]
        after_sig = after.files[path]

        before_names = set(before_sig.test_names)
        after_names = set(after_sig.test_names)

        added = sorted(after_names - before_names)
        removed = sorted(before_names - after_names)
        for name in added:
            divergence.added_tests.append(f"{path}::{name}")
        for name in removed:
            divergence.removed_tests.append(f"{path}::{name}")

        if before_sig.assertion_hash != after_sig.assertion_hash:
            if before_sig.assertion_count != after_sig.assertion_count:
                divergence.changed_assertions.append(
                    f"{path} (assertion_count "
                    f"{before_sig.assertion_count} -> "
                    f"{after_sig.assertion_count})"
                )
            else:
                divergence.changed_assertions.append(
                    f"{path} (hash alterado com mesma contagem)"
                )

    return divergence


def cmd_snapshot(args: argparse.Namespace) -> int:
    tests_dir = Path(args.tests_dir).resolve()
    project_root = Path(args.project_root).resolve()
    if not tests_dir.exists():
        print(f"erro: tests-dir '{tests_dir}' não existe")
        return 2

    snapshot = build_snapshot(tests_dir, project_root)
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(snapshot.to_json(), encoding="utf-8")
    print(
        f"snapshot escrito em {output_path} "
        f"({len(snapshot.files)} arquivos de teste)"
    )
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    tests_dir = Path(args.tests_dir).resolve()
    project_root = Path(args.project_root).resolve()
    snapshot_path = Path(args.snapshot).resolve()

    if not snapshot_path.exists():
        print(f"erro: snapshot '{snapshot_path}' inexistente")
        return 3

    try:
        before = Snapshot.from_json(snapshot_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, KeyError) as exc:
        print(f"erro: snapshot corrompido ({exc})")
        return 3

    after = build_snapshot(tests_dir, project_root)
    divergence = compare_snapshots(before, after)

    if divergence.is_empty():
        print("nenhuma mudança semântica detectada nos testes")
        return 0

    if args.role != "executor":
        print(
            f"mudança semântica detectada mas role={args.role} tem permissão "
            f"({divergence.describe()})"
        )
        return 0

    print(
        f"BLOQUEADO: Executor (skill do SLE) alterou a semântica de testes.\n"
        f"Diferenças: {divergence.describe()}.\n"
        f"Executor pode fazer refactor não-semântico (DRY, fixtures, "
        f"renomeações internas) desde que a suíte permaneça equivalente. "
        f"Adicionar/remover teste ou mudar assertion é territorio do "
        f"Validator.\n"
        f"Se detectou bug semântico legítimo no teste, faça handoff estrutural: "
        f"registre o bug no homologation log ou em .sle/pressao-metodo.md e "
        f"retorne a suíte ao Validator em nova sessão (poder estrutural v4)."
    )
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot_parser = subparsers.add_parser("snapshot")
    snapshot_parser.add_argument("--tests-dir", required=True)
    snapshot_parser.add_argument("--output", required=True)
    snapshot_parser.add_argument("--project-root", default=".")
    snapshot_parser.set_defaults(func=cmd_snapshot)

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--tests-dir", required=True)
    check_parser.add_argument("--snapshot", required=True)
    check_parser.add_argument("--role", required=True)
    check_parser.add_argument("--project-root", default=".")
    check_parser.set_defaults(func=cmd_check)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
