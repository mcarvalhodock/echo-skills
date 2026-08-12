"""O console — spec: docs/specs/sle-console.md (N1-N13)."""

from __future__ import annotations

from pathlib import Path

import pytest

import console
import driver
import repos
from lote import DecisaoDoLote
from roteador import Acao, Decisao, Motivo


@pytest.fixture
def casa_com_repo(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SLE_CASA", str(tmp_path / "casa"))
    projeto = tmp_path / "projeto"
    (projeto / "docs" / "specs").mkdir(parents=True)
    repos.gravar(f"- api: {projeto}\n")
    return projeto


def _sessao(*linhas: str):
    """Roda o console com entrada roteirizada e devolve o que ele escreveu."""
    escrito: list[str] = []
    entrada = iter(linhas)

    def ler(_prompt: str) -> str:
        return next(entrada)

    codigo = console.rodar(ler=ler, escrever=escrito.append)
    return codigo, "\n".join(escrito)


def _relato() -> driver.Relato:
    return driver.Relato(
        DecisaoDoLote(Decisao(Acao.ESCALAR, Motivo.GATE_CHECKLIST)), 0, "feito"
    )


def test_sair_encerra_com_zero(casa_com_repo):
    # spec:N3
    codigo, _ = _sessao("sair")
    assert codigo == 0


def test_fim_de_entrada_encerra_com_zero(casa_com_repo):
    # spec:N3 — Ctrl-D.
    codigo, _ = _sessao()
    assert codigo == 0


def test_o_prompt_mostra_o_selecionado_ou_a_ausencia(casa_com_repo):
    # spec:N4
    prompts: list[str] = []
    entrada = iter(["usar api", "sair"])

    def ler(prompt: str) -> str:
        prompts.append(prompt)
        return next(entrada)

    console.rodar(ler=ler, escrever=lambda _: None)

    assert "nenhum" in prompts[0].lower()
    assert "api" in prompts[1]


def test_usar_seleciona_e_apelido_desconhecido_nao_derruba(casa_com_repo):
    # spec:N5
    codigo, saida = _sessao("usar fantasma", "usar api", "sair")

    assert codigo == 0
    assert "fantasma" in saida


def test_com_selecionado_os_comandos_nao_exigem_alvo(casa_com_repo, monkeypatch):
    # spec:N6
    vistos: list[Path] = []
    monkeypatch.setattr(
        driver, "rodar", lambda c, **k: vistos.append(c.alvo) or _relato()
    )

    _sessao("usar api", "rodar --specs alfa", "sair")

    assert vistos == [casa_com_repo]


def test_sem_selecionado_os_comandos_recusam(casa_com_repo, monkeypatch):
    # spec:N7 — nunca escolhem um por conta.
    chamados: list[str] = []
    monkeypatch.setattr(driver, "rodar", lambda c, **k: chamados.append("rodou"))

    _, saida = _sessao("rodar --specs alfa", "sair")

    assert chamados == []
    assert "selecion" in saida.lower()


def test_tarefas_e_o_painel_do_selecionado(casa_com_repo, capsys):
    # spec:N8 — a saída do comando vai para a saída do programa; o escritor da
    # sessão é para as mensagens do console.
    _sessao("usar api", "tarefas", "sair")

    assert "não começou" in capsys.readouterr().out


def test_comando_desconhecido_nao_derruba(casa_com_repo):
    # spec:N9
    codigo, saida = _sessao("inventado", "sair")

    assert codigo == 0
    assert "inventado" in saida


def test_erro_dentro_de_um_comando_nao_derruba(casa_com_repo, monkeypatch, capsys):
    # spec:N10 — nada além de `sair` e do fim de entrada encerra.
    def explode(*args, **kwargs):
        raise RuntimeError("estourou por dentro")

    monkeypatch.setattr(driver, "rodar", explode)

    codigo, saida = _sessao("usar api", "rodar --specs alfa", "tarefas", "sair")

    assert codigo == 0
    assert "estourou por dentro" in saida
    # o comando seguinte rodou: a sessão sobreviveu ao estouro
    assert "não começou" in capsys.readouterr().out


def test_linha_com_aspas_abertas_nao_derruba(casa_com_repo):
    # spec:N10 — a quebra em palavras também é parte do comando, e aspas não
    # fechadas levantam ValueError antes de qualquer despacho.
    codigo, saida = _sessao('usar "api', "sair")

    assert codigo == 0
    assert "ValueError" in saida


def test_interrupcao_cancela_a_linha_e_nao_a_sessao(casa_com_repo, monkeypatch):
    # spec:N10 — KeyboardInterrupt não é Exception e escapava do tratamento.
    def interrompe(*args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(driver, "rodar", interrompe)

    codigo, _ = _sessao("usar api", "rodar --specs alfa", "sair")

    assert codigo == 0


def test_interrupcao_no_prompt_tambem_nao_derruba(casa_com_repo):
    # spec:N10 — tratar só a do despacho deixa a promessa pela metade.
    respostas = iter(["sair"])

    def ler(_prompt: str) -> str:
        if not hasattr(ler, "interrompeu"):
            ler.interrompeu = True
            raise KeyboardInterrupt
        return next(respostas)

    assert console.rodar(ler=ler, escrever=lambda _: None) == 0


def test_pedir_tambem_usa_o_selecionado(casa_com_repo, monkeypatch):
    # spec:N6 — mesmo ramo de `rodar`, e sem teste até agora.
    vistos: list[Path] = []
    monkeypatch.setattr(
        driver, "rodar_pedidos", lambda c, **k: vistos.append(c.alvo) or _relato()
    )

    _sessao("usar api", "pedir", "sair")

    assert vistos == [casa_com_repo]


def test_a_sessao_espera_o_comando_terminar(casa_com_repo, monkeypatch):
    # spec:N11 — o falsificador é a re-entrância: se a chamada fosse solta em
    # paralelo, a leitura da próxima linha aconteceria com o comando em voo.
    em_execucao: list[bool] = [False]

    def demorado(config, **kwargs):
        em_execucao[0] = True
        try:
            return _relato()
        finally:
            em_execucao[0] = False

    monkeypatch.setattr(driver, "rodar", demorado)
    entrada = iter(["usar api", "rodar --specs alfa", "sair"])

    def ler(_prompt: str) -> str:
        assert not em_execucao[0], "leu a próxima linha com o comando em voo"
        return next(entrada)

    assert console.rodar(ler=ler, escrever=lambda _: None) == 0


def test_o_console_usa_as_mesmas_funcoes_do_subcomando(casa_com_repo, monkeypatch, capsys):
    # spec:N12 — substituir `driver.rodar` muda o console também.
    monkeypatch.setattr(
        driver, "rodar", lambda c, **k: driver.Relato(_relato().final, 0, "SUBSTITUIDO")
    )

    _sessao("usar api", "rodar --specs alfa", "sair")

    assert "SUBSTITUIDO" in capsys.readouterr().out


def test_a_selecao_nao_sobrevive_a_sessao(casa_com_repo, monkeypatch):
    # spec:N13
    _sessao("usar api", "sair")

    chamados: list[str] = []
    monkeypatch.setattr(driver, "rodar", lambda c, **k: chamados.append("rodou"))
    _, saida = _sessao("rodar --specs alfa", "sair")

    assert chamados == []
    assert "selecion" in saida.lower()
    assert sorted(p.name for p in (repos.caminho_do_cadastro().parent).rglob("*")) == [
        "repos.md"
    ]


def test_repo_e_painel_funcionam_de_dentro(casa_com_repo, capsys):
    # spec:N8
    _sessao("repo list", "painel", "sair")

    assert "api" in capsys.readouterr().out


def test_sle_puro_abre_o_console_em_terminal(casa_com_repo, monkeypatch):
    # spec:N2
    monkeypatch.setattr(console, "e_terminal", lambda: True)
    monkeypatch.setattr(console, "rodar", lambda **k: 0)

    assert driver.main([]) == 0


def test_sle_puro_sem_terminal_mantem_ajuda_e_saida_dois(casa_com_repo, monkeypatch):
    # spec:N2 — o que o S3 protegia continua protegido: script não tem terminal.
    monkeypatch.setattr(console, "e_terminal", lambda: False)

    with pytest.raises(SystemExit) as saida:
        driver.main([])

    assert saida.value.code == 2


def test_o_subcomando_console_entra_no_modo_interativo(casa_com_repo, monkeypatch):
    # spec:N1
    entrou: list[bool] = []
    monkeypatch.setattr(console, "rodar", lambda **k: entrou.append(True) or 0)

    assert driver.main(["console"]) == 0
    assert entrou == [True]


def test_e_terminal_exige_as_duas_pontas(monkeypatch):
    # spec:N2 — só uma delas mente em ambiente de CI.
    class Falso:
        def __init__(self, tty: bool):
            self._tty = tty

        def isatty(self) -> bool:
            return self._tty

    monkeypatch.setattr(console.sys, "stdin", Falso(True))
    monkeypatch.setattr(console.sys, "stdout", Falso(False))
    assert console.e_terminal() is False

    monkeypatch.setattr(console.sys, "stdout", Falso(True))
    assert console.e_terminal() is True
