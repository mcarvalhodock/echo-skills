"""Registro de decisões — spec: docs/specs/roteador-nucleo.md (C13, C14)."""

from __future__ import annotations

import json

import pytest

from registro import CAMPOS, caminho_do_registro, contar_tentativas, registrar
from roteador import Acao, Decisao, Fase, Motivo

INVOCA_CODIFICAR = Decisao(
    acao=Acao.INVOCAR,
    motivo=Motivo.TRANSICAO,
    fase=Fase.CODIFICAR,
    tentativa=1,
    evidencia=("C2",),
)
INVOCA_VERIFICAR = Decisao(
    acao=Acao.INVOCAR, motivo=Motivo.TRANSICAO, fase=Fase.VERIFICAR
)


def _linhas(caminho):
    return [json.loads(l) for l in caminho.read_text(encoding="utf-8").splitlines() if l]


def test_registra_uma_linha_com_campos_fixos(tmp_path):
    # spec:C13
    caminho = tmp_path / "loop.jsonl"
    registrar(
        caminho,
        decisao=INVOCA_CODIFICAR,
        instante="2026-08-12T09:00:00",
        alvo="/repos/alfa",
        spec="alfa",
    )

    linhas = _linhas(caminho)
    assert len(linhas) == 1
    assert tuple(linhas[0]) == CAMPOS
    assert linhas[0]["transicao"] == "invocar:codificar"
    assert linhas[0]["motivo"] == "transicao"
    assert linhas[0]["evidencia"] == ["C2"]
    assert linhas[0]["tentativa"] == 1
    assert linhas[0]["alvo"] == "/repos/alfa"


def test_append_nao_reescreve_linha_anterior(tmp_path):
    # spec:C13
    caminho = tmp_path / "loop.jsonl"
    registrar(caminho, decisao=INVOCA_CODIFICAR, instante="t1", alvo="/a", spec="alfa")
    primeira = caminho.read_text(encoding="utf-8")

    registrar(caminho, decisao=INVOCA_VERIFICAR, instante="t2", alvo="/a", spec="alfa")

    assert caminho.read_text(encoding="utf-8").startswith(primeira)
    assert len(_linhas(caminho)) == 2


def test_registro_recusa_campo_de_texto_livre(tmp_path):
    # spec:C13
    caminho = tmp_path / "loop.jsonl"
    with pytest.raises(TypeError):
        registrar(
            caminho,
            decisao=INVOCA_CODIFICAR,
            instante="t1",
            alvo="/a",
            spec="alfa",
            observacao="o executor achou o critério confuso",
        )


def test_conta_tentativas_de_codificar_por_spec(tmp_path):
    # spec:C14
    caminho = tmp_path / "loop.jsonl"
    registrar(caminho, decisao=INVOCA_CODIFICAR, instante="t1", alvo="/a", spec="alfa")
    registrar(caminho, decisao=INVOCA_VERIFICAR, instante="t2", alvo="/a", spec="alfa")
    registrar(caminho, decisao=INVOCA_CODIFICAR, instante="t3", alvo="/a", spec="alfa")
    registrar(caminho, decisao=INVOCA_CODIFICAR, instante="t4", alvo="/a", spec="beta")

    assert contar_tentativas(caminho, "alfa") == 2
    assert contar_tentativas(caminho, "beta") == 1
    assert contar_tentativas(caminho, "gama") == 0


def test_registro_inexistente_conta_zero(tmp_path):
    # spec:C14
    assert contar_tentativas(tmp_path / "nao-existe.jsonl", "alfa") == 0


def test_registro_mora_dentro_do_alvo(tmp_path):
    # spec:C13 — todo caminho é relativo ao alvo, nunca ao método.
    assert caminho_do_registro(tmp_path) == tmp_path / ".sle" / "loop.jsonl"
