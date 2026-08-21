"""Testes do script pr_spec_diff (unidade da funcao evaluate).

O componente `list_changed_files` chama `git diff` de verdade — deixamos
para integração; aqui focamos na lógica de decisão.
"""

from __future__ import annotations

from pathlib import Path

from _ci_helpers import pr_spec_diff

REPO_ROOT = Path(__file__).resolve().parents[3]


class TestClassificacaoDePath:
    def test_reconhece_paths_de_producao(self) -> None:
        patterns = pr_spec_diff.DEFAULT_PRODUCTION_PATH_PATTERNS
        assert pr_spec_diff.is_production_path("src/a.ts", patterns)
        assert pr_spec_diff.is_production_path("lib/util.py", patterns)
        assert not pr_spec_diff.is_production_path("tests/x.py", patterns)
        assert not pr_spec_diff.is_production_path("docs/specs/a.md", patterns)

    def test_reconhece_alteracoes_de_spec(self) -> None:
        assert pr_spec_diff.is_spec_change("docs/specs/feature.md")
        assert not pr_spec_diff.is_spec_change("docs/specs/feature-log.md")
        assert not pr_spec_diff.is_spec_change(
            "docs/specs/feature-fidelidade.md"
        )
        assert not pr_spec_diff.is_spec_change("docs/notes.md")


class TestEvaluate:
    def test_codigo_sem_spec_falha(self) -> None:
        exit_code, offending = pr_spec_diff.evaluate(
            ["src/app.ts", "src/service.ts"],
            pr_spec_diff.DEFAULT_PRODUCTION_PATH_PATTERNS,
        )
        assert exit_code == 1
        assert offending == ["src/app.ts", "src/service.ts"]

    def test_codigo_com_spec_passa(self) -> None:
        exit_code, _ = pr_spec_diff.evaluate(
            ["src/app.ts", "docs/specs/nova.md"],
            pr_spec_diff.DEFAULT_PRODUCTION_PATH_PATTERNS,
        )
        assert exit_code == 0

    def test_apenas_docs_passa(self) -> None:
        exit_code, _ = pr_spec_diff.evaluate(
            ["docs/specs/nova.md", "README.md"],
            pr_spec_diff.DEFAULT_PRODUCTION_PATH_PATTERNS,
        )
        assert exit_code == 0

    def test_log_e_fidelidade_nao_contam_como_spec(self) -> None:
        exit_code, _ = pr_spec_diff.evaluate(
            ["src/app.ts", "docs/specs/nova-log.md"],
            pr_spec_diff.DEFAULT_PRODUCTION_PATH_PATTERNS,
        )
        assert exit_code == 1


class TestManifestoDesteRepositorio:
    """Lê o manifesto real, e não um fixture: o que se mede é a declaração
    deste repositório sobre o pacote do plugin."""

    def test_pacote_do_plugin_conta_como_producao(self) -> None:
        # spec:M10
        patterns = pr_spec_diff.read_production_patterns_from_manifest(
            REPO_ROOT / ".sle" / "manifesto.md"
        )
        assert pr_spec_diff.is_production_path(".cursor-plugin/plugin.json", patterns)
