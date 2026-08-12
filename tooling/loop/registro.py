"""Grava em JSONL as decisões que o roteador tomou, dentro do alvo.

O registro existe para auditar o loop, não para narrar o trabalho. Por isso
o conjunto de campos é fechado e todos são de máquina: um campo de texto
livre aqui reabriria a passagem que o método já pagou caro para matar, e
dessa vez ninguém estaria lendo.
"""

from __future__ import annotations

import json
from pathlib import Path

from roteador import Acao, Decisao, Fase

CAMPOS = ("instante", "alvo", "spec", "transicao", "motivo", "evidencia", "tentativa")

_RELATIVO_AO_ALVO = Path(".sle") / "loop.jsonl"

_INVOCACAO_DE_CODIFICAR = f"{Acao.INVOCAR.value}:{Fase.CODIFICAR.value}"


def caminho_do_registro(alvo: str | Path) -> Path:
    """O registro mora no alvo, nunca onde o método está instalado."""
    return Path(alvo) / _RELATIVO_AO_ALVO


def registrar(
    caminho: str | Path,
    *,
    decisao: Decisao,
    instante: str,
    alvo: str | Path,
    spec: str,
) -> dict:
    """Acrescenta uma linha. Os parâmetros são só estes — de propósito."""
    linha = {
        "instante": instante,
        "alvo": str(alvo),
        "spec": spec,
        "transicao": _transicao(decisao),
        "motivo": decisao.motivo.value,
        "evidencia": list(decisao.evidencia),
        "tentativa": decisao.tentativa,
    }

    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(linha, ensure_ascii=False) + "\n")
    return linha


def contar_tentativas(caminho: str | Path, spec: str) -> int:
    """Quantas vezes `codificar` já foi invocada para esta spec."""
    origem = Path(caminho)
    if not origem.exists():
        return 0

    tentativas = 0
    for linha in origem.read_text(encoding="utf-8").splitlines():
        if not linha.strip():
            continue
        decisao = json.loads(linha)
        if (
            decisao.get("spec") == spec
            and decisao.get("transicao") == _INVOCACAO_DE_CODIFICAR
        ):
            tentativas += 1
    return tentativas


def _transicao(decisao: Decisao) -> str:
    if decisao.acao is Acao.INVOCAR and decisao.fase is not None:
        return f"{decisao.acao.value}:{decisao.fase.value}"
    return decisao.acao.value
