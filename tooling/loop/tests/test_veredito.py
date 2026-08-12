"""Parser do molde do veredito — spec: docs/specs/roteador-nucleo.md (C8-C12)."""

from __future__ import annotations

import pytest

from veredito import Classificacao, classificar

# Trecho com a forma que a leitura limpa realmente produz: classificação em
# negrito, justificativa na mesma linha, e citação de outros critérios dentro
# dela. Foi essa forma que quebrou a primeira versão do parser.
VEREDITO_REAL = """# Veredito — exemplo

Base: `git diff fbc8cbb -- tooling/loop/`. Leitura estática do diff.

## Tabela de transições

- **C1** — **atendido**. `decidir` devolve `Decisao(INVOCAR, fase=VERIFICAR)`.
- **C2** — **atendido**. Mesmo caminho de C1, sem ramo de escalada.

## Leitura do veredito

- **C3** — **não atendido**. A segunda metade de C3 não é exercitada; o teste
  usa outra string. Ver também a ressalva em C1.
"""


def test_classifica_os_tres_estados_no_molde():
    # spec:C8
    texto = (
        "- **C1** — atendido\n"
        "- **C2** — não atendido\n"
        "- **C3** — não verificável\n"
    )
    assert classificar(texto) == {
        "C1": Classificacao.ATENDIDO,
        "C2": Classificacao.NAO_ATENDIDO,
        "C3": Classificacao.NAO_VERIFICAVEL,
    }


def test_enfase_acento_e_caixa_nao_alteram_o_resultado():
    # spec:C8
    texto = (
        "- **C1** — **Atendido**. justificativa qualquer.\n"
        "- **C2** — `NAO ATENDIDO`: falta a validação.\n"
        "- C3 - nao verificavel\n"
    )
    assert classificar(texto) == {
        "C1": Classificacao.ATENDIDO,
        "C2": Classificacao.NAO_ATENDIDO,
        "C3": Classificacao.NAO_VERIFICAVEL,
    }


def test_justificativa_que_cita_criterio_nao_classifica_o_criterio_citado():
    # spec:C9 — regressão do primeiro veredito real: seis falsos não verificável.
    assert classificar(VEREDITO_REAL) == {
        "C1": Classificacao.ATENDIDO,
        "C2": Classificacao.ATENDIDO,
        "C3": Classificacao.NAO_ATENDIDO,
    }


def test_linha_fora_do_molde_e_ignorada():
    # spec:C9
    texto = (
        "| C1 | atendido |\n"
        "O critério C2 foi atendido conforme discutido.\n"
        "- **C3** — atendido\n"
    )
    assert classificar(texto) == {"C3": Classificacao.ATENDIDO}


def test_classificacao_irreconhecivel_vira_nao_verificavel():
    # spec:C10
    texto = "- **C1** — depende do ambiente\n- **C2** — atendido\n"
    assert classificar(texto) == {
        "C1": Classificacao.NAO_VERIFICAVEL,
        "C2": Classificacao.ATENDIDO,
    }


@pytest.mark.parametrize(
    "ambigua",
    ["parcialmente atendido", "atendido em parte", "quase atendido"],
)
def test_entrada_ambigua_nunca_e_lida_como_atendido(ambigua):
    # spec:C11
    assert classificar(f"- **C1** — {ambigua}") == {
        "C1": Classificacao.NAO_VERIFICAVEL
    }


def test_nao_atendido_nunca_e_lido_como_atendido():
    # spec:C11 — "atendido" é sufixo de "não atendido"; a ordem de teste importa.
    assert classificar("- **C1** — não atendido") == {"C1": Classificacao.NAO_ATENDIDO}


def test_identificador_repetido_com_conflito_fica_com_o_pior():
    # spec:C11
    assert classificar("- **C1** — atendido\n- **C1** — não atendido") == {
        "C1": Classificacao.NAO_ATENDIDO
    }
    assert classificar("- **C1** — não atendido\n- **C1** — não verificável") == {
        "C1": Classificacao.NAO_VERIFICAVEL
    }


@pytest.mark.parametrize(
    "texto",
    [None, "", "   \n\n  ", "# Veredito\n\nsem nenhuma linha no molde."],
)
def test_veredito_sem_linha_no_molde_devolve_vazio(texto):
    # spec:C12
    assert classificar(texto) == {}
