"""CI script: criterion_coverage.

Verifica que cada critério de aceite declarado numa spec aparece como
marcador em pelo menos um teste (ou está listado no plano de validação
manual, quando TDD é parcial/manual).

Convenção do SLE:
  - Critérios são declarados em '## Critérios de aceite' com bullets no
    formato '- **A1**: descricao' ou '- **C2**: descricao'.
  - Testes automatizados marcam cobertura com um comentário ou tag
    contendo 'spec:<ID>' (ex.: 'spec:A1', '@spec:C2'). O marcador pode
    aparecer em qualquer linha do teste.
  - Alternativa: um arquivo <spec>-manual-validation.md pode listar o ID
    coberto (mesmo formato de bullet), para itens não-automatizáveis.

Falha se algum critério não tem cobertura em nenhum lugar.

Uso:
    python criterion_coverage.py [--specs-dir docs/specs] [--tests-dir tests]
                                 [--project-root .]

Exit codes:
    0 = todos os critérios cobertos
    1 = criterios sem cobertura
    2 = erro de invocação
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

CRITERION_PATTERN = re.compile(
    r"^\s*-\s+\*\*([A-Z]\d+)\*\*\s*:", re.MULTILINE
)

MARKER_PATTERN = re.compile(r"spec\s*:\s*([A-Z]\d+)", re.IGNORECASE)

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


@dataclass
class Uncovered:
    spec: str
    criterion: str


def parse_criteria(content: str) -> list[str]:
    return CRITERION_PATTERN.findall(content)


def collect_covered_ids(*sources: Path) -> set[str]:
    covered: set[str] = set()
    for source in sources:
        if not source.exists():
            continue
        for file_path in _iter_files(source):
            try:
                text = file_path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for match in MARKER_PATTERN.findall(text):
                covered.add(match.upper())
    return covered


def _iter_files(root: Path):
    if root.is_file():
        yield root
        return
    for glob in TEST_FILE_GLOBS:
        yield from root.glob(glob)
    yield from root.glob("**/*-manual-validation.md")


def evaluate(
    specs_dir: Path,
    tests_dir: Path,
    project_root: Path,
) -> tuple[int, list[Uncovered]]:
    if not specs_dir.exists():
        return 2, []

    uncovered: list[Uncovered] = []
    covered_ids = collect_covered_ids(tests_dir, specs_dir)

    for spec_path in sorted(specs_dir.rglob("*.md")):
        name = spec_path.name
        if any(
            name.endswith(suffix)
            for suffix in ("-log.md", "-fidelidade.md", "-manual-validation.md")
        ):
            continue

        content = spec_path.read_text(encoding="utf-8")
        criteria = parse_criteria(content)
        rel = spec_path.relative_to(project_root).as_posix()

        for criterion in criteria:
            if criterion.upper() not in covered_ids:
                uncovered.append(Uncovered(spec=rel, criterion=criterion))

    return (1 if uncovered else 0), uncovered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--specs-dir", default="docs/specs")
    parser.add_argument("--tests-dir", default="tests")
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    specs_dir = (project_root / args.specs_dir).resolve()
    tests_dir = (project_root / args.tests_dir).resolve()

    exit_code, uncovered = evaluate(specs_dir, tests_dir, project_root)
    if uncovered:
        print("criterion_coverage: critérios sem cobertura")
        for item in uncovered:
            print(f"  - {item.spec}: critério {item.criterion}")
    else:
        print("criterion_coverage: OK")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
