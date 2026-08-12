"""Resolve o grafo de dependência entre as specs de um lote.

Uma spec pode depender de outra; um critério, não. Este módulo só entende o
primeiro caso: quem é arrastado quando alguém trava, e quando o grafo se fecha
num ciclo que travaria o lote em silêncio. Quem lê a declaração no markdown é
`secoes.py`.

Puro, como o resto da cadeia de decisão: sem disco, sem relógio.
"""

from __future__ import annotations


def propagar(
    bloqueadas: set[str] | frozenset[str],
    dependencias: dict[str, tuple[str, ...]],
) -> frozenset[str]:
    """As bloqueadas mais todas as que dependem delas, transitivamente."""
    if not bloqueadas:
        return frozenset()

    alcancadas = set(bloqueadas)
    mudou = True
    while mudou:
        mudou = False
        for nome, requisitos in dependencias.items():
            if nome in alcancadas:
                continue
            if any(requisito in alcancadas for requisito in requisitos):
                alcancadas.add(nome)
                mudou = True
    return frozenset(alcancadas)


def ciclo_em(dependencias: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
    """Os nomes envolvidos num ciclo, ou vazio. Aresta para fora do lote é ignorada."""
    dentro_do_lote = set(dependencias)
    pendentes = {
        nome: [r for r in requisitos if r in dentro_do_lote]
        for nome, requisitos in dependencias.items()
    }

    # Remove repetidamente quem não depende de mais ninguém. O que sobra só pode
    # estar preso em ciclo — não há terceira possibilidade num grafo finito.
    resolvidos: set[str] = set()
    mudou = True
    while mudou:
        mudou = False
        for nome, requisitos in pendentes.items():
            if nome in resolvidos:
                continue
            if all(requisito in resolvidos for requisito in requisitos):
                resolvidos.add(nome)
                mudou = True

    return tuple(nome for nome in pendentes if nome not in resolvidos)


def em_ordem_de_dependencia(
    nomes: tuple[str, ...], dependencias: dict[str, tuple[str, ...]]
) -> tuple[str, ...]:
    """Ordem topológica estável: dependência antes, e o resto na ordem do lote."""
    ordenados: list[str] = []
    restantes = list(nomes)

    while restantes:
        livre = next(
            (
                nome
                for nome in restantes
                if all(
                    requisito in ordenados or requisito not in nomes
                    for requisito in dependencias.get(nome, ())
                )
            ),
            None,
        )
        if livre is None:  # ciclo — quem chama já checou, mas não travamos aqui
            ordenados.extend(restantes)
            break
        ordenados.append(livre)
        restantes.remove(livre)

    return tuple(ordenados)
