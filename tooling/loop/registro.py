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

# O laço não tem mais o que fazer sozinho depois de qualquer uma destas.
# Qualquer outra última linha significa que ele foi cortado no meio — e aí a
# execução seguinte é retomada, não ciclo novo.
_TRANSICOES_TERMINAIS = (
    Acao.ESCALAR.value,
    f"{Acao.INVOCAR.value}:{Fase.HOMOLOGAR.value}",
)


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


def linhas(caminho: str | Path) -> tuple[dict, ...]:
    """As decisões já gravadas, na ordem. Vazio se o registro não existe.

    Linha que não é JSON é pulada em vez de derrubar quem lê: o arquivo é
    append-only e alguém pode estar lendo no exato momento em que a última
    linha está sendo escrita. Quebrar ali faria o painel morrer só porque um
    ciclo estava em andamento noutro terminal.
    """
    origem = Path(caminho)
    if not origem.exists():
        return ()

    lidas = []
    for linha in origem.read_text(encoding="utf-8").splitlines():
        if not linha.strip():
            continue
        try:
            lidas.append(json.loads(linha))
        except json.JSONDecodeError:
            continue
    return tuple(lidas)


def ciclo_encerrado(caminho: str | Path) -> bool:
    """O ciclo anterior chegou ao fim, ou foi cortado no meio?"""
    gravadas = linhas(caminho)
    if not gravadas:
        return False
    return gravadas[-1].get("transicao") in _TRANSICOES_TERMINAIS


def arquivar_se_encerrado(caminho: str | Path) -> Path | None:
    """Guarda o registro do ciclo anterior e devolve o caminho. None se retomada.

    Arquivar em vez de marcar o ciclo dentro da linha: o esquema do registro é
    fechado, e um campo novo ali valeria para sempre em troca de um problema
    que a renomeação resolve sem tocar em nada.
    """
    origem = Path(caminho)
    if not ciclo_encerrado(origem):
        return None

    numero = 1
    while (destino := origem.with_name(f"{origem.stem}-{numero}{origem.suffix}")).exists():
        numero += 1

    origem.rename(destino)
    return destino


def contar_tentativas(caminho: str | Path, spec: str) -> int:
    """Quantas vezes `codificar` já foi invocada para esta spec."""
    return sum(
        1
        for decisao in linhas(caminho)
        if decisao.get("spec") == spec
        and decisao.get("transicao") == _INVOCACAO_DE_CODIFICAR
    )


def _transicao(decisao: Decisao) -> str:
    if decisao.acao is Acao.INVOCAR and decisao.fase is not None:
        return f"{decisao.acao.value}:{decisao.fase.value}"
    return decisao.acao.value
