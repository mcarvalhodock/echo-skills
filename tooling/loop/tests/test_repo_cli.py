"""O subcomando `repo` — spec: docs/specs/sle-casa.md (H2, H7, H8, H9)."""

from __future__ import annotations

from pathlib import Path

import pytest

import driver
import repos


@pytest.fixture
def casa_limpa(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("SLE_CASA", str(tmp_path / "casa"))
    return tmp_path


def test_add_cria_a_casa_e_informa_uma_vez(casa_limpa, capsys):
    # spec:H2
    alvo = casa_limpa / "projeto"
    alvo.mkdir()

    assert driver.main(["repo", "add", "api", str(alvo)]) == 0
    primeira = capsys.readouterr().out

    assert driver.main(["repo", "add", "site", str(alvo)]) == 0
    segunda = capsys.readouterr().out

    assert "casa" in primeira.lower()
    assert "casa" not in segunda.lower()


def test_list_mostra_apelido_caminho_e_se_existe(casa_limpa, capsys):
    # spec:H7
    vivo = casa_limpa / "vivo"
    vivo.mkdir()
    repos.gravar(f"- vivo: {vivo}\n- morto: {casa_limpa / 'sumiu'}\n")

    assert driver.main(["repo", "list"]) == 0
    saida = capsys.readouterr().out

    assert "vivo" in saida and str(vivo) in saida
    assert "morto" in saida
    linha_morto = [l for l in saida.splitlines() if "morto" in l][0]
    assert "ausente" in linha_morto.lower()


def test_linha_fora_do_formato_e_nomeada_para_quem_usa(casa_limpa, capsys):
    # spec:H4 — coletar a linha inválida e não mostrá-la é pior que não
    # coletar: some em silêncio e a pessoa acha que cadastrou.
    repos.gravar("- api: /um\n- torto sem dois pontos\n")

    driver.main(["repo", "list"])
    saida = capsys.readouterr().out

    assert "torto sem dois pontos" in saida
    assert "api" in saida


def test_add_de_apelido_repetido_sai_nao_zero(casa_limpa, capsys):
    # spec:H6
    repos.gravar("- api: /ja/existe\n")

    assert driver.main(["repo", "add", "api", "/outro"]) != 0
    assert "/ja/existe" in capsys.readouterr().out


def test_rm_remove_e_apelido_desconhecido_sai_nao_zero(casa_limpa, capsys):
    # spec:H8
    repos.gravar("- api: /um\n- site: /dois\n")

    assert driver.main(["repo", "rm", "api"]) == 0
    assert [r.apelido for r in repos.carregar()] == ["site"]

    assert driver.main(["repo", "rm", "fantasma"]) != 0
    assert "fantasma" in capsys.readouterr().out


def test_alvo_aceita_apelido_cadastrado(casa_limpa, monkeypatch):
    # spec:H9
    projeto = casa_limpa / "projeto"
    (projeto / "docs" / "specs").mkdir(parents=True)
    repos.gravar(f"- api: {projeto}\n")

    vistos: list[Path] = []
    monkeypatch.setattr(
        driver, "rodar", lambda c, **k: vistos.append(c.alvo) or _relato()
    )

    driver.main(["rodar", "--alvo", "api", "--specs", "alfa"])

    assert vistos == [projeto]


def test_alvo_desconhecido_e_tratado_como_caminho(casa_limpa, monkeypatch):
    # spec:H9
    vistos: list[Path] = []
    monkeypatch.setattr(
        driver, "rodar", lambda c, **k: vistos.append(c.alvo) or _relato()
    )

    driver.main(["rodar", "--alvo", str(casa_limpa / "solto"), "--specs", "alfa"])

    assert vistos == [casa_limpa / "solto"]


def _relato() -> driver.Relato:
    from lote import DecisaoDoLote
    from roteador import Acao, Decisao, Motivo

    return driver.Relato(
        DecisaoDoLote(Decisao(Acao.ESCALAR, Motivo.GATE_CHECKLIST)), 0, ""
    )
