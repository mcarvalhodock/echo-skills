"""Grafo de dependência — spec: docs/specs/roteador-lote.md (L5, L7)."""

from __future__ import annotations

from dependencia import ciclo_em, em_ordem_de_dependencia, propagar


def test_quarentena_propaga_para_quem_depende():
    # spec:L5
    deps = {"a": (), "b": ("a",), "c": ()}
    assert propagar({"a"}, deps) == frozenset({"a", "b"})


def test_quarentena_propaga_transitivamente():
    # spec:L5 — C depende de B, B depende de A, A bloqueada.
    deps = {"a": (), "b": ("a",), "c": ("b",), "d": ()}
    assert propagar({"a"}, deps) == frozenset({"a", "b", "c"})


def test_quarentena_nao_alcanca_ramo_independente():
    # spec:L5
    deps = {"a": (), "b": ("a",), "c": (), "d": ("c",)}
    assert propagar({"a"}, deps) == frozenset({"a", "b"})


def test_sem_bloqueio_nao_ha_quarentena():
    # spec:L5
    assert propagar(set(), {"a": (), "b": ("a",)}) == frozenset()


def test_detecta_ciclo_direto():
    # spec:L7
    assert set(ciclo_em({"a": ("b",), "b": ("a",)})) == {"a", "b"}


def test_detecta_ciclo_indireto():
    # spec:L7
    assert set(ciclo_em({"a": ("b",), "b": ("c",), "c": ("a",)})) == {"a", "b", "c"}


def test_grafo_aciclico_nao_tem_ciclo():
    # spec:L7
    assert ciclo_em({"a": (), "b": ("a",), "c": ("a", "b")}) == ()


def test_dependencia_para_fora_do_lote_nao_e_ciclo():
    # spec:L7 — a spec pode depender de algo que já fechou noutro lote.
    assert ciclo_em({"a": ("externa",)}) == ()


def test_ordem_topologica_estavel():
    # spec:L2 — dependência antes; entre independentes, a ordem do lote.
    deps = {"alfa": (), "gama": ("beta",), "beta": ()}
    assert em_ordem_de_dependencia(("alfa", "gama", "beta"), deps) == (
        "alfa",
        "beta",
        "gama",
    )
