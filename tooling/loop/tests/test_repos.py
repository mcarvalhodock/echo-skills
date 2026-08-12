"""O cadastro de repositórios — spec: docs/specs/sle-casa.md (H4-H11)."""

from __future__ import annotations

from pathlib import Path

import pytest

import repos

ARQUIVO = """# Meus repositórios

# o da empresa
- api: /trabalho/api

- site: /trabalho/site
"""


def test_le_apelido_e_caminho_na_ordem(tmp_path: Path):
    # spec:H4
    lidos = repos.ler(ARQUIVO)

    assert [(r.apelido, r.caminho) for r in lidos.repos] == [
        ("api", "/trabalho/api"),
        ("site", "/trabalho/site"),
    ]
    assert lidos.invalidos == ()


def test_linha_fora_do_formato_e_recusada_nomeando_a_linha(tmp_path: Path):
    # spec:H4
    lidos = repos.ler("- api /sem/dois/pontos\n- site: /ok\n")

    assert lidos.invalidos == ("- api /sem/dois/pontos",)
    assert [r.apelido for r in lidos.repos] == ["site"]


def test_add_preserva_comentarios_ordem_e_linhas_em_branco(tmp_path: Path):
    # spec:H5 — ferramenta que reescreve seu arquivo é ferramenta que você
    # para de editar à mão.
    novo = repos.adicionar(ARQUIVO, "extra", "/trabalho/extra")

    assert novo.startswith(ARQUIVO.rstrip("\n"))
    assert "# o da empresa" in novo
    assert novo.rstrip().endswith("- extra: /trabalho/extra")
    assert [r.apelido for r in repos.ler(novo).repos] == ["api", "site", "extra"]


def test_apelido_repetido_e_recusado_nomeando_o_caminho_atual():
    # spec:H6
    with pytest.raises(repos.ApelidoEmUso) as erro:
        repos.adicionar(ARQUIVO, "api", "/outro/lugar")

    assert "/trabalho/api" in str(erro.value)


def test_add_em_arquivo_vazio_funciona():
    # spec:H5
    novo = repos.adicionar("", "api", "/trabalho/api")
    assert [r.apelido for r in repos.ler(novo).repos] == ["api"]


def test_add_preserva_ate_linha_em_branco_no_fim():
    # spec:H5 — `rstrip` comia o fim do arquivo de alguém.
    original = "- api: /um\n\n\n"

    novo = repos.adicionar(original, "site", "/dois")

    assert novo.startswith(original)
    assert novo == original + "- site: /dois\n"


def test_rm_remove_so_aquela_linha():
    # spec:H8
    novo = repos.remover(ARQUIVO, "api")

    assert [r.apelido for r in repos.ler(novo).repos] == ["site"]
    assert "# o da empresa" in novo
    assert "# Meus repositórios" in novo


def test_rm_de_apelido_inexistente_e_recusado():
    # spec:H8
    with pytest.raises(repos.ApelidoDesconhecido) as erro:
        repos.remover(ARQUIVO, "fantasma")

    assert "fantasma" in str(erro.value)


def test_resolver_prefere_apelido_e_cai_para_caminho(tmp_path: Path):
    # spec:H9 — ambiguidade decidida uma vez, por escrito.
    assert repos.resolver(ARQUIVO, "api") == Path("/trabalho/api")
    assert repos.resolver(ARQUIVO, "/um/caminho/qualquer") == Path(
        "/um/caminho/qualquer"
    )


def test_caminho_cadastrado_que_sumiu_nao_impede_nada(tmp_path: Path):
    # spec:H10
    texto = f"- vivo: {tmp_path}\n- morto: {tmp_path / 'nao-existe'}\n"

    lidos = repos.ler(texto)

    assert [r.apelido for r in lidos.repos] == ["vivo", "morto"]
    assert repos.existe(lidos.repos[0]) is True
    assert repos.existe(lidos.repos[1]) is False


def test_o_cadastro_e_relido_a_cada_chamada(tmp_path: Path, monkeypatch):
    # spec:H11 — nada guardado entre execuções além do próprio arquivo.
    monkeypatch.setenv("SLE_CASA", str(tmp_path / "casa"))
    caminho = repos.caminho_do_cadastro()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text("- api: /um\n", encoding="utf-8")

    assert repos.carregar()[0].caminho == "/um"

    caminho.write_text("- api: /dois\n", encoding="utf-8")

    assert repos.carregar()[0].caminho == "/dois"


def test_cadastro_ausente_devolve_lista_vazia(tmp_path: Path, monkeypatch):
    # spec:H11
    monkeypatch.setenv("SLE_CASA", str(tmp_path / "vazia"))
    assert repos.carregar() == ()
