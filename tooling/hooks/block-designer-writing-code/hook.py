"""Hook: block-designer-writing-code.

Bloqueia o Designer (skill do SLE) de escrever código de produção.
Enforcement da primeira invariante do SLE: Designer != Executor.

Uso via CLI:
    python hook.py --role <role> --path <path> --action <action>
                   [--manifesto <path>] [--project-root <path>]

Args:
    --role: identidade do agente ativo (designer, validator, executor, observer)
    --path: caminho do arquivo alvo da operação
    --action: tipo de operação (write, edit, delete)
    --manifesto: caminho para .sle/manifesto.md (default: <project-root>/.sle/manifesto.md)
    --project-root: raiz do repositório (default: cwd)

Exit codes:
    0 = operação permitida
    1 = operação bloqueada (motivo em stdout)
    2 = erro de invocação (args inválidos, arquivo faltando, etc.)

O hook é agnóstico ao harness. README explica como plugar em Claude Code e Cursor.
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

ALLOWED_DESIGNER_PATH_PATTERNS: tuple[str, ...] = (
    r"^docs/specs/",
    r"^docs/plans/",
    r"^\.sle/",
    r"^\.echo/",
)


def is_production_path(rel_path: str, patterns: tuple[str, ...]) -> bool:
    normalized = rel_path.replace("\\", "/").lstrip("./")
    return any(re.match(p, normalized) for p in patterns)


def is_designer_allowed_path(rel_path: str) -> bool:
    normalized = rel_path.replace("\\", "/").lstrip("./")
    return any(re.match(p, normalized) for p in ALLOWED_DESIGNER_PATH_PATTERNS)


def read_production_patterns_from_manifest(
    manifesto_path: Path,
) -> tuple[str, ...]:
    """Lê padrões de path de código de produção do manifesto, se declarados.

    Manifesto pode declarar em seção 'Padrão de código local' ou 'Paths de produção'.
    Se não declarados, retorna padrões default. Ausência degrada, não bloqueia.
    """
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
    """Avalia a operação. Retorna (exit_code, mensagem)."""
    if role != "designer":
        return 0, f"hook não se aplica: role={role}"

    if action not in {"write", "edit", "delete"}:
        return 0, f"hook não se aplica: action={action}"

    if is_designer_allowed_path(path):
        return 0, f"path permitido para designer: {path}"

    production_patterns = read_production_patterns_from_manifest(manifesto_path)
    if is_production_path(path, production_patterns):
        return (
            1,
            (
                f"BLOQUEADO: Designer (skill do SLE) não pode escrever código de "
                f"produção. Caminho '{path}' bate com padrão de produção do "
                f"repositório. Invariante 1 do SLE: Designer != Executor.\n"
                f"Se a intenção é: (a) especificar/desenhar, use paths em docs/specs/ "
                f"ou docs/plans/; (b) prototipar em N3, use "
                f"docs/specs/[nome]-prototipo/; (c) implementar código de produção, "
                f"faça handoff estrutural para a skill 'executor' em nova sessão."
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
