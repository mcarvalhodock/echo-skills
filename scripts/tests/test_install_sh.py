"""Testes do install.sh.

Auto-skip se bash não está no PATH (Windows nativo sem Git-bash/WSL).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from _helpers import BASH_BIN, run_sh

pytestmark = pytest.mark.skipif(
    BASH_BIN is None, reason="bash não disponível"
)


class TestHelpAndInvocation:
    def test_help_flag_produz_ajuda(self) -> None:
        result = run_sh(["--help"])
        assert result.returncode == 0
        assert "install.sh" in result.stdout
        assert "COMPONENTS:" in result.stdout

    def test_argumento_desconhecido_retorna_exit_2(self) -> None:
        result = run_sh(["--foo"])
        assert result.returncode == 2

    def test_ajuda_anuncia_a_contagem_certa_de_skills(self) -> None:
        """G5 — a contagem acompanha a lista; hoje são seis."""
        result = run_sh(["--help"])
        assert "5 skills" not in result.stdout
        assert "6 skills" in result.stdout
        assert "orquestrar" in result.stdout
        assert "prototipar-frontend" in result.stdout


class TestDryRun:
    def test_dry_run_all_lista_todas_operacoes(self, fake_target: Path) -> None:
        result = run_sh([
            "--components", "all",
            "--scope", "local",
            "--target-repo", str(fake_target),
            "--dry-run",
        ])
        assert result.returncode == 0
        assert "[dry-run]" in result.stdout
        assert "especificar" in result.stdout
        assert not fake_target.exists()


class TestExecucaoRealSkillsLocal:
    def test_instala_as_quatro_skills(self, fake_target: Path) -> None:
        result = run_sh([
            "--components", "skills",
            "--scope", "local",
            "--target-repo", str(fake_target),
        ])
        assert result.returncode == 0
        for skill in ("especificar", "codificar", "verificar", "homologar"):
            skill_dir = fake_target / ".claude" / "skills" / skill
            assert skill_dir.is_dir()
            assert (skill_dir / "SKILL.md").is_file()

    def test_instala_a_acessoria_de_prototipagem(self, fake_target: Path) -> None:
        """P14 — a acessória entra na mesma lista das quatro do ciclo."""
        result = run_sh([
            "--components", "skills",
            "--scope", "local",
            "--target-repo", str(fake_target),
        ])
        assert result.returncode == 0
        skill_dir = fake_target / ".claude" / "skills" / "prototipar-frontend"
        assert skill_dir.is_dir()
        assert (skill_dir / "SKILL.md").is_file()

    def test_instala_o_orquestrador(self, fake_target: Path) -> None:
        """G4 — `orquestrar` entra na mesma lista das outras."""
        result = run_sh([
            "--components", "skills",
            "--scope", "local",
            "--target-repo", str(fake_target),
        ])
        assert result.returncode == 0
        skill_dir = fake_target / ".claude" / "skills" / "orquestrar"
        assert skill_dir.is_dir()
        assert (skill_dir / "SKILL.md").is_file()

    def test_instala_o_preview_junto_da_skill(self, fake_target: Path) -> None:
        """V13, V14 — o ativo viaja na cópia recursiva, sem lista nova."""
        result = run_sh([
            "--components", "skills",
            "--scope", "local",
            "--target-repo", str(fake_target),
        ])
        assert result.returncode == 0
        preview = (
            fake_target / ".claude" / "skills" / "prototipar-frontend" / "preview"
        )
        assert preview.is_dir(), "preview/ não acompanhou a skill"
        assert (preview / "compose.yml").is_file()


class TestIdempotencia:
    def test_segunda_execucao_emite_skip(self, fake_target: Path) -> None:
        args = [
            "--components", "skills",
            "--scope", "local",
            "--target-repo", str(fake_target),
        ]
        assert run_sh(args).returncode == 0
        second = run_sh(args)
        assert second.returncode == 0
        assert "[skip]" in second.stdout
        assert second.stdout.count("[skip]") >= 4


class TestCiInstall:
    def test_workflows_recebem_warning_mode(self, fake_target: Path) -> None:
        result = run_sh([
            "--components", "ci",
            "--target-repo", str(fake_target),
        ])
        assert result.returncode == 0
        wf_dir = fake_target / ".github" / "workflows"
        assert wf_dir.is_dir()
        for yml in wf_dir.glob("*.yml"):
            content = yml.read_text(encoding="utf-8")
            assert "continue-on-error: true" in content


class TestAlvoInexistente:
    def test_cria_o_diretorio_alvo(self, fake_target: Path) -> None:
        """A1 — o alvo pode não existir ainda; o instalador o cria."""
        assert not fake_target.exists()
        run_sh([
            "--components", "ci",
            "--target-repo", str(fake_target),
        ])
        assert fake_target.is_dir()

    def test_sai_com_zero_em_alvo_inexistente(self, fake_target: Path) -> None:
        """A2 — criar o alvo não é erro; o código de saída é 0."""
        assert not fake_target.exists()
        result = run_sh([
            "--components", "ci",
            "--target-repo", str(fake_target),
        ])
        assert result.returncode == 0, result.stdout + result.stderr


class TestDeteccaoDePython:
    def test_ignora_python3_que_nao_reporta_versao(
        self, fake_target: Path, tmp_path: Path
    ) -> None:
        """A7 — estar no PATH não é executar: o candidato quebrado é descartado.

        Imita o atalho da Microsoft Store, que existe no PATH, sai com erro e
        imprime instrução de instalação em vez de versão.
        """
        stub_dir = tmp_path / "stub"
        stub_dir.mkdir()
        stub = stub_dir / "python3"
        stub.write_text(
            "#!/bin/sh\n"
            "echo 'Python nao foi encontrado; execute sem argumentos para instalar'\n"
            "exit 9009\n",
            encoding="utf-8",
        )
        stub.chmod(0o755)

        result = run_sh(
            ["--components", "ci", "--target-repo", str(fake_target)],
            prefixo_de_path=stub_dir,
        )

        assert result.returncode == 0, result.stdout + result.stderr
        assert (fake_target / ".github" / "workflows").is_dir(), (
            "o 'ci' foi desabilitado por causa do python3 quebrado"
        )


class TestSetupGuide:
    def test_setup_guide_gerado(self, fake_target: Path) -> None:
        result = run_sh([
            "--components", "ci",
            "--target-repo", str(fake_target),
        ])
        assert result.returncode == 0
        setup = fake_target / "SLE-SETUP.md"
        assert setup.is_file()
        content = setup.read_text(encoding="utf-8")
        assert "{{" not in content
        assert str(fake_target) in content
        assert "especificar" in content
