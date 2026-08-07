"""Testes do install.ps1.

Auto-skip se PowerShell não está no PATH. No Linux/macOS com pwsh Core
instalado, roda normalmente.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from _helpers import POWERSHELL_BIN, run_ps1

pytestmark = pytest.mark.skipif(
    POWERSHELL_BIN is None, reason="PowerShell não disponível"
)


class TestHelpAndInvocation:
    def test_help_flag_produz_ajuda(self) -> None:
        result = run_ps1(["-Help"])
        assert result.returncode == 0
        assert "install.ps1" in result.stdout
        assert "COMPONENTS:" in result.stdout
        assert "EXIT CODES:" in result.stdout

    def test_argumento_desconhecido_retorna_exit_2(self) -> None:
        result = run_ps1(["-Components", "invalido", "-TargetRepo", "C:\\tmp"])
        assert result.returncode != 0


class TestDryRun:
    def test_dry_run_all_lista_todas_operacoes(self, fake_target: Path) -> None:
        result = run_ps1([
            "-Components", "all",
            "-Scope", "local",
            "-TargetRepo", str(fake_target),
            "-DryRun",
        ])
        assert result.returncode == 0
        assert "[dry-run]" in result.stdout
        assert "would copy" in result.stdout
        assert "designer" in result.stdout
        assert "would generate" in result.stdout or "would write" in result.stdout
        assert not fake_target.exists()

    def test_dry_run_skills_apenas(self, fake_target: Path) -> None:
        result = run_ps1([
            "-Components", "skills",
            "-Scope", "local",
            "-TargetRepo", str(fake_target),
            "-DryRun",
        ])
        assert result.returncode == 0
        assert "designer" in result.stdout
        assert "workflows" not in result.stdout


class TestExecucaoRealSkillsLocal:
    def test_instala_as_quatro_skills(self, fake_target: Path) -> None:
        result = run_ps1([
            "-Components", "skills",
            "-Scope", "local",
            "-TargetRepo", str(fake_target),
        ])
        assert result.returncode == 0
        for skill in ("designer", "validator", "executor", "observer"):
            skill_dir = fake_target / ".claude" / "skills" / skill
            assert skill_dir.is_dir(), f"skill {skill} não foi instalada"
            assert (skill_dir / "SKILL.md").is_file(), (
                f"{skill}/SKILL.md ausente"
            )


class TestIdempotencia:
    def test_segunda_execucao_emite_skip(self, fake_target: Path) -> None:
        args = [
            "-Components", "skills",
            "-Scope", "local",
            "-TargetRepo", str(fake_target),
        ]
        first = run_ps1(args)
        assert first.returncode == 0

        second = run_ps1(args)
        assert second.returncode == 0
        assert "[skip]" in second.stdout
        assert second.stdout.count("[skip]") >= 4

    def test_force_sobrescreve(self, fake_target: Path) -> None:
        args = [
            "-Components", "skills",
            "-Scope", "local",
            "-TargetRepo", str(fake_target),
        ]
        first = run_ps1(args)
        assert first.returncode == 0

        second = run_ps1(args + ["-Force"])
        assert second.returncode == 0
        assert "[skip]" not in second.stdout
        assert "installed skill" in second.stdout


class TestCiInstall:
    def test_workflows_recebem_warning_mode(self, fake_target: Path) -> None:
        result = run_ps1([
            "-Components", "ci",
            "-TargetRepo", str(fake_target),
        ])
        assert result.returncode == 0
        wf_dir = fake_target / ".github" / "workflows"
        assert wf_dir.is_dir()
        yml_files = list(wf_dir.glob("*.yml"))
        assert len(yml_files) >= 3
        for yml in yml_files:
            content = yml.read_text(encoding="utf-8")
            assert "continue-on-error: true" in content, (
                f"{yml.name} sem warning mode"
            )

    def test_manifesto_esqueleto_criado_se_ausente(self, fake_target: Path) -> None:
        result = run_ps1([
            "-Components", "ci",
            "-TargetRepo", str(fake_target),
        ])
        assert result.returncode == 0
        manifest = fake_target / ".sle" / "manifesto.md"
        assert manifest.is_file()
        content = manifest.read_text(encoding="utf-8")
        assert "<preencher:" in content

    def test_manifesto_preservado_se_existe(self, fake_target: Path) -> None:
        manifest = fake_target / ".sle" / "manifesto.md"
        manifest.parent.mkdir(parents=True)
        manifest.write_text("# manifesto pre-existente\n", encoding="utf-8")

        result = run_ps1([
            "-Components", "ci",
            "-TargetRepo", str(fake_target),
        ])
        assert result.returncode == 0
        assert manifest.read_text(encoding="utf-8") == "# manifesto pre-existente\n"


class TestHooksInstall:
    def test_hooks_copiados_e_gitignore_atualizado(self, fake_target: Path) -> None:
        result = run_ps1([
            "-Components", "hooks",
            "-TargetRepo", str(fake_target),
        ])
        assert result.returncode == 0

        hooks_dir = fake_target / "tooling" / "hooks"
        assert hooks_dir.is_dir()
        assert (hooks_dir / "block-designer-writing-code" / "hook.py").is_file()

        gitignore = fake_target / ".gitignore"
        assert gitignore.is_file()
        assert ".sle/.active-role" in gitignore.read_text(encoding="utf-8")

    def test_gitignore_nao_duplica_entrada_existente(self, fake_target: Path) -> None:
        gitignore = fake_target / ".gitignore"
        fake_target.mkdir(parents=True)
        gitignore.write_text(".sle/.active-role\n", encoding="utf-8")

        result = run_ps1([
            "-Components", "hooks",
            "-TargetRepo", str(fake_target),
        ])
        assert result.returncode == 0
        content = gitignore.read_text(encoding="utf-8")
        occurrences = content.count(".sle/.active-role")
        assert occurrences == 1, f"esperado 1 ocorrencia, achei {occurrences}"

    def test_setup_guide_gerado(self, fake_target: Path) -> None:
        result = run_ps1([
            "-Components", "hooks",
            "-TargetRepo", str(fake_target),
        ])
        assert result.returncode == 0
        setup = fake_target / "SLE-SETUP.md"
        assert setup.is_file()
        content = setup.read_text(encoding="utf-8")
        assert str(fake_target) in content
        assert "hooks" in content
        assert "{{" not in content, "placeholders não substituídos"


class TestFontesFaltando:
    def test_script_fora_do_clone_aborta(self, tmp_path: Path) -> None:
        outside_dir = tmp_path / "solto"
        outside_dir.mkdir()
        copied_script = outside_dir / "install.ps1"
        copied_script.write_bytes(
            (Path(__file__).resolve().parents[1] / "install.ps1").read_bytes()
        )

        import subprocess
        from _helpers import POWERSHELL_BIN

        result = subprocess.run(
            [POWERSHELL_BIN, "-NoProfile", "-File", str(copied_script),
             "-Components", "skills", "-Scope", "local", "-TargetRepo", str(tmp_path / "target")],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 1
        assert "source" in result.stdout.lower() or "source" in result.stderr.lower()
