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


class TestEmendaV5:
    """A invariante 2 na redação v5: escrever pode; assinar calado, não."""

    def _log_com(self, raiz: Path, conteudo: str) -> Path:
        log = raiz / ".sle" / "pressao-metodo.md"
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(conteudo, encoding="utf-8")
        return log

    def test_emenda_registrada_libera_codigo_de_producao(
        self, project_root_without_manifest: Path
    ) -> None:
        log = self._log_com(
            project_root_without_manifest,
            "| 2026-08-08 | spec-26 | @criterio:B1 | código | humano | "
            "não-independente |\n",
        )

        exit_code, message = validator_hook.evaluate(
            role="validator",
            path="src/app.ts",
            action="edit",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
            emenda="spec-26",
            log_path=log,
        )
        assert exit_code == 0
        assert "PERMITIDO em emenda" in message
        assert "independente" in message

    def test_emenda_sem_registro_e_bloqueada(
        self, project_root_without_manifest: Path
    ) -> None:
        log = self._log_com(project_root_without_manifest, "# vazio\n")

        exit_code, message = validator_hook.evaluate(
            role="validator",
            path="src/app.ts",
            action="edit",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
            emenda="spec-26",
            log_path=log,
        )
        assert exit_code == 1
        assert "não registrada" in message

    def test_registro_de_outra_spec_nao_autoriza_esta(
        self, project_root_without_manifest: Path
    ) -> None:
        log = self._log_com(
            project_root_without_manifest,
            "| 2026-08-08 | spec-19 | @criterio:A1 | código | humano | "
            "não-independente |\n",
        )

        exit_code, _ = validator_hook.evaluate(
            role="validator",
            path="src/app.ts",
            action="edit",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
            emenda="spec-26",
            log_path=log,
        )
        assert exit_code == 1

    def test_linha_que_cita_a_spec_sem_admitir_quem_assina_nao_basta(
        self, project_root_without_manifest: Path
    ) -> None:
        log = self._log_com(
            project_root_without_manifest,
            "| 2026-08-08 | spec-26 | @criterio:B1 | código | humano | ok |\n",
        )

        exit_code, _ = validator_hook.evaluate(
            role="validator",
            path="src/app.ts",
            action="edit",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
            emenda="spec-26",
            log_path=log,
        )
        assert exit_code == 1

    def test_marcador_sem_acento_tambem_vale(
        self, project_root_without_manifest: Path
    ) -> None:
        log = self._log_com(
            project_root_without_manifest,
            "| 2026-08-08 | spec-26 | @criterio:B1 | codigo | humano | "
            "nao-independente |\n",
        )

        exit_code, _ = validator_hook.evaluate(
            role="validator",
            path="src/app.ts",
            action="edit",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
            emenda="spec-26",
            log_path=log,
        )
        assert exit_code == 0

    def test_na_fase_traduzir_nem_emenda_registrada_libera(
        self, project_root_without_manifest: Path
    ) -> None:
        log = self._log_com(
            project_root_without_manifest,
            "| 2026-08-08 | spec-26 | @criterio:B1 | código | humano | "
            "não-independente |\n",
        )

        exit_code, message = validator_hook.evaluate(
            role="validator",
            path="src/app.ts",
            action="edit",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
            emenda="spec-26",
            fase="traduzir",
            log_path=log,
        )
        assert exit_code == 1
        assert "Traduzir" in message

    def test_log_inexistente_bloqueia_a_emenda(
        self, project_root_without_manifest: Path
    ) -> None:
        exit_code, _ = validator_hook.evaluate(
            role="validator",
            path="src/app.ts",
            action="edit",
            manifesto_path=project_root_without_manifest / ".sle" / "manifesto.md",
            emenda="spec-26",
            log_path=project_root_without_manifest / ".sle" / "nao-existe.md",
        )
        assert exit_code == 1


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
