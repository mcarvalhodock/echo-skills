"""A casa do `sle` — spec: docs/specs/sle-casa.md (H1, H2, H3)."""

from __future__ import annotations

from pathlib import Path

import casa


def test_a_casa_padrao_e_ponto_sle_no_home(monkeypatch):
    # spec:H1
    monkeypatch.delenv("SLE_CASA", raising=False)
    assert casa.caminho() == Path.home() / ".sle"


def test_a_variavel_de_ambiente_tem_precedencia(tmp_path: Path, monkeypatch):
    # spec:H1
    monkeypatch.setenv("SLE_CASA", str(tmp_path / "outra"))
    assert casa.caminho() == tmp_path / "outra"


def test_casa_ausente_e_criada_e_a_criacao_e_informada(tmp_path: Path, monkeypatch):
    # spec:H2
    destino = tmp_path / "nova"
    monkeypatch.setenv("SLE_CASA", str(destino))
    assert not destino.exists()

    caminho, criada = casa.garantir()

    assert caminho == destino
    assert destino.is_dir()
    assert criada is True


def test_casa_existente_nao_e_reportada_como_criada(tmp_path: Path, monkeypatch):
    # spec:H2 — informar a cada execução treina a pessoa a ignorar.
    monkeypatch.setenv("SLE_CASA", str(tmp_path / "ja-existe"))
    casa.garantir()

    _, criada = casa.garantir()

    assert criada is False


def test_criar_a_casa_nao_toca_em_alvo_nenhum(tmp_path: Path, monkeypatch):
    # spec:H3
    alvo = tmp_path / "projeto"
    (alvo / "docs").mkdir(parents=True)
    (alvo / "docs" / "algo.md").write_text("meu\n", encoding="utf-8")
    antes = sorted(p.relative_to(alvo).as_posix() for p in alvo.rglob("*"))

    monkeypatch.setenv("SLE_CASA", str(tmp_path / "casa"))
    casa.garantir()

    assert sorted(p.relative_to(alvo).as_posix() for p in alvo.rglob("*")) == antes


def test_nada_de_alvo_entra_na_casa(tmp_path: Path, monkeypatch):
    # spec:H3 — a fronteira é nos dois sentidos. Depois de cadastrar um alvo
    # cheio de arquivos, a casa contém só o que é dela.
    import driver

    alvo = tmp_path / "projeto"
    (alvo / "docs" / "specs").mkdir(parents=True)
    (alvo / "docs" / "specs" / "alfa.md").write_text("# alfa\n", encoding="utf-8")
    (alvo / ".sle").mkdir()
    (alvo / ".sle" / "loop.jsonl").write_text("{}\n", encoding="utf-8")

    monkeypatch.setenv("SLE_CASA", str(tmp_path / "casa"))
    driver.main(["repo", "add", "projeto", str(alvo)])

    dentro = sorted(p.name for p in (tmp_path / "casa").rglob("*"))
    assert dentro == ["repos.md"]
