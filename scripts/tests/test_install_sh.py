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
        assert "designer" in result.stdout
        assert not fake_target.exists()


class TestExecucaoRealSkillsLocal:
    def test_instala_as_quatro_skills(self, fake_target: Path) -> None:
        result = run_sh([
            "--components", "skills",
            "--scope", "local",
            "--target-repo", str(fake_target),
        ])
        assert result.returncode == 0
        for skill in ("designer", "validator", "executor", "observer"):
            skill_dir = fake_target / ".claude" / "skills" / skill
            assert skill_dir.is_dir()
            assert (skill_dir / "SKILL.md").is_file()


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


class TestHooksInstall:
    def test_gitignore_nao_duplica_entrada_existente(
        self, fake_target: Path
    ) -> None:
        gitignore = fake_target / ".gitignore"
        fake_target.mkdir(parents=True)
        gitignore.write_text(".sle/.active-role\n", encoding="utf-8")

        result = run_sh([
            "--components", "hooks",
            "--target-repo", str(fake_target),
        ])
        assert result.returncode == 0
        occurrences = gitignore.read_text(encoding="utf-8").count(".sle/.active-role")
        assert occurrences == 1

    def test_setup_guide_gerado(self, fake_target: Path) -> None:
        result = run_sh([
            "--components", "hooks",
            "--target-repo", str(fake_target),
        ])
        assert result.returncode == 0
        setup = fake_target / "SLE-SETUP.md"
        assert setup.is_file()
        content = setup.read_text(encoding="utf-8")
        assert "{{" not in content
        assert str(fake_target) in content
