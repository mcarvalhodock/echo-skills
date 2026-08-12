"""Percorre um lote de specs aprovadas de uma vez.

O núcleo decide uma transição por vez e não sabe que existe um lote. Este
módulo intercepta o único ponto em que isso importa — a spec que acabou de
fechar — e devolve a próxima em vez de mandar homologar.

A regra que dá nome ao resto: spec sem insumo é spec bloqueada, não ciclo
bloqueado. Ela entra em quarentena junto com quem depende dela, e as outras
seguem. Parar as cinco por causa de uma transforma problema local em parada
global, e você volta ao terminal para descobrir que nada andou.

Puro, como o núcleo: sem disco, sem relógio.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from dependencia import ciclo_em, em_ordem_de_dependencia, propagar
from roteador import TETO_PADRAO, Acao, Decisao, Estado, Fase, Motivo, decidir
from secoes import declaradas, perguntas_em_aberto


@dataclass(frozen=True)
class SpecDoLote:
    nome: str
    depende_de: tuple[str, ...] = ()
    # Não vazio significa bloqueada. Quem detecta o insumo faltante é
    # `especificar`, que o escreve em "## Perguntas em aberto"; o roteador só
    # lê se há ou não — inferir insumo exigiria ler conteúdo.
    insumo_faltante: tuple[str, ...] = ()
    fechada: bool = False


def spec_do_lote(nome: str, texto_da_spec: str) -> SpecDoLote:
    """Monta a entrada do lote a partir do markdown, lendo só estrutura.

    Pergunta em aberto é o gatilho de bloqueio, e é por isso que escalar por
    preguiça em `especificar` custa caro: a spec não anda, e leva junto quem
    depende dela.
    """
    return SpecDoLote(
        nome=nome,
        depende_de=declaradas(texto_da_spec),
        insumo_faltante=perguntas_em_aberto(texto_da_spec),
    )


@dataclass(frozen=True)
class EstadoDoLote:
    specs: tuple[SpecDoLote, ...]
    fase_concluida: Fase
    spec_atual: str
    veredito: str | None = None
    tentativas: int = 0
    teto: int = TETO_PADRAO
    vereditos: tuple[str, ...] = ()


@dataclass(frozen=True)
class DecisaoDoLote:
    decisao: Decisao
    proxima_spec: str | None = None
    fechadas: tuple[str, ...] = ()
    quarentena: tuple[str, ...] = ()
    insumos_faltantes: tuple[tuple[str, tuple[str, ...]], ...] = field(default=())


def decidir_lote(estado: EstadoDoLote) -> DecisaoDoLote:
    nomes = tuple(spec.nome for spec in estado.specs)
    dependencias = {spec.nome: spec.depende_de for spec in estado.specs}

    ciclo = ciclo_em(dependencias)
    if ciclo:
        # Escalar em vez de travar: um grafo fechado nunca libera uma spec, e
        # o loop ficaria parado sem nada no terminal explicando por quê.
        return _fechar(
            estado,
            Decisao(Acao.ESCALAR, Motivo.DEPENDENCIA_CIRCULAR, evidencia=ciclo),
            quarentena=(),
        )

    bloqueadas = {spec.nome for spec in estado.specs if spec.insumo_faltante}
    quarentena = propagar(bloqueadas, dependencias)

    if quarentena and len(quarentena) == len(nomes):
        return _fechar(
            estado,
            Decisao(Acao.ESCALAR, Motivo.LOTE_VAZIO, evidencia=tuple(sorted(quarentena))),
            quarentena=quarentena,
        )

    base = decidir(
        Estado(
            fase_concluida=estado.fase_concluida,
            spec=estado.spec_atual,
            veredito=estado.veredito,
            tentativas=estado.tentativas,
            teto=estado.teto,
            vereditos=estado.vereditos,
        )
    )

    atual_bloqueada = estado.spec_atual in quarentena
    fecha_a_spec = base.acao is Acao.INVOCAR and base.fase is Fase.HOMOLOGAR

    if not fecha_a_spec and not atual_bloqueada:
        return _fechar(estado, base, quarentena, proxima=estado.spec_atual)

    fechadas = {spec.nome for spec in estado.specs if spec.fechada}
    if fecha_a_spec:
        fechadas.add(estado.spec_atual)

    proxima = _proxima_pendente(nomes, dependencias, fechadas, quarentena)
    if proxima is not None:
        return _fechar(
            estado,
            Decisao(Acao.INVOCAR, Motivo.TRANSICAO, fase=Fase.CODIFICAR),
            quarentena,
            proxima=proxima,
            fechadas=fechadas,
        )

    if not fechadas:
        return _fechar(
            estado,
            Decisao(Acao.ESCALAR, Motivo.LOTE_VAZIO, evidencia=tuple(sorted(quarentena))),
            quarentena,
            fechadas=fechadas,
        )

    return _fechar(
        estado,
        Decisao(Acao.INVOCAR, Motivo.TRANSICAO, fase=Fase.HOMOLOGAR),
        quarentena,
        fechadas=fechadas,
    )


def _proxima_pendente(
    nomes: tuple[str, ...],
    dependencias: dict[str, tuple[str, ...]],
    fechadas: set[str],
    quarentena: frozenset[str],
) -> str | None:
    pendentes = tuple(
        nome for nome in nomes if nome not in fechadas and nome not in quarentena
    )
    if not pendentes:
        return None
    return em_ordem_de_dependencia(pendentes, dependencias)[0]


def _insumos_da_quarentena(
    estado: EstadoDoLote, quarentena
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """O que falta a CADA spec em quarentena, inclusive as arrastadas.

    Quem foi bloqueada na origem lista o insumo declarado; quem entrou por
    propagação lista a spec que a bloqueou — que é, literalmente, o que falta
    a ela. Sem isso o relatório mostra specs paradas sem dizer por quê, que é
    o mesmo que não mostrar.
    """
    return tuple(
        (
            spec.nome,
            spec.insumo_faltante
            or tuple(nome for nome in spec.depende_de if nome in quarentena),
        )
        for spec in estado.specs
        if spec.nome in quarentena
    )


def _fechar(
    estado: EstadoDoLote,
    decisao: Decisao,
    quarentena,
    *,
    proxima: str | None = None,
    fechadas: set[str] | None = None,
) -> DecisaoDoLote:
    if fechadas is None:
        fechadas = {spec.nome for spec in estado.specs if spec.fechada}

    ordem = [spec.nome for spec in estado.specs]
    insumos = _insumos_da_quarentena(estado, quarentena)

    return DecisaoDoLote(
        decisao=decisao,
        proxima_spec=proxima,
        fechadas=tuple(nome for nome in ordem if nome in fechadas),
        quarentena=tuple(nome for nome in ordem if nome in quarentena),
        insumos_faltantes=insumos,
    )
