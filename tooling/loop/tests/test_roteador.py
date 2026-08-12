"""Tabela de transições — spec: docs/specs/roteador-nucleo.md (C1-C7, C12, C15)."""

from __future__ import annotations

import builtins
import time
from pathlib import Path

from roteador import Acao, Estado, Fase, Motivo, decidir

VERDE = "- **C1** — atendido\n- **C2** — atendido"
UM_NAO_ATENDIDO = "- **C1** — atendido\n- **C2** — não atendido"
UM_NAO_VERIFICAVEL = "- **C1** — atendido\n- **C2** — não verificável"


def test_codificar_concluida_invoca_verificar():
    # spec:C1
    d = decidir(Estado(fase_concluida=Fase.CODIFICAR, spec="alfa"))
    assert d.acao is Acao.INVOCAR
    assert d.fase is Fase.VERIFICAR


def test_veredito_todo_atendido_invoca_homologar():
    # spec:C2
    d = decidir(Estado(fase_concluida=Fase.VERIFICAR, spec="alfa", veredito=VERDE))
    assert d.acao is Acao.INVOCAR
    assert d.fase is Fase.HOMOLOGAR


def test_nao_atendido_abaixo_do_teto_volta_para_codificar():
    # spec:C3
    d = decidir(
        Estado(
            fase_concluida=Fase.VERIFICAR,
            spec="alfa",
            veredito=UM_NAO_ATENDIDO,
            tentativas=1,
            teto=3,
        )
    )
    assert d.acao is Acao.INVOCAR
    assert d.fase is Fase.CODIFICAR
    assert d.tentativa == 2
    assert d.evidencia == ("C2",)


def test_teto_estourado_escala_com_os_vereditos_em_ordem():
    # spec:C4
    vereditos = ("docs/specs/alfa-veredito-1.md", "docs/specs/alfa-veredito-2.md")
    d = decidir(
        Estado(
            fase_concluida=Fase.VERIFICAR,
            spec="alfa",
            veredito=UM_NAO_ATENDIDO,
            tentativas=3,
            teto=3,
            vereditos=vereditos,
        )
    )
    assert d.acao is Acao.ESCALAR
    assert d.motivo is Motivo.TETO_DE_TENTATIVAS
    assert d.evidencia == vereditos


def test_nao_verificavel_tem_precedencia_sobre_nao_atendido():
    # spec:C5 — mesmo com tentativa sobrando e não atendido no mesmo veredito.
    misto = "- **C1** — não atendido\n- **C2** — não verificável"
    d = decidir(
        Estado(
            fase_concluida=Fase.VERIFICAR,
            spec="alfa",
            veredito=misto,
            tentativas=0,
            teto=3,
        )
    )
    assert d.acao is Acao.ESCALAR
    assert d.motivo is Motivo.DEFEITO_DE_SPEC
    assert d.evidencia == ("C2",)


def test_nao_verificavel_tem_precedencia_tambem_sobre_o_teto():
    # spec:C5
    d = decidir(
        Estado(
            fase_concluida=Fase.VERIFICAR,
            spec="alfa",
            veredito=UM_NAO_VERIFICAVEL,
            tentativas=9,
            teto=3,
        )
    )
    assert d.motivo is Motivo.DEFEITO_DE_SPEC


def test_especificar_concluida_para_no_gate_humano():
    # spec:C6
    d = decidir(Estado(fase_concluida=Fase.ESPECIFICAR, spec="alfa"))
    assert d.acao is Acao.ESCALAR
    assert d.motivo is Motivo.GATE_SPEC_APROVADA
    assert d.fase is None


def test_nenhuma_entrada_leva_de_especificar_para_codificar():
    # spec:C6
    for veredito in (None, VERDE, UM_NAO_ATENDIDO, UM_NAO_VERIFICAVEL):
        for tentativas in (0, 1, 99):
            d = decidir(
                Estado(
                    fase_concluida=Fase.ESPECIFICAR,
                    spec="alfa",
                    veredito=veredito,
                    tentativas=tentativas,
                )
            )
            assert d.acao is Acao.ESCALAR
            assert d.fase is not Fase.CODIFICAR


def test_homologar_concluida_para_no_checklist():
    # spec:C7
    d = decidir(Estado(fase_concluida=Fase.HOMOLOGAR, spec="alfa"))
    assert d.acao is Acao.ESCALAR
    assert d.motivo is Motivo.GATE_CHECKLIST


def test_veredito_ausente_ou_ilegivel_escala_nunca_invoca():
    # spec:C12
    for veredito in (None, "", "# Veredito\n\nnada aqui."):
        d = decidir(
            Estado(fase_concluida=Fase.VERIFICAR, spec="alfa", veredito=veredito)
        )
        assert d.acao is Acao.ESCALAR
        assert d.motivo is Motivo.VEREDITO_AUSENTE


def test_decidir_e_determinista():
    # spec:C15
    estado = Estado(
        fase_concluida=Fase.VERIFICAR, spec="alfa", veredito=UM_NAO_ATENDIDO
    )
    assert decidir(estado) == decidir(estado)


def test_decidir_nao_toca_disco_nem_relogio(monkeypatch):
    # spec:C15
    def explode(*args, **kwargs):
        raise AssertionError("decidir tocou disco ou relógio")

    monkeypatch.setattr(builtins, "open", explode)
    monkeypatch.setattr(Path, "open", explode)
    monkeypatch.setattr(time, "time", explode)
    monkeypatch.setattr(time, "monotonic", explode)
    monkeypatch.setattr(time, "perf_counter", explode)

    d = decidir(
        Estado(fase_concluida=Fase.VERIFICAR, spec="alfa", veredito=UM_NAO_ATENDIDO)
    )
    assert d.fase is Fase.CODIFICAR


PROIBIDOS = (
    "import os", "import io", "import time", "import datetime", "import pathlib",
    "import subprocess", "import socket", "import random",
    "from pathlib", "from datetime", "from time", "from os",
)


def test_cadeia_de_decisao_nao_importa_relogio_nem_io():
    # spec:C15 — a pureza é estrutural, e a cadeia inteira responde por ela:
    # sabotar o relógio não pega um import lazy dentro de função.
    import dependencia
    import lote
    import molde
    import roteador
    import secoes
    import veredito

    for modulo in (roteador, veredito, lote, dependencia, secoes, molde):
        fonte = Path(modulo.__file__).read_text(encoding="utf-8")
        for proibido in PROIBIDOS:
            assert proibido not in fonte, (
                f"{Path(modulo.__file__).name} não pode depender de {proibido!r}"
            )
