"""Arquivo de pedidos — spec: docs/specs/loop-especificar.md (P1, P2, P3)."""

from __future__ import annotations

import pedidos

ARQUIVO = """# Pedidos

Texto solto antes do primeiro cabeçalho, que não é pedido de ninguém.

## cadastro

Preciso que o cliente se cadastre com e-mail e senha.
A senha tem regra mínima.

## cobranca

Cobrar mensalmente, e avisar antes.
"""


def test_le_nome_e_texto_na_ordem_do_arquivo():
    # spec:P1
    lidos = pedidos.ler(ARQUIVO)

    assert [p.nome for p in lidos.pedidos] == ["cadastro", "cobranca"]
    assert "e-mail e senha" in lidos.pedidos[0].texto
    assert "regra mínima" in lidos.pedidos[0].texto
    assert "Cobrar mensalmente" in lidos.pedidos[1].texto


def test_texto_antes_do_primeiro_cabecalho_nao_vira_pedido():
    # spec:P1
    lidos = pedidos.ler(ARQUIVO)
    assert all("Texto solto" not in p.texto for p in lidos.pedidos)


def test_o_texto_de_um_pedido_nao_invade_o_seguinte():
    # spec:P1
    lidos = pedidos.ler(ARQUIVO)
    assert "Cobrar" not in lidos.pedidos[0].texto


def test_cabecalho_invalido_e_recusado_e_nao_corrigido():
    # spec:P2 — nada de derivar `cadastro-de-clientes` de `Cadastro de Clientes`.
    lidos = pedidos.ler("## Cadastro de Clientes\n\ntexto\n\n## cobranca\n\ntexto\n")

    assert lidos.invalidos == ("Cadastro de Clientes",)
    assert [p.nome for p in lidos.pedidos] == ["cobranca"]


def test_maiuscula_acento_e_espaco_sao_invalidos():
    # spec:P2
    lidos = pedidos.ler("## Cadastro\n\nx\n\n## cobrança\n\nx\n\n## meu pedido\n\nx\n")
    assert set(lidos.invalidos) == {"Cadastro", "cobrança", "meu pedido"}
    assert lidos.pedidos == ()


def test_nome_com_hifen_e_digito_e_valido():
    # spec:P2
    lidos = pedidos.ler("## cadastro-v2\n\nx\n")
    assert [p.nome for p in lidos.pedidos] == ["cadastro-v2"]
    assert lidos.invalidos == ()


def test_arquivo_vazio_ou_sem_cabecalho_nao_da_fila():
    # spec:P3
    for texto in ("", "   \n\n", "# Pedidos\n\nsó prosa, nenhum cabeçalho de nível 2.\n"):
        lidos = pedidos.ler(texto)
        assert lidos.pedidos == ()
        assert lidos.invalidos == ()


def test_pedido_sem_texto_ainda_e_um_pedido():
    # spec:P1 — cabeçalho sem corpo é pedido vazio, não pedido ausente; quem
    # decide o que fazer com isso é `especificar`, não o parser.
    lidos = pedidos.ler("## cadastro\n\n## cobranca\n\ntexto\n")
    assert [p.nome for p in lidos.pedidos] == ["cadastro", "cobranca"]
    assert lidos.pedidos[0].texto == ""
