"""Ciclo do registro — spec: docs/specs/loop-ciclo.md (R1-R8)."""

from __future__ import annotations

import json
from pathlib import Path

import registro
from roteador import Acao, Decisao, Fase, Motivo

INVOCA_CODIFICAR = Decisao(
    Acao.INVOCAR, Motivo.TRANSICAO, fase=Fase.CODIFICAR, tentativa=1
)
INVOCA_VERIFICAR = Decisao(Acao.INVOCAR, Motivo.TRANSICAO, fase=Fase.VERIFICAR)
INVOCA_HOMOLOGAR = Decisao(Acao.INVOCAR, Motivo.TRANSICAO, fase=Fase.HOMOLOGAR)
ESCALA = Decisao(Acao.ESCALAR, Motivo.DEFEITO_DE_SPEC, evidencia=("C3",))


def _grava(caminho: Path, decisao: Decisao, spec: str = "alfa") -> None:
    registro.registrar(caminho, decisao=decisao, instante="t", alvo="/a", spec=spec)


def test_escalada_e_gravada(tmp_path: Path):
    # spec:R1 — sem isto o registro não sabe dizer por que o loop parou.
    caminho = tmp_path / "loop.jsonl"
    _grava(caminho, ESCALA)

    linhas = registro.linhas(caminho)
    assert len(linhas) == 1
    assert linhas[0]["transicao"] == "escalar"
    assert linhas[0]["motivo"] == "defeito-de-spec"


def test_encerramento_do_lote_e_gravado(tmp_path: Path):
    # spec:R2
    caminho = tmp_path / "loop.jsonl"
    _grava(caminho, INVOCA_HOMOLOGAR)
    assert registro.linhas(caminho)[0]["transicao"] == "invocar:homologar"


def test_escalada_e_homologar_sao_terminais(tmp_path: Path):
    # spec:R3
    for decisao in (ESCALA, INVOCA_HOMOLOGAR):
        caminho = tmp_path / f"loop-{decisao.motivo.value}-{decisao.fase}.jsonl"
        _grava(caminho, INVOCA_CODIFICAR)
        _grava(caminho, decisao)
        assert registro.ciclo_encerrado(caminho) is True


def test_invocacao_no_meio_nao_e_terminal(tmp_path: Path):
    # spec:R4
    caminho = tmp_path / "loop.jsonl"
    _grava(caminho, INVOCA_CODIFICAR)
    _grava(caminho, INVOCA_VERIFICAR)
    assert registro.ciclo_encerrado(caminho) is False


def test_ciclo_encerrado_e_arquivado_e_o_novo_comeca_vazio(tmp_path: Path):
    # spec:R3
    caminho = tmp_path / "loop.jsonl"
    _grava(caminho, INVOCA_CODIFICAR)
    _grava(caminho, ESCALA)
    conteudo = caminho.read_text(encoding="utf-8")

    arquivado = registro.arquivar_se_encerrado(caminho)

    assert arquivado == tmp_path / "loop-1.jsonl"
    assert arquivado.read_text(encoding="utf-8") == conteudo
    assert not caminho.exists()


def test_ciclo_interrompido_nao_e_arquivado(tmp_path: Path):
    # spec:R4
    caminho = tmp_path / "loop.jsonl"
    _grava(caminho, INVOCA_CODIFICAR)

    assert registro.arquivar_se_encerrado(caminho) is None
    assert caminho.exists()
    assert len(registro.linhas(caminho)) == 1


def test_arquivamentos_sucessivos_nao_colidem(tmp_path: Path):
    # spec:R5
    caminho = tmp_path / "loop.jsonl"
    for esperado in ("loop-1.jsonl", "loop-2.jsonl", "loop-3.jsonl"):
        _grava(caminho, ESCALA)
        assert registro.arquivar_se_encerrado(caminho).name == esperado
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "loop-1.jsonl",
        "loop-2.jsonl",
        "loop-3.jsonl",
    ]


def test_arquivamento_preserva_byte_a_byte(tmp_path: Path):
    # spec:R5
    caminho = tmp_path / "loop.jsonl"
    _grava(caminho, INVOCA_CODIFICAR, spec="acentuação")
    _grava(caminho, ESCALA)
    bytes_originais = caminho.read_bytes()

    arquivado = registro.arquivar_se_encerrado(caminho)

    assert arquivado.read_bytes() == bytes_originais
    assert json.loads(arquivado.read_text(encoding="utf-8").splitlines()[0])["spec"] == (
        "acentuação"
    )


def test_registro_inexistente_e_ciclo_novo(tmp_path: Path):
    # spec:R6
    caminho = tmp_path / "loop.jsonl"
    assert registro.ciclo_encerrado(caminho) is False
    assert registro.arquivar_se_encerrado(caminho) is None
    assert list(tmp_path.iterdir()) == []


def test_registro_vazio_nao_quebra(tmp_path: Path):
    # spec:R6
    caminho = tmp_path / "loop.jsonl"
    caminho.write_text("", encoding="utf-8")
    assert registro.ciclo_encerrado(caminho) is False
    assert registro.arquivar_se_encerrado(caminho) is None


def test_tentativas_do_ciclo_anterior_nao_contam(tmp_path: Path):
    # spec:R7 — o bug que motivou esta spec: spec emendada nascia esgotada.
    caminho = tmp_path / "loop.jsonl"
    for _ in range(3):
        _grava(caminho, INVOCA_CODIFICAR)
    _grava(caminho, ESCALA)
    assert registro.contar_tentativas(caminho, "alfa") == 3

    registro.arquivar_se_encerrado(caminho)

    assert registro.contar_tentativas(caminho, "alfa") == 0


def test_tentativas_acumulam_dentro_do_mesmo_ciclo(tmp_path: Path):
    # spec:R8 — interromper e reexecutar não zera nem repete.
    caminho = tmp_path / "loop.jsonl"
    _grava(caminho, INVOCA_CODIFICAR)
    _grava(caminho, INVOCA_VERIFICAR)

    assert registro.arquivar_se_encerrado(caminho) is None
    _grava(caminho, INVOCA_CODIFICAR)

    assert registro.contar_tentativas(caminho, "alfa") == 2


def test_a_linha_terminal_nunca_e_uma_invocacao_de_codificar(tmp_path: Path):
    # spec:R8 — se o laço saísse com a decisão ainda em `invocar:codificar`, a
    # gravação final inventaria uma tentativa que não aconteceu, e o ciclo
    # seguinte a contaria contra o teto.
    from test_driver import SPEC_LIVRE, ExecutorRoteirizado, _agora, _alvo, _config

    import driver

    vermelho = {"alfa": "- **C1** — não atendido\n"}
    saidas = (
        ("fusível", dict(fusivel=1, teto=9), vermelho),
        ("teto", dict(fusivel=99, teto=1), vermelho),
        ("falha", dict(), None),
        ("fechamento", dict(), {}),
    )

    for nome, opcoes, vereditos in saidas:
        alvo = _alvo(
            tmp_path / nome, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma.")
        )
        executor = ExecutorRoteirizado(
            alvo,
            vereditos=vereditos or {},
            exit_codes=[3] if vereditos is None else None,
        )
        driver.rodar(_config(alvo, "alfa", **opcoes), executor=executor, agora=_agora)

        ultima = registro.linhas(registro.caminho_do_registro(alvo))[-1]
        assert ultima["transicao"] != "invocar:codificar", nome
        assert registro.ciclo_encerrado(registro.caminho_do_registro(alvo)), nome


def test_o_driver_arquiva_e_a_spec_emendada_nao_nasce_esgotada(tmp_path: Path):
    # spec:R7 — o cenário inteiro, do jeito que dói: a spec estoura o teto,
    # você a emenda semanas depois, e roda de novo no mesmo alvo.
    from test_driver import SPEC_LIVRE, ExecutorRoteirizado, _agora, _alvo, _config

    import driver

    alvo = _alvo(tmp_path, alfa=SPEC_LIVRE.format(nome="alfa", depende="Nenhuma."))
    caminho = registro.caminho_do_registro(alvo)
    vermelho = {"alfa": "- **C1** — não atendido\n"}

    primeiro = driver.rodar(
        _config(alvo, "alfa", teto=2),
        executor=ExecutorRoteirizado(alvo, vereditos=vermelho),
        agora=_agora,
    )
    assert primeiro.final.decisao.motivo is Motivo.TETO_DE_TENTATIVAS
    assert registro.contar_tentativas(caminho, "alfa") == 2

    segundo = driver.rodar(
        _config(alvo, "alfa", teto=2),
        executor=ExecutorRoteirizado(alvo),
        agora=_agora,
    )

    assert (alvo / ".sle" / "loop-1.jsonl").exists()
    assert segundo.final.decisao.motivo is Motivo.GATE_CHECKLIST
    assert registro.contar_tentativas(caminho, "alfa") == 1
