"""Decide a próxima transição do ciclo SLE a partir do estado observável.

Puro por contrato: não lê disco, relógio, rede nem API de harness. É essa
pureza que permite trocar o driver (Claude Code hoje, outro amanhã) sem
tocar na regra — e que torna a tabela de transições testável de verdade.

O roteador é agnóstico ao conteúdo: ele lê a classificação do veredito,
nunca o código. Julgar implementação é de `verificar`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from veredito import Classificacao, classificar

TETO_PADRAO = 3


class Fase(Enum):
    ESPECIFICAR = "especificar"
    CODIFICAR = "codificar"
    VERIFICAR = "verificar"
    HOMOLOGAR = "homologar"


class Acao(Enum):
    INVOCAR = "invocar"
    ESCALAR = "escalar"


class Motivo(Enum):
    TRANSICAO = "transicao"
    GATE_SPEC_APROVADA = "gate-spec-aprovada"
    GATE_CHECKLIST = "gate-checklist"
    DEFEITO_DE_SPEC = "defeito-de-spec"
    TETO_DE_TENTATIVAS = "teto-de-tentativas"
    VEREDITO_AUSENTE = "veredito-ausente"


@dataclass(frozen=True)
class Estado:
    fase_concluida: Fase
    spec: str
    veredito: str | None = None
    tentativas: int = 0
    teto: int = TETO_PADRAO
    vereditos: tuple[str, ...] = ()


@dataclass(frozen=True)
class Decisao:
    acao: Acao
    motivo: Motivo
    fase: Fase | None = None
    tentativa: int = 0
    evidencia: tuple[str, ...] = ()


def decidir(estado: Estado) -> Decisao:
    if estado.fase_concluida is Fase.ESPECIFICAR:
        return Decisao(Acao.ESCALAR, Motivo.GATE_SPEC_APROVADA)
    if estado.fase_concluida is Fase.HOMOLOGAR:
        return Decisao(Acao.ESCALAR, Motivo.GATE_CHECKLIST)
    if estado.fase_concluida is Fase.CODIFICAR:
        return Decisao(Acao.INVOCAR, Motivo.TRANSICAO, fase=Fase.VERIFICAR)
    return _decidir_apos_verificar(estado)


def _decidir_apos_verificar(estado: Estado) -> Decisao:
    classificados = classificar(estado.veredito)
    if not classificados:
        return Decisao(Acao.ESCALAR, Motivo.VEREDITO_AUSENTE)

    nao_verificaveis = _com_classificacao(classificados, Classificacao.NAO_VERIFICAVEL)
    if nao_verificaveis:
        # Precedência deliberada sobre o não atendido e sobre o teto: outra
        # volta de `codificar` queima tentativa contra critério que ninguém
        # consegue medir. Isso é defeito de spec, e quem conserta é o humano.
        return Decisao(
            Acao.ESCALAR, Motivo.DEFEITO_DE_SPEC, evidencia=nao_verificaveis
        )

    nao_atendidos = _com_classificacao(classificados, Classificacao.NAO_ATENDIDO)
    if not nao_atendidos:
        return Decisao(Acao.INVOCAR, Motivo.TRANSICAO, fase=Fase.HOMOLOGAR)

    if estado.tentativas >= estado.teto:
        return Decisao(
            Acao.ESCALAR, Motivo.TETO_DE_TENTATIVAS, evidencia=estado.vereditos
        )

    return Decisao(
        Acao.INVOCAR,
        Motivo.TRANSICAO,
        fase=Fase.CODIFICAR,
        tentativa=estado.tentativas + 1,
        evidencia=nao_atendidos,
    )


def _com_classificacao(
    classificados: dict[str, Classificacao], procurada: Classificacao
) -> tuple[str, ...]:
    return tuple(
        identificador
        for identificador, classificacao in classificados.items()
        if classificacao is procurada
    )
