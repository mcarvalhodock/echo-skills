"""O laço — spec: docs/specs/roteador-driver.md (D1-D11)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import driver
import registro
from roteador import Acao, Fase, Motivo

SPEC_LIVRE = """# {nome}

## Depende de
{depende}

## Critérios
- [ ] **C1** `[miolo]` — algo

## Perguntas em aberto
Nenhuma.
"""

SPEC_TRAVADA = """# {nome}

## Depende de
Nenhuma.

## Perguntas em aberto
- Qual banco de dados?
"""


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()


def _alvo(raiz: Path, nome: str = "alvo", **specs: str) -> Path:
    repo = raiz / nome
    (repo / "docs" / "specs").mkdir(parents=True)
    for spec, conteudo in specs.items():
        (repo / "docs" / "specs" / f"{spec}.md").write_text(conteudo, encoding="utf-8")
    _git(repo, "init", "-q", "-b", "trabalho")
    _git(repo, "config", "user.email", "loop@teste")
    _git(repo, "config", "user.name", "loop")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "inicial")
    return repo


class ExecutorRoteirizado:
    """Finge as fases: escreve veredito, mexe em arquivo, devolve exit code."""

    def __init__(self, alvo: Path, *, vereditos=None, exit_codes=None):
        self.alvo = alvo
        self.vereditos = dict(vereditos or {})
        self.exit_codes = list(exit_codes or [])
        self.chamadas: list[str] = []

    def __call__(self, comando, cwd):
        prompt = comando[-1]
        self.chamadas.append(prompt)

        if "codificar" in prompt:
            alvo_arquivo = self.alvo / "src.py"
            alvo_arquivo.write_text(f"# {len(self.chamadas)}\n", encoding="utf-8")
        if "verificar" in prompt:
            spec = self._spec_de(prompt)
            destino = self.alvo / "docs" / "specs" / f"{spec}-veredito.md"
            destino.write_text(
                self.vereditos.get(spec, "- **C1** — atendido\n"), encoding="utf-8"
            )

        if self.exit_codes:
            return self.exit_codes.pop(0), "saida qualquer"
        return 0, "saida qualquer"

    def _spec_de(self, prompt: str) -> str:
        for bruto in prompt.split():
            pedaco = bruto.rstrip(".,;")
            if pedaco.endswith(".md") and "-veredito" not in pedaco:
                return Path(pedaco).stem
        raise AssertionError(f"prompt sem caminho de spec: {prompt}")


def _config(alvo: Path, *specs: str, **kwargs) -> driver.Config:
    return driver.Config(alvo=alvo, specs=tuple(specs), **kwargs)


def _agora():
    return "2026-08-12T00:00:00"


def test_monta_o_estado_lendo_as_specs_do_alvo(tmp_path: Path):
    # spec:D1
    alvo = _alvo(
        tmp_path,
        alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."),
        beta=SPEC_TRAVADA.format(nome="beta"),
    )
    specs = driver.montar_specs(alvo, ("alfa", "beta"))

    assert [s.nome for s in specs] == ["alfa", "beta"]
    assert specs[0].insumo_faltante == ()
    assert specs[1].insumo_faltante == ("Qual banco de dados?",)


def test_registra_a_decisao_antes_de_invocar(tmp_path: Path):
    # spec:D2
    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))
    ordem: list[str] = []

    def executor(comando, cwd):
        ordem.append("invocou")
        return 1, ""

    def registrar_espiao(*args, **kwargs):
        ordem.append("registrou")
        return registro.registrar(*args, **kwargs)

    driver.rodar(
        _config(alvo, "alfa"),
        executor=executor,
        agora=_agora,
        registrar=registrar_espiao,
    )
    assert ordem[:2] == ["registrou", "invocou"]


def test_tentativas_vem_do_registro_e_nao_da_memoria(tmp_path: Path):
    # spec:D3
    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))
    caminho = registro.caminho_do_registro(alvo)

    executor = ExecutorRoteirizado(alvo, vereditos={"alfa": "- **C1** — não atendido\n"})
    driver.rodar(_config(alvo, "alfa", teto=2), executor=executor, agora=_agora)

    assert registro.contar_tentativas(caminho, "alfa") == 2


def test_fusivel_escala_com_motivo_proprio(tmp_path: Path):
    # spec:D4 — nunca confundido com teto-de-tentativas.
    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))
    executor = ExecutorRoteirizado(alvo, vereditos={"alfa": "- **C1** — não atendido\n"})

    relato = driver.rodar(
        _config(alvo, "alfa", fusivel=2, teto=99), executor=executor, agora=_agora
    )

    assert relato.final.decisao.acao is Acao.ESCALAR
    assert relato.final.decisao.motivo is Motivo.FUSIVEL
    assert relato.invocacoes == 2
    assert "teto-de-tentativas" not in relato.texto


def test_falha_de_invocacao_escala_em_vez_de_avancar(tmp_path: Path):
    # spec:D5
    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))
    executor = ExecutorRoteirizado(alvo, exit_codes=[3])

    relato = driver.rodar(_config(alvo, "alfa"), executor=executor, agora=_agora)

    assert relato.final.decisao.acao is Acao.ESCALAR
    assert relato.invocacoes == 1
    assert len(executor.chamadas) == 1


def test_alvo_e_obrigatorio(tmp_path: Path):
    # spec:D6
    with pytest.raises(TypeError):
        driver.Config(specs=("alfa",))


def test_dois_alvos_nao_se_misturam(tmp_path: Path):
    # spec:D7
    a = _alvo(tmp_path, "a", alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))
    b = _alvo(tmp_path, "b", alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))
    antes = sorted(p.name for p in (b / "docs" / "specs").iterdir())

    driver.rodar(
        _config(a, "alfa"), executor=ExecutorRoteirizado(a), agora=_agora
    )

    assert not registro.caminho_do_registro(b).exists()
    assert sorted(p.name for p in (b / "docs" / "specs").iterdir()) == antes


def test_ref_base_e_o_de_antes_da_primeira_tentativa(tmp_path: Path):
    # spec:D8 — retentativa não reencurta o diff.
    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))
    base_real = _git(alvo, "rev-parse", "HEAD")
    executor = ExecutorRoteirizado(alvo, vereditos={"alfa": "- **C1** — não atendido\n"})

    driver.rodar(_config(alvo, "alfa", teto=2), executor=executor, agora=_agora)

    verificacoes = [p for p in executor.chamadas if "verificar" in p]
    assert len(verificacoes) == 2
    for prompt in verificacoes:
        assert base_real in prompt


def test_escalada_nao_transcreve_o_veredito(tmp_path: Path):
    # spec:D9
    segredo = "JUSTIFICATIVA QUE NAO PODE VAZAR"
    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))
    executor = ExecutorRoteirizado(
        alvo, vereditos={"alfa": f"- **C1** — não verificável: {segredo}\n"}
    )

    relato = driver.rodar(_config(alvo, "alfa"), executor=executor, agora=_agora)

    assert relato.final.decisao.motivo is Motivo.DEFEITO_DE_SPEC
    assert segredo not in relato.texto
    assert "alfa-veredito.md" in relato.texto
    assert "defeito-de-spec" in relato.texto


def test_fechamento_informa_as_tres_listas(tmp_path: Path):
    # spec:D10
    alvo = _alvo(
        tmp_path,
        alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."),
        beta=SPEC_TRAVADA.format(nome="beta"),
        gama=SPEC_LIVRE.format(nome="gama", depende="`beta`"),
    )
    relato = driver.rodar(
        _config(alvo, "alfa", "beta", "gama"),
        executor=ExecutorRoteirizado(alvo),
        agora=_agora,
    )

    assert relato.final.decisao.fase is Fase.HOMOLOGAR
    assert "alfa" in relato.texto
    assert "beta" in relato.texto and "gama" in relato.texto
    assert "Qual banco de dados?" in relato.texto


def test_modo_seco_nao_invoca_nem_registra_nem_commita(tmp_path: Path):
    # spec:D11
    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))
    commits_antes = _git(alvo, "rev-list", "--count", "HEAD")
    executor = ExecutorRoteirizado(alvo)

    relato = driver.rodar(
        _config(alvo, "alfa", seco=True), executor=executor, agora=_agora
    )

    assert executor.chamadas == []
    assert not registro.caminho_do_registro(alvo).exists()
    assert _git(alvo, "rev-list", "--count", "HEAD") == commits_antes
    assert "alfa" in relato.texto
    assert relato.invocacoes == 0


def test_ciclo_completo_fecha_e_commita_por_tentativa(tmp_path: Path):
    # spec:D2 + D8 — o caminho feliz inteiro, com histórico marcado.
    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))
    executor = ExecutorRoteirizado(alvo)

    relato = driver.rodar(_config(alvo, "alfa"), executor=executor, agora=_agora)

    assert relato.final.decisao.fase is Fase.HOMOLOGAR
    marcados = _git(alvo, "log", "--grep=^SLE-Loop:", "--format=%s").splitlines()
    assert marcados == ["loop(alfa): codificar tentativa 1"]
