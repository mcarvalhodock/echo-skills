"""Executa uma fase num processo novo e devolve um resultado de máquina.

A regra que dá forma ao módulo: **o texto de retorno da fase nunca decide
nada.** Ele é guardado e mais nada. Duas rodadas seguidas de leitura limpa
escreveram o veredito no arquivo, como mandado, e devolveram um resumo dele no
canal de retorno — a regra "ninguém resume o veredito" foi cumprida no disco e
furada no retorno. Aqui o que decide é exit code e existência de artefato.

Impuro por definição: chama processo.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from roteador import Fase

EXECUTAVEL = "claude"


@dataclass(frozen=True)
class Resultado:
    fase: Fase
    exit_code: int
    saida: str
    artefato_esperado: str | None
    artefato_presente: bool

    @property
    def ok(self) -> bool:
        if self.exit_code != 0:
            return False
        return self.artefato_esperado is None or self.artefato_presente


def comando_de(prompt: str) -> tuple[str, ...]:
    """Headless, uma fase por processo, sem nenhuma retomada de sessão.

    Retomar sessão traria o raciocínio da fase anterior junto — que é
    exatamente o que a sessão limpa existe para cortar, e o motivo de
    retentativa também começar do zero.
    """
    return (EXECUTAVEL, "-p", prompt)


def executar_de_verdade(comando, cwd) -> tuple[int, str]:
    concluido = subprocess.run(
        list(comando), cwd=str(cwd), capture_output=True, text=True
    )
    return concluido.returncode, (concluido.stdout or "") + (concluido.stderr or "")


def invocar(
    fase: Fase,
    prompt: str,
    *,
    alvo: Path | str,
    artefato_esperado: str | None = None,
    executor=None,
) -> Resultado:
    executar = executor or executar_de_verdade
    exit_code, saida = executar(comando_de(prompt), Path(alvo))

    presente = bool(artefato_esperado) and (Path(alvo) / artefato_esperado).exists()

    return Resultado(
        fase=fase,
        exit_code=exit_code,
        saida=saida,
        artefato_esperado=artefato_esperado,
        artefato_presente=presente,
    )
