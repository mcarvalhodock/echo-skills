"""Onde o `sle` guarda o que é dele.

A casa guarda **dado autorado** — o que você escreveu: quais repositórios
existem, com que apelido. O estado de trabalho continua vivendo no alvo, em
`.sle/loop.jsonl`, nas specs e nos vereditos. Guardar cópia dele aqui seria
criar uma segunda verdade, e é assim que uma ferramenta passa a mentir com
confiança.

A fronteira vale nos dois sentidos: nada da casa é escrito num alvo, e nada de
alvo é escrito na casa.
"""

from __future__ import annotations

import os
from pathlib import Path

VARIAVEL = "SLE_CASA"


def caminho() -> Path:
    """`~/.sle/`, ou o que `SLE_CASA` disser.

    A variável existe para separar ambientes — e para a suíte não tocar a casa
    real de quem roda os testes.
    """
    declarada = os.environ.get(VARIAVEL)
    return Path(declarada) if declarada else Path.home() / ".sle"


def garantir() -> tuple[Path, bool]:
    """Devolve a casa e se ela acabou de nascer.

    Quem chama informa a criação **uma vez**: avisar a cada execução treina a
    pessoa a ignorar o aviso.
    """
    destino = caminho()
    if destino.is_dir():
        return destino, False

    destino.mkdir(parents=True, exist_ok=True)
    return destino, True
