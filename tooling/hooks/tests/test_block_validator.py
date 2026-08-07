"""Testes do hook block-validator-writing-code."""

from __future__ import annotations

from pathlib import Path

from conftest import validator_hook


class TestBloqueiaEscritaEmCodigoProducao:
    def test_validator_escrevendo_em_src_e_bloqueado(
        self, project_root_without_manifest: Path
    ) -> None:
        exit_code, message = validator_hook.evaluate(
            role="validator",
            path="src/app.ts",
            action="write",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
        )
        assert exit_code == 1
        assert "BLOQUEADO" in message
        assert "Validator" in message
        assert "Executor" in message

    def test_validator_editando_lib_e_bloqueado(
        self, project_root_without_manifest: Path
    ) -> None:
        exit_code, _ = validator_hook.evaluate(
            role="validator",
            path="lib/util.py",
            action="edit",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
        )
        assert exit_code == 1

    def test_paths_declarados_no_manifesto_substituem_defaults(
        self, project_root_with_manifest: Path
    ) -> None:
        manifest = project_root_with_manifest / ".sle" / "manifesto.md"

        exit_code_declared, _ = validator_hook.evaluate(
            role="validator",
            path="backend/app/service.py",
            action="edit",
            manifesto_path=manifest,
        )
        assert exit_code_declared == 1


class TestNaoInterfereEmOperacoesPermitidas:
    def test_validator_escrevendo_testes_e_permitido(
        self, project_root_without_manifest: Path
    ) -> None:
        for path in (
            "tests/app.test.ts",
            "test/unit.py",
            "spec/domain_spec.rb",
            "__tests__/component.test.tsx",
        ):
            exit_code, _ = validator_hook.evaluate(
                role="validator",
                path=path,
                action="write",
                manifesto_path=(
                    project_root_without_manifest / ".sle" / "manifesto.md"
                ),
            )
            assert exit_code == 0, f"deveria permitir: {path}"

    def test_validator_escrevendo_homologation_log_e_permitido(
        self, project_root_without_manifest: Path
    ) -> None:
        exit_code, _ = validator_hook.evaluate(
            role="validator",
            path="docs/specs/nova-feature-log.md",
            action="write",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
        )
        assert exit_code == 0

    def test_validator_escrevendo_manual_validation_e_permitido(
        self, project_root_without_manifest: Path
    ) -> None:
        exit_code, _ = validator_hook.evaluate(
            role="validator",
            path="docs/specs/nova-feature-manual-validation.md",
            action="write",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
        )
        assert exit_code == 0

    def test_validator_escrevendo_fidelidade_e_permitido(
        self, project_root_without_manifest: Path
    ) -> None:
        exit_code, _ = validator_hook.evaluate(
            role="validator",
            path="docs/specs/nova-feature-fidelidade.md",
            action="write",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
        )
        assert exit_code == 0

    def test_validator_registrando_pressao_metodo_e_permitido(
        self, project_root_without_manifest: Path
    ) -> None:
        exit_code, _ = validator_hook.evaluate(
            role="validator",
            path=".sle/pressao-metodo.md",
            action="edit",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
        )
        assert exit_code == 0

    def test_hook_nao_se_aplica_a_outras_roles(
        self, project_root_without_manifest: Path
    ) -> None:
        for role in ("designer", "executor", "observer"):
            exit_code, _ = validator_hook.evaluate(
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
        exit_code, _ = validator_hook.evaluate(
            role="validator",
            path="src/app.ts",
            action="read",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
        )
        assert exit_code == 0
