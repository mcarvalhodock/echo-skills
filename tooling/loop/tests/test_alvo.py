"""Forma do alvo — spec: docs/specs/loop-alvo.md (T1-T9)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import driver
import git_alvo
import registro
from roteador import Acao, Fase, Motivo
from test_driver import SPEC_LIVRE, ExecutorRoteirizado, _agora, _config


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()


def _specs_em(pasta: Path, *nomes: str) -> None:
    (pasta / "docs" / "specs").mkdir(parents=True)
    for nome in nomes:
        (pasta / "docs" / "specs" / f"{nome}.md").write_text(
            SPEC_LIVRE.format(nome=nome, depende="Nenhuma."), encoding="utf-8"
        )


def _monorepo(raiz: Path) -> Path:
    repo = raiz / "mono"
    for pacote in ("api", "web"):
        _specs_em(repo / "packages" / pacote, "alfa")
    _git_init(repo)
    return repo


def _git_init(repo: Path) -> None:
    _git(repo, "init", "-q", "-b", "trabalho")
    _git(repo, "config", "user.email", "loop@teste")
    _git(repo, "config", "user.name", "loop")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "inicial")


def _sem_git(raiz: Path) -> Path:
    pasta = raiz / "solta"
    _specs_em(pasta, "alfa")
    return pasta


def test_alvo_inexistente_escala_nomeando_o_caminho(tmp_path: Path):
    # spec:T1
    ausente = tmp_path / "nao-existe"
    relato = driver.rodar(
        _config(ausente, "alfa"), executor=ExecutorRoteirizado(ausente), agora=_agora
    )
    assert relato.final.decisao.acao is Acao.ESCALAR
    assert "nao-existe" in relato.texto


def test_pasta_sem_git_roda_em_modo_degradado_e_avisa_uma_vez(tmp_path: Path):
    # spec:T2
    alvo = _sem_git(tmp_path)
    executor = ExecutorRoteirizado(alvo)

    relato = driver.rodar(_config(alvo, "alfa"), executor=executor, agora=_agora)

    assert executor.chamadas, "modo degradado não é modo parado"
    assert relato.final.decisao.fase is Fase.HOMOLOGAR
    assert relato.texto.lower().count("degradado") == 1
    assert "commit" in relato.texto and "diff" in relato.texto


def test_modo_degradado_so_sonda_o_git_e_nao_opera(tmp_path: Path, monkeypatch):
    # spec:T3 — a sondagem é o que estabelece o modo; depois dela, nada.
    alvo = _sem_git(tmp_path)
    chamadas: list[tuple] = []
    original = git_alvo._git

    def espiao(onde, *args, **kwargs):
        chamadas.append(args)
        return original(onde, *args, **kwargs)

    monkeypatch.setattr(git_alvo, "_git", espiao)

    relato = driver.rodar(
        _config(alvo, "alfa"), executor=ExecutorRoteirizado(alvo), agora=_agora
    )

    assert relato.final.decisao.fase is Fase.HOMOLOGAR
    assert chamadas == [("rev-parse", "--show-toplevel")]


def test_modo_degradado_pede_estado_atual_e_nao_passa_ref_base(tmp_path: Path):
    # spec:T4
    alvo = _sem_git(tmp_path)
    executor = ExecutorRoteirizado(alvo)

    driver.rodar(_config(alvo, "alfa"), executor=executor, agora=_agora)

    # Pelo início da frase, não por substring: o caminho temporário do pytest
    # carrega o nome do teste, e "verificar" apareceria dentro dele.
    verificacoes = [p for p in executor.chamadas if p.startswith("Use a skill verificar")]
    assert verificacoes
    for prompt in verificacoes:
        assert "estado atual" in prompt
        assert "Ref base" not in prompt


def test_sujeira_fora_da_subarvore_nao_impede(tmp_path: Path):
    # spec:T5 — num monorepo real a árvore quase nunca está inteiramente limpa.
    repo = _monorepo(tmp_path)
    (repo / "packages" / "web" / "app.js").write_text("de outro time\n", encoding="utf-8")

    alvo = repo / "packages" / "api"
    assert git_alvo.impedimentos(alvo) == ()

    relato = driver.rodar(
        _config(alvo, "alfa"), executor=ExecutorRoteirizado(alvo), agora=_agora
    )
    assert relato.final.decisao.fase is Fase.HOMOLOGAR


def test_sujeira_dentro_da_subarvore_ainda_impede(tmp_path: Path):
    # spec:T5
    repo = _monorepo(tmp_path)
    alvo = repo / "packages" / "api"
    (alvo / "solto.py").write_text("x = 1\n", encoding="utf-8")

    assert any("solto.py" in i for i in git_alvo.impedimentos(alvo))


def test_alvo_na_raiz_mantem_o_comportamento_de_hoje(tmp_path: Path):
    # spec:T6
    repo = tmp_path / "simples"
    _specs_em(repo, "alfa")
    _git_init(repo)

    assert git_alvo.subarvore(repo) == "."
    (repo / "solto.py").write_text("x = 1\n", encoding="utf-8")
    assert any("solto.py" in i for i in git_alvo.impedimentos(repo))


def test_subarvore_e_o_caminho_relativo_a_raiz(tmp_path: Path):
    # spec:T7
    repo = _monorepo(tmp_path)
    assert git_alvo.subarvore(repo / "packages" / "api") == "packages/api"


def test_subarvore_sobrevive_a_caminho_com_acento(tmp_path: Path):
    # spec:T7 — o git fala UTF-8; decodificar com a codepage do Windows fazia
    # `fusível/` voltar como `fus?vel/` e o caminho deixar de casar com o disco.
    repo = tmp_path / "raiz"
    pacote = repo / "pacotes" / "cobrança"
    _specs_em(pacote, "alfa")
    _git_init(repo)

    assert git_alvo.raiz(pacote) == repo.resolve()
    assert git_alvo.subarvore(pacote) == "pacotes/cobrança"

    (pacote / "código.py").write_text("x = 1\n", encoding="utf-8")
    assert any("código.py" in i for i in git_alvo.impedimentos(pacote))


def test_prompt_de_verificar_limita_o_diff_a_subarvore(tmp_path: Path):
    # spec:T7
    repo = _monorepo(tmp_path)
    alvo = repo / "packages" / "api"
    executor = ExecutorRoteirizado(alvo)

    driver.rodar(_config(alvo, "alfa"), executor=executor, agora=_agora)

    # Pelo início da frase, não por substring: o caminho temporário do pytest
    # carrega o nome do teste, e "verificar" apareceria dentro dele.
    verificacoes = [p for p in executor.chamadas if p.startswith("Use a skill verificar")]
    assert verificacoes
    for prompt in verificacoes:
        assert "packages/api" in prompt


def test_commit_recolhe_so_a_subarvore(tmp_path: Path):
    # spec:T8
    repo = _monorepo(tmp_path)
    alvo = repo / "packages" / "api"
    (repo / "packages" / "web" / "app.js").write_text("de outro time\n", encoding="utf-8")

    driver.rodar(_config(alvo, "alfa"), executor=ExecutorRoteirizado(alvo), agora=_agora)

    tocados = _git(repo, "show", "--name-only", "--format=", "HEAD").split()
    assert tocados
    assert all(caminho.startswith("packages/api/") for caminho in tocados), tocados


def test_mudanca_ja_staged_fora_da_subarvore_nao_entra_no_commit(tmp_path: Path):
    # spec:T8 — o vão entre T5 e T8: a guarda só olha a subárvore, então não vê
    # o que outro time deixou no índice; se o commit gravar o índice inteiro,
    # o trabalho dele entra num commit rotulado `loop(...)`.
    repo = _monorepo(tmp_path)
    alvo = repo / "packages" / "api"
    (repo / "packages" / "web" / "app.js").write_text("de outro time\n", encoding="utf-8")
    _git(repo, "add", "packages/web/app.js")

    assert git_alvo.impedimentos(alvo) == ()

    driver.rodar(_config(alvo, "alfa"), executor=ExecutorRoteirizado(alvo), agora=_agora)

    tocados = _git(repo, "show", "--name-only", "--format=", "HEAD").split()
    assert not any(c.startswith("packages/web/") for c in tocados), tocados


def test_subarvores_irmas_nao_interferem(tmp_path: Path):
    # spec:T9
    repo = _monorepo(tmp_path)
    api, web = repo / "packages" / "api", repo / "packages" / "web"

    driver.rodar(_config(api, "alfa"), executor=ExecutorRoteirizado(api), agora=_agora)

    assert registro.caminho_do_registro(api).exists()
    assert not registro.caminho_do_registro(web).exists()
    tocados = _git(repo, "show", "--name-only", "--format=", "HEAD").split()
    assert not any(caminho.startswith("packages/web/") for caminho in tocados)


@pytest.mark.parametrize("tem_git", [True, False])
def test_deteccao_de_repositorio(tmp_path: Path, tem_git: bool):
    # spec:T2
    pasta = tmp_path / ("com" if tem_git else "sem")
    _specs_em(pasta, "alfa")
    if tem_git:
        _git_init(pasta)
    assert git_alvo.e_repositorio(pasta) is tem_git
