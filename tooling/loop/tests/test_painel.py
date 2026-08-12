"""O painel — spec: docs/specs/sle-painel.md (V1-V12)."""

from __future__ import annotations

from pathlib import Path

import pytest

import driver
import painel
import registro
import repos
from roteador import Acao, Decisao, Fase, Motivo

INVOCA_CODIFICAR = Decisao(Acao.INVOCAR, Motivo.TRANSICAO, fase=Fase.CODIFICAR)
INVOCA_HOMOLOGAR = Decisao(Acao.INVOCAR, Motivo.TRANSICAO, fase=Fase.HOMOLOGAR)


@pytest.fixture
def casa_limpa(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SLE_CASA", str(tmp_path / "casa"))
    return tmp_path


def _alvo(raiz: Path, nome: str, *decisoes, spec: str = "alfa") -> Path:
    pasta = raiz / nome
    (pasta / "docs" / "specs").mkdir(parents=True)
    caminho = registro.caminho_do_registro(pasta)
    for decisao in decisoes:
        registro.registrar(
            caminho, decisao=decisao, instante="t", alvo=str(pasta), spec=spec
        )
    return pasta


def test_registro_ausente_e_nao_comecou(casa_limpa):
    # spec:V4 — não começou, ocioso e pronto são três coisas diferentes.
    alvo = _alvo(casa_limpa, "novo")

    estado = painel.estado_de(alvo)

    assert "não começou" in estado.rotulo
    assert "ocioso" not in estado.rotulo and "pronto" not in estado.rotulo


def test_gate_de_spec_aprovada_pede_aprovacao_do_lote(casa_limpa):
    # spec:V5
    alvo = _alvo(
        casa_limpa, "a", Decisao(Acao.ESCALAR, Motivo.GATE_SPEC_APROVADA)
    )
    assert "aprovação do lote" in painel.estado_de(alvo).rotulo


def test_gate_de_checklist_pede_checklist(casa_limpa):
    # spec:V6
    alvo = _alvo(casa_limpa, "b", Decisao(Acao.ESCALAR, Motivo.GATE_CHECKLIST))
    assert "checklist" in painel.estado_de(alvo).rotulo


def test_outra_escalada_e_travado_e_nomeia_o_motivo(casa_limpa):
    # spec:V7
    alvo = _alvo(
        casa_limpa, "c", Decisao(Acao.ESCALAR, Motivo.TETO_DE_TENTATIVAS)
    )

    estado = painel.estado_de(alvo)

    assert "travado" in estado.rotulo
    assert "teto-de-tentativas" in estado.detalhe


def test_linha_nao_terminal_e_em_andamento_com_fase_e_spec(casa_limpa):
    # spec:V8
    alvo = _alvo(casa_limpa, "d", INVOCA_CODIFICAR, spec="cobranca")

    estado = painel.estado_de(alvo)

    assert "em andamento" in estado.rotulo
    assert "codificar" in estado.detalhe and "cobranca" in estado.detalhe


def test_pronto_nunca_e_afirmado(casa_limpa):
    # spec:V6 — ninguém verificou; "aguarda checklist" é o mais longe honesto.
    alvo = _alvo(casa_limpa, "e", INVOCA_HOMOLOGAR)
    assert "pronto" not in painel.estado_de(alvo).rotulo


def test_caminho_inacessivel_e_reportado_como_tal(casa_limpa):
    # spec:V11
    estado = painel.estado_de(casa_limpa / "nunca-existiu")
    assert "inacessível" in estado.rotulo


def test_o_painel_lista_todos_os_cadastrados(casa_limpa, capsys):
    # spec:V1
    a = _alvo(casa_limpa, "um", Decisao(Acao.ESCALAR, Motivo.GATE_CHECKLIST))
    b = _alvo(casa_limpa, "dois", INVOCA_CODIFICAR)
    repos.gravar(f"- um: {a}\n- dois: {b}\n")

    assert driver.main(["painel"]) == 0
    saida = capsys.readouterr().out

    assert "um" in saida and "dois" in saida
    assert "checklist" in saida and "em andamento" in saida


def test_um_inacessivel_nao_impede_os_outros(casa_limpa, capsys):
    # spec:V11
    a = _alvo(casa_limpa, "vivo", Decisao(Acao.ESCALAR, Motivo.GATE_CHECKLIST))
    repos.gravar(f"- vivo: {a}\n- morto: {casa_limpa / 'sumiu'}\n")

    assert driver.main(["painel"]) == 0
    saida = capsys.readouterr().out

    assert "vivo" in saida and "checklist" in saida
    assert "morto" in saida and "inacessível" in saida


def test_alvo_mostra_so_aquele(casa_limpa, capsys):
    # spec:V2
    a = _alvo(casa_limpa, "um", Decisao(Acao.ESCALAR, Motivo.GATE_CHECKLIST))
    b = _alvo(casa_limpa, "dois", INVOCA_CODIFICAR)
    repos.gravar(f"- um: {a}\n- dois: {b}\n")

    driver.main(["painel", "--alvo", "um"])
    saida = capsys.readouterr().out

    assert "um" in saida
    assert "dois" not in saida


def test_sai_com_zero_mesmo_com_travado(casa_limpa):
    # spec:V3 — o painel relata, não julga.
    a = _alvo(casa_limpa, "travado", Decisao(Acao.ESCALAR, Motivo.FUSIVEL))
    repos.gravar(f"- travado: {a}\n")

    assert driver.main(["painel"]) == 0


def test_o_painel_nao_escreve_nada_no_alvo(casa_limpa, capsys):
    # spec:V9 + V10
    a = _alvo(casa_limpa, "um", INVOCA_CODIFICAR)
    repos.gravar(f"- um: {a}\n")
    antes = {
        p.relative_to(a).as_posix(): p.stat().st_mtime_ns
        for p in a.rglob("*")
        if p.is_file()
    }

    driver.main(["painel"])

    depois = {
        p.relative_to(a).as_posix(): p.stat().st_mtime_ns
        for p in a.rglob("*")
        if p.is_file()
    }
    assert depois == antes


def test_o_painel_nao_invoca_agente(casa_limpa, monkeypatch):
    # spec:V10
    a = _alvo(casa_limpa, "um", INVOCA_CODIFICAR)
    repos.gravar(f"- um: {a}\n")

    def explode(*args, **kwargs):
        raise AssertionError("o painel invocou agente")

    monkeypatch.setattr(driver, "invocar", explode)

    assert driver.main(["painel"]) == 0


def test_o_painel_le_com_ciclo_em_andamento_sem_esperar(casa_limpa):
    # spec:V12 — somente-leitura por desenho, não por omissão.
    a = _alvo(casa_limpa, "um", INVOCA_CODIFICAR)
    conteudo = registro.caminho_do_registro(a).read_bytes()

    estado = painel.estado_de(a)

    assert "em andamento" in estado.rotulo
    assert registro.caminho_do_registro(a).read_bytes() == conteudo


def test_le_com_a_ultima_linha_sendo_escrita(casa_limpa):
    # spec:V12 — o cenário real de "ciclo em andamento noutro terminal": o
    # arquivo é append-only e a última linha pode estar pela metade.
    alvo = _alvo(casa_limpa, "um", INVOCA_CODIFICAR, spec="cobranca")
    with registro.caminho_do_registro(alvo).open("a", encoding="utf-8") as arquivo:
        arquivo.write('{"instante": "t", "alvo"')

    estado = painel.estado_de(alvo)

    assert "em andamento" in estado.rotulo
    assert "cobranca" in estado.detalhe


def test_alvo_aceita_caminho_alem_de_apelido(casa_limpa, capsys):
    # spec:V2 — a metade "ou caminho" do critério.
    a = _alvo(casa_limpa, "solto", Decisao(Acao.ESCALAR, Motivo.GATE_CHECKLIST))

    assert driver.main(["painel", "--alvo", str(a)]) == 0

    assert "checklist" in capsys.readouterr().out


def test_nao_ha_armazenamento_proprio_de_estado(casa_limpa):
    # spec:V9 — a casa guarda dado autorado, e só.
    a = _alvo(casa_limpa, "um", INVOCA_CODIFICAR)
    repos.gravar(f"- um: {a}\n")

    driver.main(["painel"])

    assert sorted(p.name for p in (casa_limpa / "casa").rglob("*")) == ["repos.md"]
