"""Helpers compartilhados para testes dos scripts de instalação SLE.

Separado de conftest.py para evitar colisão de namespace com outros
conftest.py do repositório (pytest unifica módulos com o mesmo nome).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SCRIPTS_ROOT.parent


def _find_shell(candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if shutil.which(candidate):
            return candidate
    return None


def _bash_ao_lado_do_git() -> list[str]:
    """Bash que acompanha a instalação do git, derivado — nunca fixado.

    Endereço fixo (`C:\\Program Files\\Git\\...`) só vale para a instalação
    padrão do Git for Windows: quebra em Scoop, Chocolatey, git portátil ou
    outro drive. E quebraria em silêncio, porque este ramo só é alcançado
    quando o `which` já falhou — a suíte voltaria a pular testes dizendo "bash
    não disponível", que é o defeito que este repositório acabou de quitar.

    O git está no PATH em qualquer máquina que use este repositório, então ele
    é a âncora. Subir pelos pais, e não por índice fixo, porque a profundidade
    varia: no Git for Windows o executável mora em `mingw64/bin/git.exe`.
    """
    git = shutil.which("git")
    if not git:
        return []
    achados: list[str] = []
    for pai in Path(git).resolve().parents:
        for relativo in ("bin/bash.exe", "usr/bin/bash.exe", "bin/bash"):
            candidato = pai / relativo
            if candidato.exists():
                achados.append(str(candidato))
        if achados:
            break
    return achados


def _find_working_bash() -> str | None:
    """Primeiro bash do PATH que de fato executa.

    Estar no PATH não é executar: no Windows, `bash` costuma resolver para o
    atalho do WSL, que existe e falha com "execvpe /bin/bash failed". A versão
    anterior contornava descartando bash inteiro no win32 — e o descarte dizia
    "bash não disponível", escondendo por um ciclo um defeito do install.sh que
    reprovava em qualquer sistema. Aqui o candidato é testado, não presumido.
    """
    candidatos = [shutil.which("bash")] + _bash_ao_lado_do_git()
    for candidato in candidatos:
        if not candidato:
            continue
        try:
            sonda = subprocess.run(
                [candidato, "-c", "echo sle-ok"],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if sonda.returncode == 0 and "sle-ok" in sonda.stdout:
            return candidato
    return None


POWERSHELL_BIN = _find_shell(("pwsh", "powershell"))
BASH_BIN = _find_working_bash()

INSTALL_PS1 = SCRIPTS_ROOT / "install.ps1"
INSTALL_SH = SCRIPTS_ROOT / "install.sh"


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


def run_sh(
    args: list[str],
    cwd: Path | None = None,
    prefixo_de_path: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    if BASH_BIN is None:
        pytest.skip("bash não disponível no PATH")
    cmd = [BASH_BIN, str(INSTALL_SH)] + args
    env = dict(os.environ, LC_ALL="C")
    if prefixo_de_path is not None:
        env["PATH"] = f"{prefixo_de_path}{os.pathsep}{env.get('PATH', '')}"
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        cwd=str(cwd) if cwd else None,
        env=env,
    )
