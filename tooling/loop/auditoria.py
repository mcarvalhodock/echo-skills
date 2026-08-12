"""Relê todos os critérios do alvo contra o código que existe agora.

Veredito envelhece. O da primeira spec deste repositório julgou o código de um
commit que dois commits depois já não existia, e ninguém releu — a suíte verde
seguia verde, que é exatamente o sinal em que a invariante 2 manda não
acreditar.

Não é fase nova e não usa skill nenhuma: é o mesmo molde da leitura limpa, na
variante sem diff, emitido uma vez por spec.
"""

from __future__ import annotations

import re
from pathlib import Path

import dependencia
import molde
import secoes
import veredito as leitura

# Sufixos dos arquivos DERIVADOS de uma spec.
#
# Testar isto como substring — ou mesmo como sufixo — descartaria
# `loop-auditoria.md`, que é uma spec de verdade cujo nome termina em
# `-auditoria`: a auditoria deixaria de auditar justamente a spec que a define.
# O discriminador honesto é outro: é derivado quem, tirando o sufixo, sobra o
# nome de uma spec que EXISTE ao lado.
_SUFIXO_DERIVADO = re.compile(r"^(?P<base>.+?)-(veredito(-\d+)?|auditoria|manual-validation)$")


def caminho_da_auditoria(alvo: Path | str, nome: str) -> Path:
    return Path(alvo) / "docs" / "specs" / f"{nome}-auditoria.md"


def auditaveis(alvo: Path | str) -> tuple[str, ...]:
    """Toda spec do alvo, menos as em quarentena.

    Quarentena fica de fora porque a spec não foi construída: cobrar critério
    dela seria reprovar trabalho que ninguém fez.
    """
    pasta = Path(alvo) / "docs" / "specs"
    if not pasta.is_dir():
        return ()

    textos = {
        arquivo.stem: arquivo.read_text(encoding="utf-8")
        for arquivo in sorted(pasta.glob("*.md"))
        if not _e_derivado(arquivo)
    }

    # Quarentena é transitiva no laço, e precisa ser aqui também: spec bloqueada
    # por depender de outra bloqueada também não foi construída.
    bloqueadas = {n for n, t in textos.items() if secoes.perguntas_em_aberto(t)}
    quarentena = dependencia.propagar(
        bloqueadas, {n: secoes.declaradas(t) for n, t in textos.items()}
    )

    return tuple(n for n in textos if n not in quarentena)


def _e_derivado(arquivo: Path) -> bool:
    encontrado = _SUFIXO_DERIVADO.match(arquivo.stem)
    return bool(
        encontrado
        and (arquivo.parent / f"{encontrado.group('base')}.md").exists()
    )


def prompt_de(alvo: Path | str, nome: str, *, escopo: str = ".") -> str:
    """O molde da leitura limpa, na variante sem diff. Nenhuma skill citada."""
    return molde.contra_estado_atual(
        spec=str(Path(alvo) / "docs" / "specs" / f"{nome}.md"),
        escopo=escopo,
        saida=str(caminho_da_auditoria(alvo, nome)),
    )


def regressoes(alvo: Path | str, nome: str) -> tuple[str, ...]:
    """Os critérios que deixaram de estar atendidos. Vazio quando tudo passa."""
    caminho = caminho_da_auditoria(alvo, nome)
    if not caminho.exists():
        # Ausência não é aprovação. O laço já escala por artefato faltando,
        # mas quem chamar isto direto não pode receber "verde" de um arquivo
        # que ninguém escreveu — é o mesmo princípio do parser de veredito.
        return ("(auditoria não produzida)",)

    classificados = leitura.classificar(caminho.read_text(encoding="utf-8"))
    return tuple(
        identificador
        for identificador, classificacao in classificados.items()
        if classificacao is not leitura.Classificacao.ATENDIDO
    )
