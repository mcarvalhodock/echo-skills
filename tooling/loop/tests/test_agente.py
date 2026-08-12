"""Agente e skills instaladas — spec: docs/specs/loop-agente.md (G1-G11)."""

from __future__ import annotations

from pathlib import Path

import pytest

import driver
import invocacao
import registro
import skills_instaladas
from roteador import Acao, Fase, Motivo
from test_alvo import _git_init, _specs_em
from test_driver import ExecutorRoteirizado, _agora, _config

CURSOR = ("cursor-agent", "-p", "{prompt}")
PROMPT_NA_FRENTE = ("agente", "{prompt}", "--headless")


def _alvo_git(raiz: Path, nome: str = "alvo") -> Path:
    pasta = raiz / nome
    _specs_em(pasta, "alfa")
    _git_init(pasta)
    return pasta


def _transicoes(alvo: Path) -> list[str]:
    return [l["transicao"] for l in registro.linhas(registro.caminho_do_registro(alvo))]


def test_o_comando_e_configuravel(tmp_path: Path):
    # spec:G1
    assert invocacao.comando_de("oi", CURSOR) == ("cursor-agent", "-p", "oi")


def test_sem_configuracao_o_comando_e_o_claude(tmp_path: Path):
    # spec:G2
    assert invocacao.comando_de("oi") == ("claude", "-p", "oi")
    assert invocacao.COMANDO_PADRAO[0] == "claude"


def test_o_prompt_pode_vir_antes_de_outras_flags():
    # spec:G3 — a posição é declarada pelo marcador, não presumida no fim.
    assert invocacao.comando_de("oi", PROMPT_NA_FRENTE) == ("agente", "oi", "--headless")


def test_template_sem_marcador_e_recusado_antes_de_invocar(tmp_path: Path):
    # spec:G4
    alvo = _alvo_git(tmp_path)
    executor = ExecutorRoteirizado(alvo)

    relato = driver.rodar(
        _config(alvo, "alfa", comando=("claude", "-p")),
        executor=executor,
        agora=_agora,
    )

    assert relato.final.decisao.acao is Acao.ESCALAR
    assert executor.chamadas == []
    assert "{prompt}" in relato.texto


def test_executavel_ausente_e_detectado():
    # spec:G5
    assert invocacao.executavel_ausente(CURSOR + ()) in (None, "cursor-agent")
    assert invocacao.executavel_ausente(("nao-existe-mesmo", "{prompt}")) == (
        "nao-existe-mesmo"
    )
    assert invocacao.executavel_ausente(invocacao.COMANDO_PADRAO) is None


def test_executavel_ausente_escala_antes_de_gerar_processo(tmp_path: Path):
    # spec:G5 — `executor=None` é o caminho real; a escalada acontece antes de
    # qualquer processo nascer, então o teste não gera nenhum.
    alvo = _alvo_git(tmp_path)

    relato = driver.rodar(
        _config(alvo, "alfa", comando=("agente-que-nao-existe", "-p", "{prompt}")),
        executor=None,
        agora=_agora,
    )

    assert relato.final.decisao.acao is Acao.ESCALAR
    assert relato.final.decisao.motivo is Motivo.GUARDA_DO_ALVO
    assert "agente-que-nao-existe" in relato.texto
    assert relato.invocacoes == 0


def test_skill_divergente_avisa_e_a_execucao_continua(tmp_path: Path):
    # spec:G6 — divergência é informação, não impedimento.
    alvo = _alvo_git(tmp_path)
    metodo = tmp_path / "metodo"
    instaladas = tmp_path / "casa" / ".claude" / "skills"
    for nome in skills_instaladas.SKILLS:
        (metodo / nome).mkdir(parents=True)
        (metodo / nome / "SKILL.md").write_text(f"# {nome} novo\n", encoding="utf-8")
        (instaladas / nome).mkdir(parents=True)
        (instaladas / nome / "SKILL.md").write_text(f"# {nome} novo\n", encoding="utf-8")
    (instaladas / "codificar" / "SKILL.md").write_text("# antigo\n", encoding="utf-8")

    avisos = skills_instaladas.divergencias(alvo, metodo=metodo, global_=instaladas)

    assert len(avisos) == 1
    assert "codificar" in avisos[0]

    executor = ExecutorRoteirizado(alvo)
    relato = driver.rodar(_config(alvo, "alfa"), executor=executor, agora=_agora)
    assert executor.chamadas, "aviso não trava"
    assert relato.final.decisao.fase is Fase.HOMOLOGAR


def test_skill_ausente_e_avisada_como_ausencia(tmp_path: Path):
    # spec:G7
    alvo = _alvo_git(tmp_path)
    metodo = tmp_path / "metodo"
    instaladas = tmp_path / "casa" / ".claude" / "skills"
    for nome in skills_instaladas.SKILLS:
        (metodo / nome).mkdir(parents=True)
        (metodo / nome / "SKILL.md").write_text(f"# {nome}\n", encoding="utf-8")
    instaladas.mkdir(parents=True)

    avisos = skills_instaladas.divergencias(alvo, metodo=metodo, global_=instaladas)

    assert len(avisos) == len(skills_instaladas.SKILLS)
    assert all("ausente" in a for a in avisos)
    assert not any("difere" in a for a in avisos)


def test_escopo_local_tem_precedencia_sobre_o_global(tmp_path: Path):
    # spec:G8 — é a local que o agente vai usar.
    alvo = _alvo_git(tmp_path)
    metodo = tmp_path / "metodo"
    instaladas = tmp_path / "casa" / ".claude" / "skills"
    for nome in skills_instaladas.SKILLS:
        (metodo / nome).mkdir(parents=True)
        (metodo / nome / "SKILL.md").write_text(f"# {nome}\n", encoding="utf-8")
        (instaladas / nome).mkdir(parents=True)
        (instaladas / nome / "SKILL.md").write_text("# global divergente\n", encoding="utf-8")

    local = alvo / ".claude" / "skills"
    for nome in skills_instaladas.SKILLS:
        (local / nome).mkdir(parents=True)
        (local / nome / "SKILL.md").write_text(f"# {nome}\n", encoding="utf-8")

    assert skills_instaladas.divergencias(alvo, metodo=metodo, global_=instaladas) == ()


def test_o_prompt_cita_a_skill_e_passa_os_insumos(tmp_path: Path):
    # spec:G9
    alvo = _alvo_git(tmp_path)
    executor = ExecutorRoteirizado(alvo)

    driver.rodar(_config(alvo, "alfa"), executor=executor, agora=_agora)

    codificacoes = [p for p in executor.chamadas if p.startswith("Use a skill codificar")]
    verificacoes = [p for p in executor.chamadas if p.startswith("Use a skill verificar")]
    assert codificacoes and verificacoes
    assert "docs/specs/alfa.md" in codificacoes[0] and str(alvo) in codificacoes[0]
    assert "Ref base" in verificacoes[0]


def test_o_prompt_nao_carrega_o_corpo_da_spec_nem_do_veredito(tmp_path: Path):
    # spec:G10 — quem lê os arquivos é a fase, dentro da sessão dela.
    alvo = _alvo_git(tmp_path)
    marca = "TEXTO-QUE-SO-EXISTE-DENTRO-DA-SPEC"
    spec = alvo / "docs" / "specs" / "alfa.md"
    spec.write_text(spec.read_text(encoding="utf-8") + f"\n{marca}\n", encoding="utf-8")
    _git = __import__("subprocess").run
    _git(["git", "add", "-A"], cwd=alvo, check=True)
    _git(["git", "commit", "-q", "-m", "spec"], cwd=alvo, check=True)

    executor = ExecutorRoteirizado(alvo)
    driver.rodar(_config(alvo, "alfa"), executor=executor, agora=_agora)

    assert executor.chamadas
    assert all(marca not in prompt for prompt in executor.chamadas)
    assert all("atendido" not in prompt for prompt in executor.chamadas)


def test_trocar_o_comando_nao_muda_a_sequencia_de_decisoes(tmp_path: Path):
    # spec:G11
    sequencias = []
    for nome, comando in (("a", invocacao.COMANDO_PADRAO), ("b", CURSOR)):
        alvo = _alvo_git(tmp_path, nome)
        driver.rodar(
            _config(alvo, "alfa", comando=comando),
            executor=ExecutorRoteirizado(alvo),
            agora=_agora,
        )
        sequencias.append(_transicoes(alvo))

    assert sequencias[0] == sequencias[1]
    assert sequencias[0]


def test_o_comando_configurado_chega_ao_executor(tmp_path: Path):
    # spec:G1
    alvo = _alvo_git(tmp_path)
    executados: list[tuple] = []

    def executor(comando, cwd):
        executados.append(tuple(comando))
        return 1, ""

    driver.rodar(_config(alvo, "alfa", comando=CURSOR), executor=executor, agora=_agora)

    assert executados
    assert executados[0][0] == "cursor-agent"
