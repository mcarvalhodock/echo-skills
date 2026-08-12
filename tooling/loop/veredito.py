"""Classifica, por critério, o veredito produzido pela leitura limpa.

O molde de `verificar` é contrato: uma linha por critério, abrindo com
`- **<ID>** — <classificação>`. Este parser lê a classificação no **início**
do texto após o travessão e ignora todo o resto.

A versão anterior varria a linha inteira procurando as palavras. Custou seis
falsos `não verificável` no primeiro veredito real que ela leu, porque
justificativa cita identificador de critério o tempo todo — e classificava
`parcialmente atendido` como atendido, que é o erro na direção perigosa.
"""

from __future__ import annotations

import re
import unicodedata
from enum import Enum


class Classificacao(Enum):
    ATENDIDO = "atendido"
    NAO_ATENDIDO = "nao atendido"
    NAO_VERIFICAVEL = "nao verificavel"


# Do mais específico para o mais genérico: "atendido" é prefixo de nada, mas
# é sufixo de "nao atendido", e testar na ordem errada inverte o veredito.
_PREFIXOS = (
    ("nao verificavel", Classificacao.NAO_VERIFICAVEL),
    ("nao atendido", Classificacao.NAO_ATENDIDO),
    ("atendido", Classificacao.ATENDIDO),
)

# Entrada ambígua nunca pode ser lida como atendido: um parser que erra para
# o lado bom reconstrói o falso "está pronto" que o método existe para pegar.
_SEVERIDADE = {
    Classificacao.ATENDIDO: 0,
    Classificacao.NAO_ATENDIDO: 1,
    Classificacao.NAO_VERIFICAVEL: 2,
}

_LINHA_DO_MOLDE = re.compile(
    r"^\s*[-*+]\s+\*{0,2}([A-Z]\d{1,3})\*{0,2}\s*[—–:-]\s*(.+)$"
)

# Depois da classificação só pode vir pontuação — "atendido." e "atendido, com
# ressalva" são a classificação mais a justificativa; "atendido em parte" é
# outra coisa, e reconhecer o prefixo ali seria ler ressalva como aprovação.
_TERMINADOR = re.compile(r"^\s*[^\w\s]")


def _sem_acento(texto: str) -> str:
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def _classificacao(apos_o_travessao: str) -> Classificacao:
    limpo = _sem_acento(apos_o_travessao).replace("*", "").replace("`", "")
    limpo = limpo.strip().lower()
    for prefixo, classificacao in _PREFIXOS:
        if not limpo.startswith(prefixo):
            continue
        resto = limpo[len(prefixo) :]
        if resto == "" or _TERMINADOR.match(resto):
            return classificacao
        return Classificacao.NAO_VERIFICAVEL
    return Classificacao.NAO_VERIFICAVEL


def classificar(texto: str | None) -> dict[str, Classificacao]:
    """Devolve {identificador: classificação}. Vazio quando não há linha no molde."""
    if not texto:
        return {}

    classificados: dict[str, Classificacao] = {}
    for linha in texto.splitlines():
        no_molde = _LINHA_DO_MOLDE.match(linha)
        if no_molde is None:
            continue
        identificador, resto = no_molde.group(1), no_molde.group(2)
        classificacao = _classificacao(resto)
        anterior = classificados.get(identificador)
        if anterior is None or _SEVERIDADE[classificacao] > _SEVERIDADE[anterior]:
            classificados[identificador] = classificacao
    return classificados
