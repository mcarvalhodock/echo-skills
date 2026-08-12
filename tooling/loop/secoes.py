"""Lê as seções de uma spec que o roteador precisa conhecer.

Duas, e só duas: quem esta spec declara como pré-requisito, e se ela tem
pergunta em aberto. Nenhuma das duas interpreta conteúdo — a primeira colhe
nomes, a segunda pergunta se a seção está vazia. É essa pobreza que mantém o
roteador agnóstico ao que a spec diz.

Puro: sem disco, sem relógio.
"""

from __future__ import annotations

import re
import unicodedata

_NOME_EM_CRASE = re.compile(r"`([^`]+)`")

_ITEM = re.compile(r"^\s*[-*+]\s+(.*\S)\s*$", re.MULTILINE)

# `- [ ] **C1** `[miolo, plataforma]` — ...`, com o domínio opcional.
_CRITERIO = re.compile(
    r"^\s*[-*+]\s+(?:\[[ xX]\]\s+)?\*\*([A-Z]\d+)\*\*(?:\s*`\[([^\]]*)\]`)?",
    re.MULTILINE,
)


def _secao(texto_da_spec: str, titulo: str) -> str:
    # A próxima seção é reconhecida por "##" em início de LINHA. Fechar o corpo
    # com "\n##" deixaria o motor recuar e engolir o separador, e a seção vazia
    # passaria a devolver o título da seção seguinte — spec travada por engano.
    padrao = re.compile(
        rf"^##\s+{titulo}[^\n]*\n(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    encontrada = padrao.search(texto_da_spec or "")
    return encontrada.group(1).strip() if encontrada else ""


def _sem_acento(texto: str) -> str:
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def declaradas(texto_da_spec: str) -> tuple[str, ...]:
    """As specs que esta declara como pré-requisito, na ordem em que aparecem."""
    corpo = _secao(texto_da_spec, r"Depende\s+de")
    if not corpo:
        return ()

    # "Nenhuma. `roteador-lote` depende desta." declara o INVERSO — quem depende
    # de mim. Ler a crase ali inverteria a aresta e fabricaria um ciclo.
    if _sem_acento(corpo).lower().startswith("nenhuma"):
        return ()

    return tuple(nome.strip() for nome in _NOME_EM_CRASE.findall(corpo))


def criterios(texto_da_spec: str) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """(identificador, domínios) por critério, na ordem. Estrutura, não conteúdo."""
    lidos = []
    for encontrado in _CRITERIO.finditer(texto_da_spec or ""):
        marcados = encontrado.group(2) or ""
        dominios = tuple(d.strip() for d in marcados.split(",") if d.strip())
        lidos.append((encontrado.group(1), dominios))
    return tuple(lidos)


def perguntas_em_aberto(texto_da_spec: str) -> tuple[str, ...]:
    """Os itens da seção. Vazio significa spec desbloqueada — e é o caso comum."""
    corpo = _secao(texto_da_spec, r"Perguntas\s+em\s+aberto")
    if not corpo:
        return ()

    if _sem_acento(corpo).lower().startswith("nenhuma"):
        return ()

    itens = tuple(item.group(1) for item in _ITEM.finditer(corpo) if item.group(1))
    if itens:
        return itens

    # Seção preenchida em prosa corrida ainda é pergunta em aberto: o gatilho é
    # a seção não estar vazia, e ler menos do que isso destravaria spec travada.
    return (corpo.splitlines()[0].strip(),)
