"""Semântica de lote — spec: docs/specs/roteador-lote.md (L2, L3, L4, L6, L8, L9)."""

from __future__ import annotations

from lote import EstadoDoLote, SpecDoLote, decidir_lote, spec_do_lote
from roteador import Acao, Fase, Motivo

VERDE = "- **C1** — atendido"
VERMELHO = "- **C1** — não atendido"


def spec(nome, *, depende_de=(), insumo_faltante=(), fechada=False):
    return SpecDoLote(
        nome=nome,
        depende_de=depende_de,
        insumo_faltante=insumo_faltante,
        fechada=fechada,
    )


def apos_verificar(specs, atual, veredito=VERDE, **kwargs):
    return EstadoDoLote(
        specs=tuple(specs),
        fase_concluida=Fase.VERIFICAR,
        spec_atual=atual,
        veredito=veredito,
        **kwargs,
    )


def test_veredito_verde_com_pendentes_vai_para_a_proxima_spec():
    # spec:L2
    d = decidir_lote(apos_verificar([spec("alfa"), spec("beta")], "alfa"))
    assert d.decisao.acao is Acao.INVOCAR
    assert d.decisao.fase is Fase.CODIFICAR
    assert d.proxima_spec == "beta"


def test_a_proxima_spec_respeita_a_ordem_de_dependencia():
    # spec:L2 — gama depende de beta, então beta vem antes mesmo listada depois.
    specs = [spec("alfa"), spec("gama", depende_de=("beta",)), spec("beta")]
    d = decidir_lote(apos_verificar(specs, "alfa"))
    assert d.proxima_spec == "beta"


def test_lote_esgotado_com_algo_fechado_vai_para_homologar():
    # spec:L3
    d = decidir_lote(apos_verificar([spec("alfa", fechada=True), spec("beta")], "beta"))
    assert d.decisao.acao is Acao.INVOCAR
    assert d.decisao.fase is Fase.HOMOLOGAR
    assert d.proxima_spec is None
    assert set(d.fechadas) == {"alfa", "beta"}


def test_spec_sem_insumo_entra_em_quarentena_e_o_lote_segue():
    # spec:L4
    specs = [spec("alfa"), spec("beta", insumo_faltante=("qual banco",)), spec("gama")]
    d = decidir_lote(apos_verificar(specs, "alfa"))
    assert d.decisao.acao is Acao.INVOCAR
    assert d.proxima_spec == "gama"
    assert set(d.quarentena) == {"beta"}


def test_quarentena_arrasta_quem_depende_dela():
    # spec:L4 + L5
    specs = [
        spec("alfa"),
        spec("beta", insumo_faltante=("qual banco",)),
        spec("gama", depende_de=("beta",)),
        spec("delta"),
    ]
    d = decidir_lote(apos_verificar(specs, "alfa"))
    assert set(d.quarentena) == {"beta", "gama"}
    assert d.proxima_spec == "delta"


def test_spec_em_quarentena_nunca_e_invocada():
    # spec:L6
    specs = [spec("alfa"), spec("beta", insumo_faltante=("falta x",))]
    d = decidir_lote(apos_verificar(specs, "alfa"))
    assert d.proxima_spec != "beta"
    assert d.decisao.fase is Fase.HOMOLOGAR


def test_retentativa_de_spec_em_quarentena_nao_acontece():
    # spec:L6 — o núcleo mandaria voltar para codificar; a quarentena vence.
    specs = [spec("alfa", insumo_faltante=("falta x",)), spec("beta")]
    d = decidir_lote(apos_verificar(specs, "alfa", veredito=VERMELHO))
    assert d.proxima_spec == "beta"
    assert d.decisao.fase is Fase.CODIFICAR


def test_ciclo_de_dependencia_escala_em_vez_de_travar():
    # spec:L7
    specs = [spec("alfa", depende_de=("beta",)), spec("beta", depende_de=("alfa",))]
    d = decidir_lote(apos_verificar(specs, "alfa"))
    assert d.decisao.acao is Acao.ESCALAR
    assert d.decisao.motivo is Motivo.DEPENDENCIA_CIRCULAR
    assert set(d.decisao.evidencia) == {"alfa", "beta"}


def test_lote_todo_em_quarentena_escala_e_nunca_homologa():
    # spec:L8 — homologar um ciclo onde nada fechou mede o nada.
    specs = [
        spec("alfa", insumo_faltante=("falta x",)),
        spec("beta", depende_de=("alfa",)),
    ]
    d = decidir_lote(apos_verificar(specs, "alfa"))
    assert d.decisao.acao is Acao.ESCALAR
    assert d.decisao.motivo is Motivo.LOTE_VAZIO
    assert d.decisao.fase is not Fase.HOMOLOGAR


def test_pergunta_em_aberto_na_spec_bloqueia_pelo_markdown():
    # spec:L4 — o gatilho é a seção, lida do texto, não um flag do chamador.
    travada = spec_do_lote(
        "beta",
        "# beta\n\n## Depende de\nNenhuma.\n\n"
        "## Perguntas em aberto\n\n- Qual banco de dados?\n",
    )
    livre = spec_do_lote(
        "gama", "# gama\n\n## Depende de\n`beta`\n\n## Perguntas em aberto\nNenhuma.\n"
    )
    assert travada.insumo_faltante == ("Qual banco de dados?",)
    assert livre.insumo_faltante == ()

    d = decidir_lote(apos_verificar([spec("alfa"), travada, livre], "alfa"))
    # gama declara depender de beta, então cai junto.
    assert set(d.quarentena) == {"beta", "gama"}
    assert d.decisao.fase is Fase.HOMOLOGAR


def test_fechamento_carrega_fechadas_quarentena_e_insumo_faltante():
    # spec:L9
    specs = [
        spec("alfa", fechada=True),
        spec("beta"),
        spec("gama", insumo_faltante=("qual retenção", "qual base legal")),
    ]
    d = decidir_lote(apos_verificar(specs, "beta"))
    assert set(d.fechadas) == {"alfa", "beta"}
    assert set(d.quarentena) == {"gama"}
    assert dict(d.insumos_faltantes) == {
        "gama": ("qual retenção", "qual base legal")
    }


def test_fechamento_diz_por_que_a_arrastada_esta_parada():
    # spec:L9 — spec em quarentena por propagação também precisa de motivo;
    # sem isso o relatório mostra spec parada sem dizer por quê.
    specs = [
        spec("alfa"),
        spec("beta", insumo_faltante=("qual banco",)),
        spec("gama", depende_de=("beta",)),
    ]
    d = decidir_lote(apos_verificar(specs, "alfa"))
    assert dict(d.insumos_faltantes) == {
        "beta": ("qual banco",),
        "gama": ("beta",),
    }


def test_ciclo_nao_reporta_quarentena_nem_insumo():
    # spec:L9 — a saída por ciclo não computa quarentena; as duas listas
    # precisam concordar entre si.
    specs = [spec("alfa", depende_de=("beta",)), spec("beta", depende_de=("alfa",))]
    d = decidir_lote(apos_verificar(specs, "alfa"))
    assert d.quarentena == ()
    assert d.insumos_faltantes == ()


def test_transicoes_do_nucleo_passam_intactas():
    # spec:L2 — o lote intercepta o fim de spec, não o resto da tabela.
    estado = EstadoDoLote(
        specs=(spec("alfa"), spec("beta")),
        fase_concluida=Fase.CODIFICAR,
        spec_atual="alfa",
    )
    d = decidir_lote(estado)
    assert d.decisao.fase is Fase.VERIFICAR
    assert d.proxima_spec == "alfa"
