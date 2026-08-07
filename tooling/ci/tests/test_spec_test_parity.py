"""Testes do script spec_test_parity."""

from __future__ import annotations

from pathlib import Path

from conftest import spec_test_parity


def _spec(specs_dir: Path, name: str, body: str) -> None:
    specs_dir.mkdir(parents=True, exist_ok=True)
    (specs_dir / name).write_text(body, encoding="utf-8")


class TestParidadeDeclarada:
    def test_spec_com_teste_existente_passa(self, tmp_path: Path) -> None:
        specs_dir = tmp_path / "docs" / "specs"
        _spec(
            specs_dir,
            "feature.md",
            "# Feature\n\n## Testes vinculados\n\n- `tests/test_feature.py`\n",
        )
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_feature.py").write_text(
            "def test_x(): assert True\n", encoding="utf-8"
        )

        exit_code, violations = spec_test_parity.evaluate(specs_dir, tmp_path)
        assert exit_code == 0
        assert violations == []

    def test_spec_com_teste_faltando_falha(self, tmp_path: Path) -> None:
        specs_dir = tmp_path / "docs" / "specs"
        _spec(
            specs_dir,
            "feature.md",
            "# Feature\n\n## Testes vinculados\n\n- `tests/inexistente.py`\n",
        )

        exit_code, violations = spec_test_parity.evaluate(specs_dir, tmp_path)
        assert exit_code == 1
        assert any("inexistente.py" in v for v in violations)

    def test_spec_sem_testes_com_tdd_ortodoxo_falha(
        self, tmp_path: Path
    ) -> None:
        specs_dir = tmp_path / "docs" / "specs"
        _spec(specs_dir, "feature.md", "# Feature\n\ntdd: ortodoxo\n")

        exit_code, violations = spec_test_parity.evaluate(specs_dir, tmp_path)
        assert exit_code == 1
        assert any("sem 'Testes vinculados'" in v for v in violations)

    def test_spec_sem_testes_com_tdd_manual_passa(
        self, tmp_path: Path
    ) -> None:
        specs_dir = tmp_path / "docs" / "specs"
        _spec(
            specs_dir,
            "feature.md",
            "# Feature\n\ntdd: manual\n\n"
            "criterios cobertos por manual-validation.md\n",
        )

        exit_code, violations = spec_test_parity.evaluate(specs_dir, tmp_path)
        assert exit_code == 0
        assert violations == []


class TestIgnoraSufixos:
    def test_log_e_fidelidade_sao_ignorados(self, tmp_path: Path) -> None:
        specs_dir = tmp_path / "docs" / "specs"
        _spec(specs_dir, "feature-log.md", "# Log\n")
        _spec(specs_dir, "feature-fidelidade.md", "# Fidelidade\n")
        _spec(
            specs_dir,
            "feature-manual-validation.md",
            "# Manual validation\n",
        )

        exit_code, _ = spec_test_parity.evaluate(specs_dir, tmp_path)
        assert exit_code == 0
