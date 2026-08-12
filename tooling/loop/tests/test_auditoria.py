"""Auditoria de critérios — spec: docs/specs/loop-auditoria.md (F1-F12)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import auditoria
import driver
from roteador import Acao, Fase, Motivo
from test_alvo import _git_init
from test_driver import SPEC_LIVRE, SPEC_TRAVADA, ExecutorRoteirizado, _agora, _config
from test_homologar import ExecutorComHomologar

VERDE = "- **C1** — atendido\n"
VERMELHO = "- **C1** — não atendido: deixou de valer\n"


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()


def _alvo(raiz: Path, **specs: str) -> Path:
    pasta = raiz / "alvo"
    (pasta / "docs" / "specs").mkdir(parents=True)
    for nome, conteudo in specs.items():
        (pasta / "docs" / "specs" / f"{nome}.md").write_text(conteudo, encoding="utf-8")
    _git_init(pasta)
    return pasta


class ExecutorComAuditoria(ExecutorComHomologar):
    """Responde também à auditoria, escrevendo o arquivo que ela cobra."""

    def __init__(self, alvo: Path, *, auditorias=None, **kwargs):
        super().__init__(alvo, **kwargs)
        self.auditorias = dict(auditorias or {})
        self.auditadas: list[str] = []

    def __call__(self, comando, cwd):
        prompt = comando[-1]
        if "-auditoria.md" in prompt:
            self.chamadas.append(prompt)
            nome = prompt.split("-auditoria.md")[0].split("/")[-1].split("\\")[-1]
            self.auditadas.append(nome)
            (self.alvo / "docs" / "specs" / f"{nome}-auditoria.md").write_text(
                self.auditorias.get(nome, VERDE), encoding="utf-8"
            )
            return 0, ""
        return super().__call__(comando, cwd)


def _rodar(alvo: Path, executor, *specs: str, **kwargs):
    return driver.rodar(
        _config(alvo, *(specs or ("alfa",)), **kwargs), executor=executor, agora=_agora
    )


def test_audita_todas_as_specs_do_alvo_nao_so_as_do_ciclo(tmp_path: Path):
    # spec:F2
    alvo = _alvo(
        tmp_path,
        alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."),
        antiga=SPEC_LIVRE.format(nome="antiga", depende="Nenhuma."),
    )
    executor = ExecutorComAuditoria(alvo)

    _rodar(alvo, executor, "alfa")

    assert sorted(executor.auditadas) == ["alfa", "antiga"]


def test_a_auditoria_roda_antes_de_homologar(tmp_path: Path):
    # spec:F1
    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))
    executor = ExecutorComAuditoria(alvo)

    _rodar(alvo, executor)

    ordem = [
        "auditoria" if "-auditoria.md" in p else "homologar"
        for p in executor.chamadas
        if "-auditoria.md" in p or p.startswith("Use a skill homologar")
    ]
    assert ordem == ["auditoria", "homologar"]


def test_spec_cujo_nome_termina_como_derivado_ainda_e_spec(tmp_path: Path):
    # spec:F2 — `loop-auditoria.md` é spec de verdade, e o filtro por substring
    # a descartava: a auditoria deixava de auditar a spec que a define.
    alvo = _alvo(
        tmp_path,
        alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."),
        **{"loop-auditoria": SPEC_LIVRE.format(nome="loop-auditoria", depende="Nenhuma.")},
    )
    (alvo / "docs" / "specs" / "alfa-auditoria.md").write_text(VERDE, encoding="utf-8")
    (alvo / "docs" / "specs" / "alfa-veredito-1.md").write_text(VERDE, encoding="utf-8")

    nomes = auditoria.auditaveis(alvo)

    assert "loop-auditoria" in nomes
    assert "alfa" in nomes
    assert "alfa-auditoria" not in nomes
    assert "alfa-veredito-1" not in nomes


def test_auditoria_nao_produzida_nao_conta_como_verde(tmp_path: Path):
    # spec:F10 — ausência não é aprovação; mesmo princípio do parser.
    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))

    assert auditoria.regressoes(alvo, "alfa") != ()


def test_spec_em_quarentena_nao_e_auditada(tmp_path: Path):
    # spec:F3 — cobrar critério de spec não construída seria reprovar o que
    # ninguém fez.
    alvo = _alvo(
        tmp_path,
        alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."),
        travada=SPEC_TRAVADA.format(nome="travada"),
    )
    executor = ExecutorComAuditoria(alvo)

    _rodar(alvo, executor, "alfa", "travada")

    assert "travada" not in executor.auditadas
    assert "alfa" in executor.auditadas


def test_quarentena_por_dependencia_tambem_fica_de_fora(tmp_path: Path):
    # spec:F3 — a quarentena é transitiva no laço; aqui também precisa ser.
    alvo = _alvo(
        tmp_path,
        alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."),
        travada=SPEC_TRAVADA.format(nome="travada"),
        dependente=SPEC_LIVRE.format(nome="dependente", depende="`travada`"),
    )

    nomes = auditoria.auditaveis(alvo)

    assert "alfa" in nomes
    assert "travada" not in nomes
    assert "dependente" not in nomes


def test_cada_invocacao_da_auditoria_conta_no_fusivel(tmp_path: Path):
    # spec:F4
    alvo = _alvo(
        tmp_path,
        alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."),
        antiga=SPEC_LIVRE.format(nome="antiga", depende="Nenhuma."),
    )
    executor = ExecutorComAuditoria(alvo)

    relato = _rodar(alvo, executor, "alfa")

    # codificar + verificar + 2 auditorias + homologar
    assert relato.invocacoes == 5


def test_uma_invocacao_por_spec(tmp_path: Path):
    # spec:F5
    alvo = _alvo(
        tmp_path,
        alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."),
        antiga=SPEC_LIVRE.format(nome="antiga", depende="Nenhuma."),
    )
    executor = ExecutorComAuditoria(alvo)

    _rodar(alvo, executor, "alfa")

    auditorias = [p for p in executor.chamadas if "-auditoria.md" in p]
    assert len(auditorias) == 2
    assert len(set(auditorias)) == 2


def test_o_molde_pede_estado_atual_e_nao_diff(tmp_path: Path):
    # spec:F6 + F7 — molde já existente, e nenhuma skill citada.
    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))
    executor = ExecutorComAuditoria(alvo)

    _rodar(alvo, executor)

    prompt = [p for p in executor.chamadas if "-auditoria.md" in p][0]
    assert "estado atual" in prompt
    assert "diff" not in prompt and "Ref base" not in prompt
    assert "Use a skill" not in prompt


def test_nenhum_arquivo_de_skill_e_lido_ou_citado():
    # spec:F7
    prompt = auditoria.prompt_de(Path("/alvo"), "alfa", escopo=".")
    assert "SKILL.md" not in prompt
    assert "Use a skill" not in prompt
    assert "alfa.md" in prompt and "alfa-auditoria.md" in prompt


def test_o_resultado_vai_para_arquivo_proprio(tmp_path: Path):
    # spec:F8
    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))

    _rodar(alvo, ExecutorComAuditoria(alvo))

    assert (alvo / "docs" / "specs" / "alfa-auditoria.md").exists()


def test_o_veredito_da_demanda_nao_e_tocado(tmp_path: Path):
    # spec:F9 — as duas perguntas são diferentes.
    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))

    _rodar(alvo, ExecutorComAuditoria(alvo))

    veredito = alvo / "docs" / "specs" / "alfa-veredito.md"
    assert veredito.exists()
    assert veredito.read_text(encoding="utf-8") == "- **C1** — atendido\n"


def test_regressao_escala_e_homologar_nao_roda(tmp_path: Path):
    # spec:F10
    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))
    executor = ExecutorComAuditoria(alvo, auditorias={"alfa": VERMELHO})

    relato = _rodar(alvo, executor)

    assert relato.final.decisao.acao is Acao.ESCALAR
    assert relato.final.decisao.motivo is Motivo.REGRESSAO_DE_CRITERIO
    assert not [p for p in executor.chamadas if p.startswith("Use a skill homologar")]


def test_criterio_nao_verificavel_tambem_e_regressao(tmp_path: Path):
    # spec:F10
    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))
    executor = ExecutorComAuditoria(
        alvo, auditorias={"alfa": "- **C1** — não verificável\n"}
    )

    relato = _rodar(alvo, executor)

    assert relato.final.decisao.motivo is Motivo.REGRESSAO_DE_CRITERIO


def test_auditoria_verde_segue_para_homologar(tmp_path: Path):
    # spec:F11
    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))
    executor = ExecutorComAuditoria(alvo)

    relato = _rodar(alvo, executor)

    assert relato.final.decisao.motivo is Motivo.GATE_CHECKLIST
    assert [p for p in executor.chamadas if p.startswith("Use a skill homologar")]


def test_o_relato_nomeia_a_spec_e_o_caminho_sem_transcrever(tmp_path: Path):
    # spec:F12
    segredo = "MOTIVO-QUE-NAO-PODE-VAZAR"
    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))
    executor = ExecutorComAuditoria(
        alvo, auditorias={"alfa": f"- **C1** — não atendido: {segredo}\n"}
    )

    relato = _rodar(alvo, executor)

    assert "alfa" in relato.texto
    assert "alfa-auditoria.md" in relato.texto
    assert segredo not in relato.texto
