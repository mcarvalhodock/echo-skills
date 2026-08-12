"""O que cada repositório espera de você, derivado do disco dele.

O recurso escasso deixou de ser a atenção dentro de um projeto e passou a ser a
atenção **entre** projetos. Por isso a saída não é um relatório de tudo que
aconteceu: é uma fila do que falta você fazer.

Somente-leitura por desenho, não por omissão — é o que permite rodá-lo com um
ciclo em andamento noutro terminal. E sem armazenamento próprio: cache que
diverge do alvo é como uma ferramenta passa a mentir com confiança, agora
sobre N projetos ao mesmo tempo.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import registro
from roteador import Acao, Fase, Motivo

# O que cada parada quer dizer para quem lê a fila. `homologar` não vira
# "pronto": ninguém verificou, e "aguarda checklist" é o mais longe honesto.
_ROTULO_POR_MOTIVO = {
    Motivo.GATE_SPEC_APROVADA.value: "aguarda você: aprovação do lote",
    Motivo.GATE_CHECKLIST.value: "aguarda você: checklist de homologação",
}

_TERMINAL_DE_FECHAMENTO = f"{Acao.INVOCAR.value}:{Fase.HOMOLOGAR.value}"


@dataclass(frozen=True)
class Estado:
    rotulo: str
    detalhe: str = ""


def estado_de(alvo: Path | str) -> Estado:
    """Derivado dos artefatos do alvo, relido agora. Nada é guardado."""
    caminho = Path(alvo)
    if not caminho.is_dir():
        return Estado("inacessível", f"não encontrei {caminho}")

    gravadas = registro.linhas(registro.caminho_do_registro(caminho))
    if not gravadas:
        # Três coisas diferentes: não começou, ocioso, pronto. Só a primeira é
        # afirmável a partir da ausência de registro.
        return Estado("não começou", "sem registro de ciclo")

    ultima = gravadas[-1]
    transicao = ultima.get("transicao", "")
    motivo = ultima.get("motivo", "")

    if transicao == Acao.ESCALAR.value:
        if motivo in _ROTULO_POR_MOTIVO:
            return Estado(_ROTULO_POR_MOTIVO[motivo], ultima.get("spec", ""))
        return Estado("travado", f"{motivo} em `{ultima.get('spec', '—')}`")

    if transicao == _TERMINAL_DE_FECHAMENTO:
        return Estado(
            _ROTULO_POR_MOTIVO[Motivo.GATE_CHECKLIST.value], ultima.get("spec", "")
        )

    fase = transicao.split(":")[-1]
    return Estado("em andamento", f"{fase} em `{ultima.get('spec', '—')}`")


def linha_de(apelido: str, alvo: Path | str) -> str:
    estado = estado_de(alvo)
    sufixo = f" — {estado.detalhe}" if estado.detalhe else ""
    return f"{apelido}: {estado.rotulo}{sufixo}"
