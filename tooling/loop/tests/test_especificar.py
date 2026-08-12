"""Fila de especificar — spec: docs/specs/loop-especificar.md (P4-P11)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import driver
import registro
import secoes
from roteador import Acao, Fase, Motivo
from test_alvo import _git_init
from test_driver import _agora

SPEC_PRODUZIDA = """# {nome}

## Depende de
Nenhuma.

## Critérios
- [ ] **C1** `[miolo]` — algo falsificável
- [ ] **C2** `[plataforma, integração]` — outra coisa

## Perguntas em aberto
{perguntas}
"""

PEDIDOS = "## cadastro\n\nQuero cadastro.\n\n## cobranca\n\nQuero cobrança.\n"


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()


def _alvo(raiz: Path, pedidos_md: str = PEDIDOS, *, versionar_pedidos: bool = True) -> Path:
    pasta = raiz / "alvo"
    (pasta / "docs" / "specs").mkdir(parents=True)
    (pasta / "docs" / "specs" / ".gitkeep").write_text("", encoding="utf-8")
    if versionar_pedidos:
        (pasta / "pedidos.md").write_text(pedidos_md, encoding="utf-8")
    _git_init(pasta)
    if not versionar_pedidos:
        (pasta / "pedidos.md").write_text(pedidos_md, encoding="utf-8")
    return pasta


class EspecificadorFalso:
    """Escreve a spec que `especificar` escreveria, e registra o prompt."""

    def __init__(self, alvo: Path, *, perguntas: dict | None = None, criterios=None):
        self.alvo = alvo
        self.perguntas = dict(perguntas or {})
        self.criterios = criterios or {}
        self.chamadas: list[str] = []

    def __call__(self, comando, cwd):
        prompt = comando[-1]
        self.chamadas.append(prompt)
        nome = prompt.split("Nome da spec: ")[1].split(".")[0].strip()

        corpo = SPEC_PRODUZIDA.format(
            nome=nome, perguntas=self.perguntas.get(nome, "Nenhuma.")
        )
        if nome in self.criterios:
            extras = "\n".join(
                f"- [ ] **C{i}** `[miolo]` — item" for i in range(3, self.criterios[nome] + 1)
            )
            corpo = corpo.replace("## Perguntas em aberto", extras + "\n\n## Perguntas em aberto")
        (self.alvo / "docs" / "specs" / f"{nome}.md").write_text(corpo, encoding="utf-8")
        return 0, "ok"


def _config(alvo: Path, **kwargs) -> driver.Config:
    return driver.Config(alvo=alvo, specs=(), pedidos="pedidos.md", **kwargs)


def test_le_criterios_e_dominios_da_spec():
    # spec:P9
    lidos = secoes.criterios(SPEC_PRODUZIDA.format(nome="x", perguntas="Nenhuma."))
    assert lidos == (("C1", ("miolo",)), ("C2", ("plataforma", "integração")))


def test_spec_existente_e_pulada_sem_invocacao(tmp_path: Path):
    # spec:P4
    alvo = _alvo(tmp_path)
    (alvo / "docs" / "specs" / "cadastro.md").write_text("# ja existe\n", encoding="utf-8")
    _git(alvo, "add", "-A")
    _git(alvo, "commit", "-q", "-m", "spec anterior")
    executor = EspecificadorFalso(alvo)

    relato = driver.rodar_pedidos(_config(alvo), executor=executor, agora=_agora)

    assert len(executor.chamadas) == 1
    assert "cobranca" in executor.chamadas[0]
    assert "cadastro" in relato.texto and "pulad" in relato.texto
    assert (alvo / "docs" / "specs" / "cadastro.md").read_text(encoding="utf-8") == (
        "# ja existe\n"
    )


def test_cada_pedido_vira_uma_invocacao_com_nome_texto_e_alvo(tmp_path: Path):
    # spec:P5
    alvo = _alvo(tmp_path)
    executor = EspecificadorFalso(alvo)

    driver.rodar_pedidos(_config(alvo), executor=executor, agora=_agora)

    assert len(executor.chamadas) == 2
    assert all(p.startswith("Use a skill especificar") for p in executor.chamadas)
    assert "Nome da spec: cadastro" in executor.chamadas[0]
    assert "Quero cadastro." in executor.chamadas[0]
    assert str(alvo) in executor.chamadas[0]


def test_spec_nao_produzida_escala(tmp_path: Path):
    # spec:P6
    alvo = _alvo(tmp_path)

    def nao_escreve(comando, cwd):
        return 0, "disse que fez"

    relato = driver.rodar_pedidos(_config(alvo), executor=nao_escreve, agora=_agora)

    assert relato.final.decisao.acao is Acao.ESCALAR
    assert relato.final.decisao.motivo is Motivo.FALHA_DE_INVOCACAO


def test_cada_spec_vira_um_commit_marcado(tmp_path: Path):
    # spec:P7
    alvo = _alvo(tmp_path)

    driver.rodar_pedidos(_config(alvo), executor=EspecificadorFalso(alvo), agora=_agora)

    assuntos = _git(alvo, "log", "--grep=^SLE-Loop:", "--format=%s").splitlines()
    assert assuntos == ["loop(cobranca): especificar", "loop(cadastro): especificar"]
    corpo = _git(alvo, "log", "-1", "--format=%b")
    assert "SLE-Loop: cobranca#spec" in corpo


def test_a_fila_para_no_gate_e_nunca_chama_codificar(tmp_path: Path):
    # spec:P8
    alvo = _alvo(tmp_path)
    executor = EspecificadorFalso(alvo)

    relato = driver.rodar_pedidos(_config(alvo), executor=executor, agora=_agora)

    assert relato.final.decisao.acao is Acao.ESCALAR
    assert relato.final.decisao.motivo is Motivo.GATE_SPEC_APROVADA
    assert all("codificar" not in p for p in executor.chamadas)
    transicoes = [l["transicao"] for l in registro.linhas(registro.caminho_do_registro(alvo))]
    assert "invocar:codificar" not in transicoes


def test_relatorio_diz_quantos_criterios_e_quais_dominios(tmp_path: Path):
    # spec:P9
    alvo = _alvo(tmp_path)

    relato = driver.rodar_pedidos(_config(alvo), executor=EspecificadorFalso(alvo), agora=_agora)

    assert "cadastro" in relato.texto and "cobranca" in relato.texto
    assert "2 critérios" in relato.texto
    assert "miolo" in relato.texto and "plataforma" in relato.texto


def test_spec_com_pergunta_em_aberto_aparece_bloqueada(tmp_path: Path):
    # spec:P10
    alvo = _alvo(tmp_path)
    executor = EspecificadorFalso(
        alvo, perguntas={"cobranca": "- Qual gateway de pagamento?"}
    )

    relato = driver.rodar_pedidos(_config(alvo), executor=executor, agora=_agora)

    assert "bloqueada" in relato.texto
    assert "Qual gateway de pagamento?" in relato.texto
    linha_cadastro = [l for l in relato.texto.splitlines() if "cadastro" in l][0]
    assert "bloqueada" not in linha_cadastro


def test_spec_que_estoura_o_teto_aparece_marcada(tmp_path: Path):
    # spec:P11 — o teto é de `especificar`; o relatório expõe quando foi furado.
    alvo = _alvo(tmp_path)
    executor = EspecificadorFalso(alvo, criterios={"cobranca": 18})

    relato = driver.rodar_pedidos(_config(alvo), executor=executor, agora=_agora)

    linha = [l for l in relato.texto.splitlines() if "cobranca" in l][0]
    assert "18 critérios" in linha
    assert "teto" in linha
    assert "teto" not in [l for l in relato.texto.splitlines() if "cadastro" in l][0]


def test_modo_seco_nao_invoca_a_fila(tmp_path: Path):
    # spec:P8 — `--seco` significa o mesmo nos dois segmentos.
    alvo = _alvo(tmp_path)
    executor = EspecificadorFalso(alvo)

    relato = driver.rodar_pedidos(
        _config(alvo, seco=True), executor=executor, agora=_agora
    )

    assert executor.chamadas == []
    assert not registro.caminho_do_registro(alvo).exists()
    assert not (alvo / "docs" / "specs" / "cadastro.md").exists()
    assert "cadastro" in relato.texto and "cobranca" in relato.texto


def test_pedidos_e_specs_juntos_e_erro_de_invocacao(tmp_path: Path):
    # spec:P3 — a fronteira entre os dois segmentos é explícita.
    alvo = _alvo(tmp_path)
    relato = driver.rodar_pedidos(
        driver.Config(alvo=alvo, specs=("cadastro",), pedidos="pedidos.md"),
        executor=EspecificadorFalso(alvo),
        agora=_agora,
    )
    assert relato.final.decisao.acao is Acao.ESCALAR


def test_arquivo_de_pedidos_ausente_escala(tmp_path: Path):
    # spec:P3
    alvo = _alvo(tmp_path)
    (alvo / "pedidos.md").unlink()
    _git(alvo, "add", "-A")
    _git(alvo, "commit", "-q", "-m", "sem pedidos")

    relato = driver.rodar_pedidos(_config(alvo), executor=EspecificadorFalso(alvo), agora=_agora)

    assert relato.final.decisao.acao is Acao.ESCALAR
    assert "pedidos.md" in relato.texto


def test_cabecalho_invalido_escala_nomeando_o_cabecalho(tmp_path: Path):
    # spec:P2
    alvo = _alvo(tmp_path, "## Cadastro de Clientes\n\ntexto\n")
    executor = EspecificadorFalso(alvo)

    relato = driver.rodar_pedidos(_config(alvo), executor=executor, agora=_agora)

    assert relato.final.decisao.acao is Acao.ESCALAR
    assert "Cadastro de Clientes" in relato.texto
    assert executor.chamadas == []
