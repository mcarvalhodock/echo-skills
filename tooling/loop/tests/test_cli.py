"""A ferramenta `sle` — spec: docs/specs/loop-cli.md (S1-S7)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import driver
from roteador import Motivo
from test_especificar import EspecificadorFalso, _alvo

INVOLUCROS = (
    driver.CLONE_DO_METODO / "scripts" / "sle",
    driver.CLONE_DO_METODO / "scripts" / "sle.ps1",
)


def test_pedir_roda_o_segmento_um(tmp_path: Path, monkeypatch):
    # spec:S1
    alvo = _alvo(tmp_path)
    chamados: list[str] = []
    monkeypatch.setattr(
        driver, "rodar_pedidos", lambda config, **k: chamados.append("pedidos") or _relato_gate()
    )
    monkeypatch.setattr(driver, "rodar", lambda config, **k: chamados.append("specs") or _relato_gate())

    driver.main(["pedir", "--alvo", str(alvo)])

    assert chamados == ["pedidos"]


def test_rodar_roda_o_segmento_dois(tmp_path: Path, monkeypatch):
    # spec:S2
    alvo = _alvo(tmp_path)
    chamados: list[str] = []
    monkeypatch.setattr(driver, "rodar_pedidos", lambda config, **k: chamados.append("pedidos") or _relato_gate())
    monkeypatch.setattr(
        driver, "rodar", lambda config, **k: chamados.append("specs") or _relato_gate()
    )

    driver.main(["rodar", "--alvo", str(alvo), "--specs", "alfa"])

    assert chamados == ["specs"]


@pytest.mark.parametrize("argv", [[], ["inventado", "--alvo", "."]])
def test_sem_subcomando_ou_com_desconhecido_mostra_ajuda_e_falha(argv, capsys):
    # spec:S3
    with pytest.raises(SystemExit) as saida:
        driver.main(argv)

    assert saida.value.code != 0
    texto = capsys.readouterr()
    assert "pedir" in (texto.out + texto.err)


def test_seco_vale_nos_dois_subcomandos(tmp_path: Path, monkeypatch):
    # spec:S4
    alvo = _alvo(tmp_path)
    vistos: list[bool] = []
    monkeypatch.setattr(driver, "rodar_pedidos", lambda c, **k: vistos.append(c.seco) or _relato_gate())
    monkeypatch.setattr(driver, "rodar", lambda c, **k: vistos.append(c.seco) or _relato_gate())

    driver.main(["pedir", "--alvo", str(alvo), "--seco"])
    driver.main(["rodar", "--alvo", str(alvo), "--specs", "alfa", "--seco"])

    assert vistos == [True, True]


def test_os_involucros_existem_e_apontam_para_o_driver():
    # spec:S5
    for involucro in INVOLUCROS:
        assert involucro.exists(), involucro
        conteudo = involucro.read_text(encoding="utf-8")
        assert "driver.py" in conteudo
        assert "python" in conteudo.lower()


def test_o_involucro_sh_e_executavel():
    # spec:S5 — "executável" é bit, não intenção. No Windows o sistema de
    # arquivos não carrega o modo, então quem responde é o índice do git.
    modo = subprocess.run(
        ["git", "ls-files", "-s", "scripts/sle"],
        cwd=driver.CLONE_DO_METODO,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()[0]

    assert modo == "100755", f"scripts/sle está {modo}; em POSIX não roda"


def test_ensaio_nao_sai_como_falha(tmp_path: Path, monkeypatch):
    # spec:S6 — nada foi tentado, então não há insucesso a reportar.
    alvo = _alvo(tmp_path)
    monkeypatch.setattr(
        driver, "rodar_pedidos", lambda c, **k: _relato_gate(Motivo.LOTE_VAZIO)
    )

    assert driver.main(["pedir", "--alvo", str(alvo), "--seco"]) == 0


@pytest.mark.parametrize(
    "motivo", [Motivo.GATE_SPEC_APROVADA, Motivo.GATE_CHECKLIST]
)
def test_gate_planejado_sai_com_zero(tmp_path: Path, monkeypatch, motivo):
    # spec:S6
    alvo = _alvo(tmp_path)
    monkeypatch.setattr(driver, "rodar", lambda c, **k: _relato_gate(motivo))

    assert driver.main(["rodar", "--alvo", str(alvo), "--specs", "alfa"]) == 0


@pytest.mark.parametrize(
    "motivo",
    [
        Motivo.DEFEITO_DE_SPEC,
        Motivo.TETO_DE_TENTATIVAS,
        Motivo.FUSIVEL,
        Motivo.FALHA_DE_INVOCACAO,
        Motivo.GUARDA_DO_ALVO,
        Motivo.LOTE_VAZIO,
        Motivo.DEPENDENCIA_CIRCULAR,
    ],
)
def test_excecao_sai_com_nao_zero(tmp_path: Path, monkeypatch, motivo):
    # spec:S7
    alvo = _alvo(tmp_path)
    monkeypatch.setattr(driver, "rodar", lambda c, **k: _relato_gate(motivo))

    assert driver.main(["rodar", "--alvo", str(alvo), "--specs", "alfa"]) != 0


def _relato_gate(motivo: Motivo = Motivo.GATE_CHECKLIST) -> driver.Relato:
    from lote import DecisaoDoLote
    from roteador import Acao, Decisao

    return driver.Relato(DecisaoDoLote(Decisao(Acao.ESCALAR, motivo)), 0, "texto")
