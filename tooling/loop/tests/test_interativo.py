"""Sessão interativa e o insumo — spec: docs/specs/loop-pedido-interativo.md."""

from __future__ import annotations

import subprocess
from pathlib import Path

import driver
import git_alvo
import invocacao
from roteador import Acao, Fase
from test_driver import SPEC_LIVRE, ExecutorRoteirizado, _agora
from test_especificar import PEDIDOS, EspecificadorFalso, _alvo, _git


def test_a_sessao_interativa_nao_captura_saida(monkeypatch):
    # spec:Q1 — o driver sai do meio entre você e o agente. Capturar a saída
    # roubaria o terminal da conversa.
    recebidos: dict = {}

    def falso_run(comando, **kwargs):
        recebidos["comando"] = list(comando)
        recebidos["kwargs"] = kwargs

        class Concluido:
            returncode = 0

        return Concluido()

    monkeypatch.setattr(invocacao.subprocess, "run", falso_run)

    codigo, saida = invocacao.executar_interativo(("claude", "oi"), Path("."))

    assert codigo == 0
    assert saida == ""
    for proibido in ("capture_output", "stdout", "stderr", "input", "text"):
        assert proibido not in recebidos["kwargs"], proibido


def test_o_comando_interativo_nao_tem_flag_headless():
    # spec:Q2
    assert "-p" not in invocacao.COMANDO_INTERATIVO_PADRAO
    assert "-p" in invocacao.COMANDO_PADRAO
    assert invocacao.MARCADOR in invocacao.COMANDO_INTERATIVO_PADRAO
    assert driver.Config(alvo=Path("."), specs=()).comando_interativo == (
        invocacao.COMANDO_INTERATIVO_PADRAO
    )


def test_o_comando_interativo_e_configuravel(tmp_path: Path):
    # spec:Q2
    alvo = _alvo(tmp_path)
    executados: list[tuple] = []

    def executor(comando, cwd):
        executados.append(tuple(comando))
        return 1, ""

    driver.rodar_pedidos(
        driver.Config(
            alvo=alvo,
            specs=(),
            pedidos="pedidos.md",
            comando_interativo=("agent", "{prompt}"),
        ),
        executor=executor,
        agora=_agora,
    )

    assert executados and executados[0][0] == "agent"
    assert "-p" not in executados[0]


def test_a_fila_espera_cada_sessao_terminar(tmp_path: Path):
    # spec:Q3 — a spec do pedido anterior já existe quando o próximo começa.
    alvo = _alvo(tmp_path)
    base = EspecificadorFalso(alvo)
    existentes: list[list[str]] = []

    def executor(comando, cwd):
        existentes.append(
            sorted(p.name for p in (alvo / "docs" / "specs").glob("*.md"))
        )
        return base(comando, cwd)

    driver.rodar_pedidos(
        driver.Config(alvo=alvo, specs=(), pedidos="pedidos.md"),
        executor=executor,
        agora=_agora,
    )

    assert existentes == [[], ["cadastro.md"]]


def test_a_spec_continua_sendo_cobrada(tmp_path: Path):
    # spec:Q4
    alvo = _alvo(tmp_path)

    relato = driver.rodar_pedidos(
        driver.Config(alvo=alvo, specs=(), pedidos="pedidos.md"),
        executor=lambda comando, cwd: (0, ""),
        agora=_agora,
    )

    assert relato.final.decisao.acao is Acao.ESCALAR


def test_o_segmento_dois_continua_headless(tmp_path: Path):
    # spec:Q5
    pasta = tmp_path / "alvo2"
    (pasta / "docs" / "specs").mkdir(parents=True)
    (pasta / "docs" / "specs" / "alfa.md").write_text(
        SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."), encoding="utf-8"
    )
    _git(pasta, "init", "-q", "-b", "trabalho")
    _git(pasta, "config", "user.email", "loop@teste")
    _git(pasta, "config", "user.name", "loop")
    _git(pasta, "add", "-A")
    _git(pasta, "commit", "-q", "-m", "inicial")

    executados: list[tuple] = []
    roteirizado = ExecutorRoteirizado(pasta)

    def executor(comando, cwd):
        executados.append(tuple(comando))
        return roteirizado(comando, cwd)

    driver.rodar(
        driver.Config(alvo=pasta, specs=("alfa",)), executor=executor, agora=_agora
    )

    assert executados
    assert all("-p" in comando for comando in executados)


def test_pedidos_nao_conta_como_sujeira(tmp_path: Path):
    # spec:Q6 — o loop se bloqueava por causa do próprio insumo.
    alvo = _alvo(tmp_path)
    assert git_alvo.impedimentos(alvo) == ()

    (alvo / "pedidos.md").write_text(PEDIDOS + "\n## outro\n\nmais um\n", encoding="utf-8")
    assert git_alvo.impedimentos(alvo) == ()


def test_nome_parecido_com_pedidos_ainda_e_sujeira(tmp_path: Path):
    # spec:Q6 — a exceção é o caminho exato, não o prefixo.
    alvo = _alvo(tmp_path)
    (alvo / "pedidos-antigos.md").write_text("rascunho meu\n", encoding="utf-8")

    assert any("pedidos-antigos.md" in i for i in git_alvo.impedimentos(alvo))


def test_pedidos_vira_commit_proprio_antes_da_fila(tmp_path: Path):
    # spec:Q7
    alvo = _alvo(tmp_path, versionar_pedidos=False)
    assert "pedidos.md" not in _git(alvo, "ls-files")

    driver.rodar_pedidos(
        driver.Config(alvo=alvo, specs=(), pedidos="pedidos.md"),
        executor=EspecificadorFalso(alvo),
        agora=_agora,
    )

    assuntos = _git(alvo, "log", "--grep=^SLE-Loop:", "--format=%s").splitlines()
    assert assuntos[-1] == "loop(pedidos): registrar pedidos"
    primeiro = _git(alvo, "log", "--grep=^SLE-Loop:", "--format=%H").splitlines()[-1]
    assert _git(alvo, "show", "--name-only", "--format=", primeiro).split() == [
        "pedidos.md"
    ]
    assert "SLE-Loop: pedidos#registro" in _git(alvo, "show", "-s", "--format=%b", primeiro)


def test_pedidos_ja_versionado_nao_gera_commit(tmp_path: Path):
    # spec:Q8
    alvo = _alvo(tmp_path)
    antes = _git(alvo, "rev-list", "--count", "HEAD")

    driver.rodar_pedidos(
        driver.Config(alvo=alvo, specs=(), pedidos="pedidos.md"),
        executor=EspecificadorFalso(alvo),
        agora=_agora,
    )

    assuntos = _git(alvo, "log", "--grep=^SLE-Loop:", "--format=%s").splitlines()
    assert "loop(pedidos): registrar pedidos" not in assuntos
    assert int(_git(alvo, "rev-list", "--count", "HEAD")) == int(antes) + 2


def test_modo_seco_nao_abre_sessao_nem_commita(tmp_path: Path):
    # spec:Q9
    alvo = _alvo(tmp_path, versionar_pedidos=False)
    executor = EspecificadorFalso(alvo)
    antes = _git(alvo, "rev-list", "--count", "HEAD")

    driver.rodar_pedidos(
        driver.Config(alvo=alvo, specs=(), pedidos="pedidos.md", seco=True),
        executor=executor,
        agora=_agora,
    )

    assert executor.chamadas == []
    assert _git(alvo, "rev-list", "--count", "HEAD") == antes
    assert "pedidos.md" not in _git(alvo, "ls-files")
