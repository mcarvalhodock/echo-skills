"""Resolução de bash usada pelos testes do install.sh."""

from __future__ import annotations

import subprocess
from pathlib import Path

import _helpers


class TestBashAoLadoDoGit:
    def test_deriva_do_git_em_prefixo_nao_padrao(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """Fallback derivado, não fixado: um git fora de C:\\Program Files.

        Imita um Scoop/Chocolatey/portátil, e a profundidade real do Git for
        Windows, onde o executável mora em `mingw64/bin/`.
        """
        raiz = tmp_path / "ferramentas" / "Git"
        (raiz / "mingw64" / "bin").mkdir(parents=True)
        (raiz / "bin").mkdir()
        git = raiz / "mingw64" / "bin" / "git.exe"
        git.write_text("", encoding="utf-8")
        bash = raiz / "bin" / "bash.exe"
        bash.write_text("", encoding="utf-8")

        monkeypatch.setattr(_helpers.shutil, "which", lambda _: str(git))

        assert str(bash) in _helpers._bash_ao_lado_do_git()

    def test_sem_git_no_path_devolve_lista_vazia(self, monkeypatch) -> None:
        """Sem âncora não há derivação — e isso não é exceção."""
        monkeypatch.setattr(_helpers.shutil, "which", lambda _: None)

        assert _helpers._bash_ao_lado_do_git() == []


class TestFindWorkingBash:
    def test_descarta_candidato_que_nao_executa(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """A8 — quem não responde à sondagem é descartado, e a busca segue.

        Imita o bash do WSL: está no PATH, é encontrado por `which`, e falha ao
        ser executado. Era ele que a versão anterior devolvia no Windows.
        """
        quebrado = tmp_path / "bash-quebrado"
        quebrado.write_text("", encoding="utf-8")
        monkeypatch.setattr(_helpers.shutil, "which", lambda _: str(quebrado))

        def sonda_falha(*args, **kwargs):
            raise OSError("execvpe /bin/bash failed")

        monkeypatch.setattr(_helpers.subprocess, "run", sonda_falha)

        assert _helpers._find_working_bash() is None

    def test_aceita_candidato_que_responde(self, tmp_path: Path, monkeypatch) -> None:
        """A8 — o candidato que executa e responde a sondagem é aceito."""
        bom = tmp_path / "bash-bom"
        bom.write_text("", encoding="utf-8")
        monkeypatch.setattr(_helpers.shutil, "which", lambda _: str(bom))

        def sonda_ok(*args, **kwargs):
            return subprocess.CompletedProcess(args, 0, "sle-ok\n", "")

        monkeypatch.setattr(_helpers.subprocess, "run", sonda_ok)

        assert _helpers._find_working_bash() == str(bom)
