"""Trocar de agente na sessão — spec: docs/specs/sle-ferramenta.md (W1-W10)."""

from __future__ import annotations

from pathlib import Path

import pytest

import console
import driver
import invocacao
import repos
from lote import DecisaoDoLote
from roteador import Acao, Decisao, Motivo

CURSOR_HEADLESS = ("agent", "-p", "{prompt}")


@pytest.fixture
def casa_com_repo(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SLE_CASA", str(tmp_path / "casa"))
    projeto = tmp_path / "projeto"
    (projeto / "docs" / "specs").mkdir(parents=True)
    repos.gravar(f"- api: {projeto}\n")
    return projeto


def _sessao(*linhas: str, **kwargs):
    escrito: list[str] = []
    entrada = iter(linhas)
    codigo = console.rodar(
        ler=lambda _p: next(entrada), escrever=escrito.append, **kwargs
    )
    return codigo, "\n".join(escrito)


def _relato() -> driver.Relato:
    return driver.Relato(
        DecisaoDoLote(Decisao(Acao.ESCALAR, Motivo.GATE_CHECKLIST)), 0, ""
    )


def _espiar_rodar(monkeypatch) -> list[tuple]:
    vistos: list[tuple] = []
    monkeypatch.setattr(
        driver, "rodar", lambda c, **k: vistos.append(c.comando) or _relato()
    )
    return vistos


def test_abertura_define_os_comandos_da_sessao(casa_com_repo, monkeypatch):
    # spec:W1
    vistos = _espiar_rodar(monkeypatch)

    _sessao(
        "usar api",
        "rodar --specs alfa",
        "sair",
        comando=CURSOR_HEADLESS,
    )

    assert vistos == [CURSOR_HEADLESS]


def test_o_subcomando_console_repassa_os_comandos(casa_com_repo, monkeypatch):
    # spec:W1
    recebidos: dict = {}
    monkeypatch.setattr(console, "rodar", lambda **k: recebidos.update(k) or 0)

    driver.main(["console", "--comando", "agent -p {prompt}"])

    assert recebidos["comando"] == CURSOR_HEADLESS


def test_sem_argumento_a_sessao_abre_com_o_default(casa_com_repo, monkeypatch):
    # spec:W2 — o G2 da loop-agente continua valendo, sem emenda.
    vistos = _espiar_rodar(monkeypatch)

    _sessao("usar api", "rodar --specs alfa", "sair")

    assert vistos == [invocacao.COMANDO_PADRAO]


def test_ferramenta_sem_argumento_mostra_os_dois(casa_com_repo):
    # spec:W3
    _, saida = _sessao("ferramenta", "sair")

    assert "claude -p {prompt}" in saida
    assert "claude {prompt}" in saida


def test_troca_por_template_vale_nas_invocacoes_seguintes(casa_com_repo, monkeypatch):
    # spec:W4
    vistos = _espiar_rodar(monkeypatch)

    _sessao(
        "usar api",
        "rodar --specs alfa",
        "ferramenta --comando 'agent -p {prompt}'",
        "rodar --specs beta",
        "sair",
    )

    assert vistos == [invocacao.COMANDO_PADRAO, CURSOR_HEADLESS]


def test_template_sem_marcador_e_recusado_e_a_sessao_segue(casa_com_repo, monkeypatch):
    # spec:W5 — nunca fica sem comando.
    vistos = _espiar_rodar(monkeypatch)

    _, saida = _sessao(
        "usar api",
        "ferramenta --comando 'agent -p'",
        "rodar --specs alfa",
        "sair",
    )

    assert invocacao.MARCADOR in saida
    assert vistos == [invocacao.COMANDO_PADRAO]


def test_nome_troca_os_dois_de_uma_vez(casa_com_repo, monkeypatch):
    # spec:W9 — a mesma economia de `usar <apelido>`.
    vistos = _espiar_rodar(monkeypatch)

    _, saida = _sessao("usar api", "ferramenta cursor", "rodar --specs alfa", "sair")

    assert vistos == [CURSOR_HEADLESS]

    _, depois = _sessao("ferramenta cursor", "ferramenta", "sair")
    assert "agent -p {prompt}" in depois
    assert "agent {prompt}" in depois


def test_nome_desconhecido_lista_os_que_existem(casa_com_repo, monkeypatch):
    # spec:W10
    vistos = _espiar_rodar(monkeypatch)

    _, saida = _sessao(
        "usar api", "ferramenta cursos", "rodar --specs alfa", "sair"
    )

    assert "cursos" in saida
    assert "claude" in saida and "cursor" in saida
    assert vistos == [invocacao.COMANDO_PADRAO]


def test_comando_na_linha_sobrepoe_o_da_sessao(casa_com_repo, monkeypatch):
    # spec:W6
    vistos = _espiar_rodar(monkeypatch)

    _sessao(
        "usar api",
        "ferramenta cursor",
        "rodar --specs alfa --comando 'outro -p {prompt}'",
        "sair",
    )

    assert vistos == [("outro", "-p", "{prompt}")]


def test_depois_da_chamada_a_sessao_volta_ao_dela(casa_com_repo, monkeypatch):
    # spec:W7
    vistos = _espiar_rodar(monkeypatch)

    _sessao(
        "usar api",
        "ferramenta cursor",
        "rodar --specs alfa --comando 'outro -p {prompt}'",
        "rodar --specs beta",
        "sair",
    )

    assert vistos == [("outro", "-p", "{prompt}"), CURSOR_HEADLESS]


def test_a_troca_nao_sobrevive_a_sessao(casa_com_repo, monkeypatch):
    # spec:W8
    _sessao("ferramenta cursor", "sair")

    vistos = _espiar_rodar(monkeypatch)
    _sessao("usar api", "rodar --specs alfa", "sair")

    assert vistos == [invocacao.COMANDO_PADRAO]


def _conteudo(raiz: Path) -> dict:
    """Caminho e conteúdo: só o nome não pega alteração, que é metade do W8."""
    return {
        p.relative_to(raiz).as_posix(): p.read_bytes()
        for p in raiz.rglob("*")
        if p.is_file()
    }


def test_a_troca_nao_escreve_nem_altera_arquivo_nenhum(casa_com_repo):
    # spec:W8 — "criado ou alterado": comparar só nome pegaria a criação e
    # deixaria a alteração passar.
    casa = repos.caminho_do_cadastro().parent
    antes_casa, antes_alvo = _conteudo(casa), _conteudo(casa_com_repo)

    _sessao("ferramenta cursor", "ferramenta --comando 'x {prompt}'", "sair")

    assert _conteudo(casa) == antes_casa
    assert _conteudo(casa_com_repo) == antes_alvo


def test_o_interativo_tambem_e_configuravel_na_abertura(casa_com_repo, monkeypatch):
    # spec:W1 — o ramo interativo, que só era observado de relance.
    vistos: list[tuple] = []
    monkeypatch.setattr(
        driver,
        "rodar_pedidos",
        lambda c, **k: vistos.append(c.comando_interativo) or _relato(),
    )

    _sessao("usar api", "pedir", "sair", comando_interativo=("agent", "{prompt}"))

    assert vistos == [("agent", "{prompt}")]


def test_o_interativo_tambem_troca_no_meio_da_sessao(casa_com_repo, monkeypatch):
    # spec:W4
    vistos: list[tuple] = []
    monkeypatch.setattr(
        driver,
        "rodar_pedidos",
        lambda c, **k: vistos.append(c.comando_interativo) or _relato(),
    )

    _sessao(
        "usar api",
        "pedir",
        "ferramenta --interativo 'agent {prompt}'",
        "pedir",
        "sair",
    )

    assert vistos == [invocacao.COMANDO_INTERATIVO_PADRAO, ("agent", "{prompt}")]
