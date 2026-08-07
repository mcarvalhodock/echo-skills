"""Testes do script criterion_coverage."""

from __future__ import annotations

from pathlib import Path

from conftest import criterion_coverage


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestExtracaoDeCriterios:
    def test_extrai_criterios_bem_formados(self) -> None:
        content = (
            "## Critérios de aceite\n\n"
            "- **A1**: primeiro criterio\n"
            "- **A2**: segundo criterio\n"
            "- **C1**: contrato arquitetural\n"
        )
        assert criterion_coverage.parse_criteria(content) == ["A1", "A2", "C1"]

    def test_extrai_apenas_padrao_bold_id(self) -> None:
        content = "- **A1**: ok\n- A2: sem bold, ignorado\n"
        assert criterion_coverage.parse_criteria(content) == ["A1"]


class TestCoberturaCompleta:
    def test_todos_criterios_cobertos_passa(self, tmp_path: Path) -> None:
        specs_dir = tmp_path / "docs" / "specs"
        tests_dir = tmp_path / "tests"

        _write(
            specs_dir / "feature.md",
            "## Critérios de aceite\n\n- **A1**: ok\n- **A2**: ok\n",
        )
        _write(
            tests_dir / "test_feature.py",
            "def test_a1():\n    # spec:A1\n    assert True\n\n"
            "def test_a2():\n    # @spec:A2\n    assert True\n",
        )

        exit_code, uncovered = criterion_coverage.evaluate(
            specs_dir, tests_dir, tmp_path
        )
        assert exit_code == 0
        assert uncovered == []

    def test_criterio_sem_cobertura_falha(self, tmp_path: Path) -> None:
        specs_dir = tmp_path / "docs" / "specs"
        tests_dir = tmp_path / "tests"

        _write(
            specs_dir / "feature.md",
            "## Critérios de aceite\n\n- **A1**: ok\n- **A2**: ok\n",
        )
        _write(
            tests_dir / "test_feature.py",
            "def test_a1():\n    # spec:A1\n    assert True\n",
        )

        exit_code, uncovered = criterion_coverage.evaluate(
            specs_dir, tests_dir, tmp_path
        )
        assert exit_code == 1
        assert len(uncovered) == 1
        assert uncovered[0].criterion == "A2"

    def test_cobertura_via_manual_validation_conta(self, tmp_path: Path) -> None:
        specs_dir = tmp_path / "docs" / "specs"

        _write(
            specs_dir / "feature.md",
            "## Critérios de aceite\n\n- **A1**: ok\n- **A2**: ok\n",
        )
        _write(
            specs_dir / "feature-manual-validation.md",
            "- spec:A1\n- spec:A2 (manual)\n",
        )

        exit_code, uncovered = criterion_coverage.evaluate(
            specs_dir, tmp_path / "tests", tmp_path
        )
        assert exit_code == 0
        assert uncovered == []
