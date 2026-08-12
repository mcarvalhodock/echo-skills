"""Guardas e histórico do alvo.

Duas guardas antes de o loop começar, e um commit por tentativa de
`codificar` depois. Nada aqui sai da máquina e nada reescreve o que já existe:
o loop só acrescenta, e sempre de forma marcada, para que a limpeza posterior
do histórico — humana — encontre o que ele deixou.

Impuro por definição: chama git de verdade.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

BRANCHES_DEFAULT = ("main", "master")

TRAILER = "SLE-Loop"

# A escrituração do próprio loop: `.sle/loop.jsonl` e os arquivados. Ela não
# conta como sujeira nem entra nos commits de tentativa — senão o loop suja o
# alvo ao rodar e a própria guarda impede a execução seguinte. Uma ferramenta
# que se bloqueia na segunda vez está quebrada.
ESCRITURACAO_DO_LOOP = ".sle/loop*.jsonl"

# O mesmo conjunto que o pathspec acima, do lado do Python. Prefixo solto
# (".sle/loop") engoliria `.sle/loop-anotacoes.md`, que é arquivo de alguém —
# e a guarda deixaria de nomear sujeira de verdade.
_E_ESCRITURACAO = re.compile(r"^\.sle/loop[^/]*\.jsonl$")


def _git(alvo: Path | str, *args: str) -> str:
    concluido = subprocess.run(
        ["git", *args],
        cwd=str(alvo),
        capture_output=True,
        text=True,
        check=True,
    )
    return concluido.stdout.strip()


def _tenta_git(alvo: Path | str, *args: str) -> str | None:
    try:
        return _git(alvo, *args)
    except subprocess.CalledProcessError:
        return None


def head(alvo: Path | str) -> str:
    """O SHA atual. É ele que vira ref base antes da primeira tentativa."""
    return _git(alvo, "rev-parse", "HEAD")


def branch_atual(alvo: Path | str) -> str:
    return _git(alvo, "rev-parse", "--abbrev-ref", "HEAD")


def branch_default(alvo: Path | str) -> str | None:
    referencia = _tenta_git(alvo, "symbolic-ref", "refs/remotes/origin/HEAD")
    if referencia:
        return referencia.rsplit("/", 1)[-1]
    # Sem remoto não há verdade a consultar; os dois nomes convencionais são o
    # que sobra, e errar para o lado de recusar é o lado barato.
    atual = branch_atual(alvo)
    return atual if atual in BRANCHES_DEFAULT else None


def sujos(alvo: Path | str) -> tuple[str, ...]:
    # `--untracked-files=all` lista arquivo por arquivo; sem ele, um diretório
    # inteiramente novo vira uma linha só e não dá para separar a escrituração
    # do loop do que é trabalho de quem roda.
    saida = _git(alvo, "status", "--porcelain", "--untracked-files=all")
    # As duas primeiras colunas são o status (índice e working tree); o resto,
    # depois do espaço, é o caminho. Cortar três engole a primeira letra do nome
    # quando o status ocupa as duas colunas.
    caminhos = (linha[2:].strip() for linha in saida.splitlines() if linha.strip())
    return tuple(
        caminho
        for caminho in caminhos
        if not _E_ESCRITURACAO.match(caminho.strip('"').replace("\\", "/"))
    )


def impedimentos(alvo: Path | str) -> tuple[str, ...]:
    """O que impede o ciclo de começar. Vazio significa pode ir."""
    problemas: list[str] = []

    pendentes = sujos(alvo)
    if pendentes:
        # Começar com o alvo sujo faria o primeiro commit do loop varrer
        # mudança que não é dele, e ninguém separaria isso depois.
        problemas.append("working tree sujo: " + ", ".join(pendentes))

    atual = branch_atual(alvo)
    if atual == branch_default(alvo):
        problemas.append(
            f"branch default ({atual}): crie um branch de trabalho antes de rodar"
        )

    return tuple(problemas)


def commitar_tentativa(
    alvo: Path | str, *, spec: str, tentativa: int
) -> str | None:
    """Recolhe tudo que a tentativa mudou num commit marcado. None se nada mudou."""
    _git(alvo, "add", "-A", "--", ".", f":!{ESCRITURACAO_DO_LOOP}")
    if not _git(alvo, "diff", "--cached", "--name-only"):
        return None

    mensagem = (
        f"loop({spec}): codificar tentativa {tentativa}\n"
        f"\n"
        f"{TRAILER}: {spec}#{tentativa}\n"
    )
    _git(alvo, "commit", "-q", "-m", mensagem)
    return head(alvo)
