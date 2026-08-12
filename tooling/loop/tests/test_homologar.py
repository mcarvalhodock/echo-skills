"""O ciclo vai até o fim — spec: docs/specs/loop-cli.md (S8-S12)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import driver
import registro
from roteador import Acao, Fase, Motivo
from test_alvo import _git_init, _specs_em
from test_driver import ExecutorRoteirizado, _agora, _config

CHECKLIST = "## O que precisa da sua decisão\n- Esta decisão segura se o volume triplicar?"


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()


def _alvo(raiz: Path, *specs: str) -> Path:
    pasta = raiz / "alvo"
    _specs_em(pasta, *(specs or ("alfa",)))
    _git_init(pasta)
    return pasta


class ExecutorComHomologar(ExecutorRoteirizado):
    """O roteirizado, mais a saída que `homologar` devolveria."""

    def __init__(self, alvo: Path, *, saida_homologar: str = CHECKLIST, **kwargs):
        super().__init__(alvo, **kwargs)
        self.saida_homologar = saida_homologar

    def __call__(self, comando, cwd):
        prompt = comando[-1]
        if prompt.startswith("Use a skill homologar"):
            self.chamadas.append(prompt)
            return 0, self.saida_homologar
        return super().__call__(comando, cwd)


def _homologacoes(executor) -> list[str]:
    return [p for p in executor.chamadas if p.startswith("Use a skill homologar")]


def test_o_lote_esgotado_invoca_homologar(tmp_path: Path):
    # spec:S8 — o loop não para mais antes dela.
    alvo = _alvo(tmp_path)
    executor = ExecutorComHomologar(alvo)

    relato = driver.rodar(_config(alvo, "alfa"), executor=executor, agora=_agora)

    assert len(_homologacoes(executor)) == 1
    assert relato.final.decisao.acao is Acao.ESCALAR


def test_o_prompt_de_homologar_carrega_specs_vereditos_e_base(tmp_path: Path):
    # spec:S9
    alvo = _alvo(tmp_path, "alfa", "beta")
    executor = ExecutorComHomologar(alvo)
    base = _git(alvo, "rev-parse", "HEAD")

    driver.rodar(_config(alvo, "alfa", "beta"), executor=executor, agora=_agora)

    prompt = _homologacoes(executor)[0]
    assert "alfa" in prompt and "beta" in prompt
    assert "alfa-veredito.md" in prompt and "beta-veredito.md" in prompt
    assert base in prompt
    assert str(alvo) in prompt


def test_o_ref_base_do_ciclo_e_o_da_primeira_spec(tmp_path: Path):
    # spec:S10 — não o da última, que já teria commits do ciclo em cima.
    alvo = _alvo(tmp_path, "alfa", "beta")
    executor = ExecutorComHomologar(alvo)
    base_do_ciclo = _git(alvo, "rev-parse", "HEAD")

    driver.rodar(_config(alvo, "alfa", "beta"), executor=executor, agora=_agora)

    prompt = _homologacoes(executor)[0]
    assert base_do_ciclo in prompt
    # o HEAD final é outro: houve commit de tentativa no meio
    assert _git(alvo, "rev-parse", "HEAD") != base_do_ciclo
    assert _git(alvo, "rev-parse", "HEAD") not in prompt


def test_a_saida_de_homologar_e_repassada_na_integra(tmp_path: Path):
    # spec:S11 — o que amacia um parecer é a paráfrase, não o encaminhamento.
    alvo = _alvo(tmp_path)
    executor = ExecutorComHomologar(alvo, saida_homologar=CHECKLIST)

    relato = driver.rodar(_config(alvo, "alfa"), executor=executor, agora=_agora)

    assert CHECKLIST in relato.texto
    assert relato.final.decisao.motivo is Motivo.GATE_CHECKLIST


def test_falha_de_homologar_escala_e_nao_fecha_o_ciclo(tmp_path: Path):
    # spec:S12
    alvo = _alvo(tmp_path)

    class HomologarFalha(ExecutorComHomologar):
        def __call__(self, comando, cwd):
            if comando[-1].startswith("Use a skill homologar"):
                self.chamadas.append(comando[-1])
                return 4, "estourou"
            return ExecutorRoteirizado.__call__(self, comando, cwd)

    relato = driver.rodar(
        _config(alvo, "alfa"), executor=HomologarFalha(alvo), agora=_agora
    )

    assert relato.final.decisao.acao is Acao.ESCALAR
    assert relato.final.decisao.motivo is Motivo.FALHA_DE_INVOCACAO
    assert relato.final.decisao.motivo is not Motivo.GATE_CHECKLIST


def test_homologar_conta_no_fusivel(tmp_path: Path):
    # spec:S8 — é invocação como qualquer outra.
    alvo = _alvo(tmp_path)
    executor = ExecutorComHomologar(alvo)

    relato = driver.rodar(_config(alvo, "alfa"), executor=executor, agora=_agora)

    # codificar, verificar, a auditoria da única spec, homologar
    assert relato.invocacoes == 4


def test_modo_seco_nao_invoca_homologar(tmp_path: Path):
    # spec:S8 + S4
    alvo = _alvo(tmp_path)
    executor = ExecutorComHomologar(alvo)

    driver.rodar(_config(alvo, "alfa", seco=True), executor=executor, agora=_agora)

    assert _homologacoes(executor) == []
    assert not registro.caminho_do_registro(alvo).exists()
