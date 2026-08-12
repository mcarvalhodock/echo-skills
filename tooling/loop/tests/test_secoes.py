"""Leitura das seções da spec — spec: docs/specs/roteador-lote.md (L1, L4)."""

from __future__ import annotations

import pytest

from secoes import declaradas, perguntas_em_aberto

# As duas formas reais que as specs deste repositório usam hoje. A segunda é a
# armadilha: a seção diz "Nenhuma" e logo em seguida cita outra spec — no
# sentido inverso, "quem depende de mim".
SPEC_COM_DEPENDENCIA = """# roteador-lote

## Depende de
`roteador-nucleo` — a tabela de transições, o parser e o registro.

## Critérios
- [ ] **L1** `[miolo]` — algo

## Perguntas em aberto

Nenhuma.
"""

SPEC_SEM_DEPENDENCIA = """# roteador-nucleo

## Depende de
Nenhuma. `roteador-lote` depende desta.

## Perguntas em aberto
Nenhuma.
"""


def test_le_a_spec_declarada_na_secao():
    # spec:L1
    assert declaradas(SPEC_COM_DEPENDENCIA) == ("roteador-nucleo",)


def test_nenhuma_devolve_lista_vazia_mesmo_citando_outra_spec():
    # spec:L1 — "Nenhuma. `X` depende desta" declara o inverso, não dependência.
    assert declaradas(SPEC_SEM_DEPENDENCIA) == ()


def test_varias_dependencias_preservam_a_ordem():
    # spec:L1
    texto = "## Depende de\n- `alfa`\n- `beta` — motivo\n\n## Critérios\n"
    assert declaradas(texto) == ("alfa", "beta")


def test_spec_sem_a_secao_nao_declara_nada():
    # spec:L1
    assert declaradas("# spec\n\n## Critérios\n- [ ] **C1** `[miolo]` — x\n") == ()


def test_perguntas_em_aberto_lista_os_itens():
    # spec:L4
    texto = (
        "## Perguntas em aberto\n\n"
        "- Qual banco de dados o serviço usa?\n"
        "- Quem aprova a retenção de 90 dias?\n"
    )
    assert perguntas_em_aberto(texto) == (
        "Qual banco de dados o serviço usa?",
        "Quem aprova a retenção de 90 dias?",
    )


def test_prosa_corrida_tambem_conta_como_pergunta_em_aberto():
    # spec:L4 — o gatilho é a seção não estar vazia, não o formato dela.
    texto = "## Perguntas em aberto\n\nNão sei qual mercado isto atende.\n"
    assert perguntas_em_aberto(texto) == ("Não sei qual mercado isto atende.",)


@pytest.mark.parametrize(
    "texto",
    [
        SPEC_COM_DEPENDENCIA,
        "## Perguntas em aberto\n\nNenhuma.\n",
        "## Perguntas em aberto\n\n\n## Plano\n1. x\n",
        "# spec sem a seção\n\n## Critérios\n",
    ],
)
def test_secao_vazia_ou_nenhuma_nao_bloqueia(texto):
    # spec:L4
    assert perguntas_em_aberto(texto) == ()
