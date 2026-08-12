"""Compara a skill que o agente vai rodar com a que está no clone do método.

Avisa, não trava. Divergência é informação: travar obrigaria a reinstalar a
cada linha editada numa skill, e o loop passaria a atrapalhar exatamente quem
está desenvolvendo o método. As guardas que travam protegem o repositório de
quem roda; esta protege quem lê o resultado, e um aviso basta.

Existe porque já aconteceu: um ciclo inteiro rodou com as skills instaladas
numa versão anterior à do clone, e ninguém percebeu até o fim.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

SKILLS = ("especificar", "codificar", "verificar", "homologar")

_CASA = Path.home() / ".claude" / "skills"


def _hash(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def _instalada(nome: str, alvo: Path, global_: Path) -> Path | None:
    """Local antes de global: é a local que o agente vai usar."""
    for raiz in (Path(alvo) / ".claude" / "skills", global_):
        caminho = raiz / nome / "SKILL.md"
        if caminho.exists():
            return caminho
    return None


def divergencias(
    alvo: Path | str,
    *,
    metodo: Path | str,
    global_: Path | str | None = None,
) -> tuple[str, ...]:
    """Uma linha por skill que não confere. Vazio quando todas conferem."""
    global_ = Path(global_) if global_ is not None else _CASA
    avisos: list[str] = []

    for nome in SKILLS:
        no_clone = Path(metodo) / nome / "SKILL.md"
        if not no_clone.exists():
            continue

        instalada = _instalada(nome, Path(alvo), global_)
        if instalada is None:
            avisos.append(f"skill `{nome}` ausente na instalação")
            # Compara conteúdo, nunca data: data de arquivo mente depois de um
            # `git checkout`, e mentiria justamente para o lado tranquilizador.
        elif _hash(instalada) != _hash(no_clone):
            avisos.append(f"skill `{nome}` instalada difere da do clone ({instalada})")

    return tuple(avisos)
