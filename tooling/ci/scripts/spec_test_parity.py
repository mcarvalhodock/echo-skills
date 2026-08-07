"""CI script: spec_test_parity.

Verifica paridade entre specs e testes no repositório consumidor.

Convenção do SLE: cada spec em docs/specs/<nome>.md declara, em uma seção
'## Testes vinculados' (ou 'Testes vinculados' no cabeçalho), a lista de
caminhos de arquivos de teste que a cobrem. O script falha se:

  - a spec declara um caminho que não existe no filesystem
  - uma spec produtiva (não legado, não sufixo -log/-fidelidade/-manual-validation)
    não declara nenhum teste vinculado E nao esta marcada com
    'tdd: manual' no cabecalho (v3: TDD manual e permitido)

Ausência da seção quando TDD é manual não é erro — o script apenas verifica
a coerência declarativa. Reforço da homologação é humano.

Uso:
    python spec_test_parity.py [--specs-dir docs/specs] [--project-root .]

Exit codes:
    0 = paridade OK
    1 = uma ou mais violações (descritas em stdout)
    2 = erro de invocação
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

IGNORED_SPEC_SUFFIXES: tuple[str, ...] = (
    "-log.md",
    "-fidelidade.md",
    "-manual-validation.md",
)


@dataclass
class SpecReport:
    path: Path
    declared_tests: list[str]
    tdd_mode: str
    missing_tests: list[str]


def parse_tdd_mode(content: str) -> str:
    match = re.search(
        r"^\s*(?:-\s*)?[Tt][Dd][Dd][- ]?(?:aplic[aá]vel|mode|:)\s*[:=]?\s*"
        r"(ortodoxo|parcial|manual)",
        content,
        re.MULTILINE,
    )
    if match:
        return match.group(1).lower()
    return "ortodoxo"


def parse_declared_tests(content: str) -> list[str]:
    match = re.search(
        r"##\s+Testes\s+vinculados\s*\n(.+?)(?:\n##|\Z)",
        content,
        re.DOTALL | re.IGNORECASE,
    )
    if not match:
        return []

    declared: list[str] = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            item = stripped[2:].strip("`").strip()
            if item:
                declared.append(item)
    return declared


def is_ignored_spec(spec_path: Path) -> bool:
    name = spec_path.name
    return any(name.endswith(suffix) for suffix in IGNORED_SPEC_SUFFIXES)


def analyze_spec(spec_path: Path, project_root: Path) -> SpecReport:
    content = spec_path.read_text(encoding="utf-8")
    declared = parse_declared_tests(content)
    tdd_mode = parse_tdd_mode(content)
    missing = [
        item for item in declared if not (project_root / item).exists()
    ]
    return SpecReport(
        path=spec_path,
        declared_tests=declared,
        tdd_mode=tdd_mode,
        missing_tests=missing,
    )


def evaluate(specs_dir: Path, project_root: Path) -> tuple[int, list[str]]:
    if not specs_dir.exists():
        return 2, [f"specs-dir '{specs_dir}' não existe"]

    violations: list[str] = []
    for spec_path in sorted(specs_dir.rglob("*.md")):
        if is_ignored_spec(spec_path):
            continue

        report = analyze_spec(spec_path, project_root)
        rel = spec_path.relative_to(project_root).as_posix()

        if report.missing_tests:
            for item in report.missing_tests:
                violations.append(
                    f"{rel}: declara teste '{item}' que não existe"
                )

        if not report.declared_tests and report.tdd_mode == "ortodoxo":
            violations.append(
                f"{rel}: sem 'Testes vinculados' e TDD mode='ortodoxo'; "
                f"declare a secao ou explicite 'tdd: parcial/manual'"
            )

    return (1 if violations else 0), violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--specs-dir", default="docs/specs")
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    specs_dir = (project_root / args.specs_dir).resolve()

    exit_code, violations = evaluate(specs_dir, project_root)
    if violations:
        print("spec_test_parity: violações encontradas")
        for line in violations:
            print(f"  - {line}")
    else:
        print("spec_test_parity: OK")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
