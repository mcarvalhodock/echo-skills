"""Testes do hook block-designer-writing-code.

Cobre pelo menos:
- teste que confirma bloqueio quando designer tenta escrever em código de produção
- teste que confirma não-interferência em operações permitidas
"""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import designer_hook


class TestBloqueiaEscritaEmCodigoProducao:
    def test_designer_escrevendo_em_src_e_bloqueado(
        self, project_root_without_manifest: Path
    ) -> None:
        exit_code, message = designer_hook.evaluate(
            role="designer",
            path="src/app.ts",
            action="write",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
        )
        assert exit_code == 1
        assert "BLOQUEADO" in message
        assert "Designer" in message
        assert "Executor" in message

    def test_designer_escrevendo_em_lib_e_bloqueado(
        self, project_root_without_manifest: Path
    ) -> None:
        exit_code, _ = designer_hook.evaluate(
            role="designer",
            path="lib/util.py",
            action="edit",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
        )
        assert exit_code == 1

    def test_designer_deletando_codigo_producao_e_bloqueado(
        self, project_root_without_manifest: Path
    ) -> None:
        exit_code, _ = designer_hook.evaluate(
            role="designer",
            path="app/main.py",
            action="delete",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
        )
        assert exit_code == 1

    def test_paths_declarados_no_manifesto_substituem_defaults(
        self, project_root_with_manifest: Path
    ) -> None:
        manifest = project_root_with_manifest / ".sle" / "manifesto.md"

        exit_code_declared, _ = designer_hook.evaluate(
            role="designer",
            path="frontend/src/index.tsx",
            action="write",
            manifesto_path=manifest,
        )
        assert exit_code_declared == 1

        exit_code_default_only, _ = designer_hook.evaluate(
            role="designer",
            path="src/index.tsx",
            action="write",
            manifesto_path=manifest,
        )
        assert exit_code_default_only == 0


class TestNaoInterfereEmOperacoesPermitidas:
    def test_designer_escrevendo_spec_e_permitido(
        self, project_root_without_manifest: Path
    ) -> None:
        exit_code, _ = designer_hook.evaluate(
            role="designer",
            path="docs/specs/nova-feature.md",
            action="write",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
        )
        assert exit_code == 0

    def test_designer_escrevendo_plan_e_permitido(
        self, project_root_without_manifest: Path
    ) -> None:
        exit_code, _ = designer_hook.evaluate(
            role="designer",
            path="docs/plans/nova-feature.md",
            action="write",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
        )
        assert exit_code == 0

    def test_designer_escrevendo_prototipo_dentro_de_specs_e_permitido(
        self, project_root_without_manifest: Path
    ) -> None:
        exit_code, _ = designer_hook.evaluate(
            role="designer",
            path="docs/specs/nova-feature-prototipo/index.html",
            action="write",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
        )
        assert exit_code == 0

    def test_designer_atualizando_manifesto_e_permitido(
        self, project_root_without_manifest: Path
    ) -> None:
        exit_code, _ = designer_hook.evaluate(
            role="designer",
            path=".sle/manifesto.md",
            action="edit",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
        )
        assert exit_code == 0

    def test_hook_nao_se_aplica_a_outras_roles(
        self, project_root_without_manifest: Path
    ) -> None:
        for role in ("executor", "validator", "observer"):
            exit_code, _ = designer_hook.evaluate(
                role=role,
                path="src/app.ts",
                action="write",
                manifesto_path=(
                    project_root_without_manifest / ".sle" / "manifesto.md"
                ),
            )
            assert exit_code == 0, f"hook não deve bloquear role={role}"

    def test_hook_nao_se_aplica_a_leitura(
        self, project_root_without_manifest: Path
    ) -> None:
        exit_code, _ = designer_hook.evaluate(
            role="designer",
            path="src/app.ts",
            action="read",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
        )
        assert exit_code == 0


@pytest.mark.parametrize(
    "raw_path,expected_normalized_match",
    [
        ("src\\app.ts", True),
        ("./src/app.ts", True),
        ("src/app.ts", True),
        ("other/thing.ts", False),
    ],
)
def test_normalizacao_de_path(raw_path: str, expected_normalized_match: bool) -> None:
    assert (
        designer_hook.is_production_path(
            raw_path, designer_hook.DEFAULT_PRODUCTION_PATH_PATTERNS
        )
        is expected_normalized_match
    )
