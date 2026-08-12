"""Lê o arquivo de pedidos: um `##` por demanda, e o cabeçalho É o nome da spec.

Sem slugificação, de propósito. Derivar `cadastro-de-clientes` de
`## Cadastro de Clientes` produziria arquivo com nome que ninguém esperava — e
o driver precisa saber o caminho do artefato **antes** de invocar, para poder
cobrar a existência dele depois. Cabeçalho que não serve como nome é recusado,
nunca corrigido.

Puro: recebe texto, devolve dados.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

NOME_VALIDO = re.compile(r"^[a-z0-9-]+$")

_CABECALHO = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Pedido:
    nome: str
    texto: str


@dataclass(frozen=True)
class Leitura:
    pedidos: tuple[Pedido, ...]
    invalidos: tuple[str, ...]


def ler(texto: str) -> Leitura:
    """Os pedidos na ordem do arquivo, mais os cabeçalhos que não servem de nome."""
    if not texto:
        return Leitura((), ())

    cabecalhos = list(_CABECALHO.finditer(texto))
    aceitos: list[Pedido] = []
    recusados: list[str] = []

    for indice, cabecalho in enumerate(cabecalhos):
        titulo = cabecalho.group(1).strip()
        # O corpo vai até o próximo cabeçalho — ou até o fim, no último. O que
        # vem ANTES do primeiro não é pedido de ninguém e fica de fora.
        fim = (
            cabecalhos[indice + 1].start()
            if indice + 1 < len(cabecalhos)
            else len(texto)
        )
        corpo = texto[cabecalho.end() : fim].strip()

        if NOME_VALIDO.match(titulo):
            aceitos.append(Pedido(nome=titulo, texto=corpo))
        else:
            recusados.append(titulo)

    return Leitura(tuple(aceitos), tuple(recusados))
