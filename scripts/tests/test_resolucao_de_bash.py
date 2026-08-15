"""Resolução de bash usada pelos testes do install.sh."""

from __future__ import annotations

import subprocess
from pathlib import Path

import _helpers


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
