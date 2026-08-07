"""Hook: block-validator-writing-code.

Bloqueia o Validator (skill do SLE) de escrever código de produção.
Enforcement da segunda invariante do SLE: Executor != Validator.

O Validator escreve testes (BDD + contrato arquitetural + fidelidade),
homologation logs, planos de validação manual (quando TDD é parcial/manual —
v3 do método) e entradas em .sle/pressao-metodo.md. Nunca código de produção.

Uso via CLI:
    python hook.py --role <role> --path <path> --action <action>
                   [--manifesto <path>] [--project-root <path>]

Exit codes:
    0 = operação permitida
    1 = operação bloqueada (motivo em stdout)
    2 = erro de invocação
"""

from __future__ import annotations

import argparse
import re
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

ALLOWED_VALIDATOR_PATH_PATTERNS: tuple[str, ...] = (
    r"^tests?/",
    r"^spec/",
    r"^__tests__/",
    r"^docs/specs/.*-log\.md$",
    r"^docs/specs/.*-manual-validation\.md$",
    r"^docs/specs/.*-fidelidade\.md$",
    r"^\.sle/pressao-metodo\.md$",
    r"^\.sle/pressao-catalogo\.md$",
    r"^\.echo/pressao-catalogo\.md$",
)


def is_production_path(rel_path: str, patterns: tuple[str, ...]) -> bool:
    normalized = rel_path.replace("\\", "/").lstrip("./")
    return any(re.match(p, normalized) for p in patterns)


def is_validator_allowed_path(rel_path: str) -> bool:
    normalized = rel_path.replace("\\", "/").lstrip("./")
    return any(re.match(p, normalized) for p in ALLOWED_VALIDATOR_PATH_PATTERNS)


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


def evaluate(
    role: str,
    path: str,
    action: str,
    manifesto_path: Path,
) -> tuple[int, str]:
    if role != "validator":
        return 0, f"hook não se aplica: role={role}"

    if action not in {"write", "edit", "delete"}:
        return 0, f"hook não se aplica: action={action}"

    if is_validator_allowed_path(path):
        return 0, f"path permitido para validator: {path}"

    production_patterns = read_production_patterns_from_manifest(manifesto_path)
    if is_production_path(path, production_patterns):
        return (
            1,
            (
                f"BLOQUEADO: Validator (skill do SLE) não pode escrever código de "
                f"produção. Caminho '{path}' bate com padrão de produção do "
                f"repositório. Invariante 2 do SLE: Executor != Validator.\n"
                f"O Validator escreve: (a) testes em tests/, test/ ou __tests__/; "
                f"(b) homologation log em docs/specs/*-log.md; "
                f"(c) plano de validação manual (quando TDD é parcial/manual) em "
                f"docs/specs/*-manual-validation.md; "
                f"(d) testes de fidelidade em docs/specs/*-fidelidade.md; "
                f"(e) pressão-método em .sle/pressao-metodo.md.\n"
                f"Se precisa alterar código de produção (ex.: para corrigir bug "
                f"achado na homologação), faça handoff estrutural: registre a "
                f"não-conformidade no log, retorne para 'executor' em nova sessão."
            ),
        )

    return 0, f"path fora do escopo de produção declarado: {path}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--action", required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--manifesto", default=None)

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()
    manifesto_path = (
        Path(args.manifesto).resolve()
        if args.manifesto
        else project_root / ".sle" / "manifesto.md"
    )
    if not manifesto_path.exists():
        legacy = project_root / ".echo" / "manifesto.md"
        if legacy.exists():
            manifesto_path = legacy

    exit_code, message = evaluate(
        role=args.role,
        path=args.path,
        action=args.action,
        manifesto_path=manifesto_path,
    )
    print(message)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
