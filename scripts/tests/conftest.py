"""Fixtures compartilhadas para testes dos scripts de instalação SLE."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SCRIPTS_ROOT.parent


def _find_shell(candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if shutil.which(candidate):
            return candidate
    return None


POWERSHELL_BIN = _find_shell(("pwsh", "powershell"))
BASH_BIN = _find_shell(("bash",))

if BASH_BIN and sys.platform.startswith("win"):
    BASH_BIN = None

INSTALL_PS1 = SCRIPTS_ROOT / "install.ps1"
INSTALL_SH = SCRIPTS_ROOT / "install.sh"


@pytest.fixture()
def fake_target(tmp_path: Path) -> Path:
    """Diretório temporário representando o repositório-alvo."""
    return tmp_path / "target"


def run_ps1(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    if POWERSHELL_BIN is None:
        pytest.skip("PowerShell não disponível no PATH")
    cmd = [POWERSHELL_BIN, "-NoProfile", "-File", str(INSTALL_PS1)] + args
    env = dict(os.environ, LC_ALL="C")
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        cwd=str(cwd) if cwd else None,
        env=env,
    )


def run_sh(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    if BASH_BIN is None:
        pytest.skip("bash não disponível no PATH")
    cmd = [BASH_BIN, str(INSTALL_SH)] + args
    env = dict(os.environ, LC_ALL="C")
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        cwd=str(cwd) if cwd else None,
        env=env,
    )
