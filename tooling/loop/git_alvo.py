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
    # `encoding="utf-8"`: o git fala UTF-8, e sem isto o Python decodifica com a
    # codepage do sistema — num Windows pt-BR, `fusível/` volta como `fus?vel/`
    # e o caminho deixa de casar com o do disco.
    # `core.quotePath=false`: sem isto o git devolve `"fus\303\255vel"` com aspas
    # e escapes octais, e o nome precisaria ser desmontado à mão.
    concluido = subprocess.run(
        ["git", "-c", "core.quotePath=false", *args],
        cwd=str(alvo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return concluido.stdout.strip()


def _tenta_git(alvo: Path | str, *args: str) -> str | None:
    try:
        return _git(alvo, *args)
    except subprocess.CalledProcessError:
        return None


def raiz(alvo: Path | str) -> Path | None:
    """A raiz do repositório que contém o alvo, ou None. Única sonda de git.

    Uma chamada só, e quem precisa das duas respostas (é repo? qual subárvore?)
    reaproveita esta: em modo degradado, o loop não pode ficar tateando git.
    """
    saida = _tenta_git(alvo, "rev-parse", "--show-toplevel")
    return Path(saida) if saida else None


def e_repositorio(alvo: Path | str) -> bool:
    return raiz(alvo) is not None


def subarvore(alvo: Path | str, raiz_conhecida: Path | None = None) -> str:
    """O caminho do alvo relativo à raiz do repositório. `.` quando é a raiz.

    O alvo é uma SUBÁRVORE, não um repositório. Num monorepo, tratar os dois
    como a mesma coisa faz a guarda reprovar o trabalho de outro time e a
    leitura limpa julgar a spec contra o diff do repositório inteiro.
    """
    topo = raiz_conhecida or raiz(alvo)
    if topo is None:
        return "."
    relativo = Path(alvo).resolve().relative_to(Path(topo).resolve())
    return relativo.as_posix() or "."


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
    # `-- .` limita à subárvore do alvo. Sem isso, num monorepo, o arquivo que
    # outro time deixou sujo noutro pacote impede este ciclo de começar — e
    # árvore inteiramente limpa é coisa que monorepo quase nunca tem.
    saida = _git(alvo, "status", "--porcelain", "--untracked-files=all", "--", ".")
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
    escopo = ("--", ".", f":!{ESCRITURACAO_DO_LOOP}")

    _git(alvo, "add", "-A", *escopo)
    # A verificação de vazio também é escopada: com algo já no índice fora da
    # subárvore, o índice inteiro pareceria ter conteúdo e o commit sairia por
    # mudança que não é desta demanda.
    if not _git(alvo, "diff", "--cached", "--name-only", *escopo):
        return None

    mensagem = (
        f"loop({spec}): codificar tentativa {tentativa}\n"
        f"\n"
        f"{TRAILER}: {spec}#{tentativa}\n"
    )
    # Com caminhos, e não só `-m`: `git commit` sem pathspec grava o ÍNDICE
    # INTEIRO. Mudança que outro time já tinha deixado staged fora da subárvore
    # entraria num commit rotulado `loop(...)` — e a guarda não a veria, porque
    # ela só olha a subárvore. Cada metade certa, o vão entre as duas.
    _git(alvo, "commit", "-q", "-m", mensagem, *escopo)
    return head(alvo)
