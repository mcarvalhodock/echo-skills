"""CI script: pr_spec_diff.

Bloqueia PR que modifica código de produção sem alteração correspondente
em spec. Enforcement do princípio 'spec é a única fonte de verdade' do SLE.

Como funciona:
  - Recebe base ref (default: origin/main) e head ref (default: HEAD).
  - Chama git para listar arquivos alterados entre base e head.
  - Se algum arquivo alterado está em paths de produção (declarados no
    manifesto ou default), exige que pelo menos um arquivo em docs/specs/
    (excluindo -log.md e -fidelidade.md — logs são gerados na execução)
    também esteja alterado.

Uso:
    python pr_spec_diff.py [--base-ref origin/main] [--head-ref HEAD]
                           [--project-root .] [--manifesto <path>]

Exit codes:
    0 = spec acompanhou o código (ou nenhum código de producao mudou)
    1 = codigo mudou sem spec correspondente
    2 = erro de invocação
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_PRODUCTION_PATH_PATTERNS: tuple[str, ...] = (
    r"^src/",
    r"^lib/",
    r"^app/",
    r"^internal/",
    r"^pkg/",
    r"^cmd/",
)


def is_production_path(rel_path: str, patterns: tuple[str, ...]) -> bool:
    normalized = rel_path.replace("\\", "/").lstrip("./")
    return any(re.match(p, normalized) for p in patterns)


def is_spec_change(rel_path: str) -> bool:
    normalized = rel_path.replace("\\", "/").lstrip("./")
    if not normalized.startswith("docs/specs/"):
        return False
    return not any(
        normalized.endswith(suffix)
        for suffix in ("-log.md", "-fidelidade.md")
    )


def read_production_patterns_from_manifest(
    manifesto_path: Path,
) -> tuple[str, ...]:
    if not manifesto_path.exists():
        return DEFAULT_PRODUCTION_PATH_PATTERNS

    content = manifesto_path.read_text(encoding="utf-8")
    match = re.search(
        r"##\s+Paths?\s+de\s+produ[cç][aã]o\s*\n(.+?)(?:\n##|\Z)",
        content,
        re.DOTALL | re.IGNORECASE,
    )
    if not match:
        return DEFAULT_PRODUCTION_PATH_PATTERNS

    declared: list[str] = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            declared.append(stripped[2:].strip("`").strip())

    return tuple(declared) if declared else DEFAULT_PRODUCTION_PATH_PATTERNS


def list_changed_files(
    base_ref: str, head_ref: str, project_root: Path
) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...{head_ref}"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git diff falhou (base={base_ref}, head={head_ref}): "
            f"{result.stderr.strip()}"
        )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def evaluate(
    changed: list[str], production_patterns: tuple[str, ...]
) -> tuple[int, list[str]]:
    production_changes = [
        p for p in changed if is_production_path(p, production_patterns)
    ]
    spec_changes = [p for p in changed if is_spec_change(p)]

    if production_changes and not spec_changes:
        return 1, production_changes

    return 0, production_changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--head-ref", default="HEAD")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--manifesto", default=None)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    manifesto_path = (
        Path(args.manifesto).resolve()
        if args.manifesto
        else project_root / ".sle" / "manifesto.md"
    )

    try:
        changed = list_changed_files(args.base_ref, args.head_ref, project_root)
    except RuntimeError as exc:
        print(f"erro: {exc}")
        return 2

    production_patterns = read_production_patterns_from_manifest(manifesto_path)
    exit_code, production_changes = evaluate(changed, production_patterns)

    if exit_code == 1:
        print(
            "pr_spec_diff: código de produção mudou sem spec correspondente"
        )
        for path in production_changes:
            print(f"  - {path}")
        print(
            "  --> altere ou crie um arquivo em docs/specs/ documentando "
            "a mudança."
        )
    else:
        print("pr_spec_diff: OK")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
