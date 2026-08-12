"""O cadastro de repositórios: markdown que você edita à mão.

Formato deliberadamente pobre — `- <apelido>: <caminho>`, uma linha cada.
"Cadastro alterável" quer dizer que você abre e edita; formato que exige
ferramenta para ser mudado quebra isso, e `sle repo add` é conveniência, não a
única porta.

Por isso a escrita **acrescenta** em vez de reescrever: comentário, ordem e
linha em branco são seus, e ferramenta que os come é ferramenta que você para
de editar à mão.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import casa

ARQUIVO = "repos.md"

_LINHA = re.compile(r"^\s*-\s+(?P<apelido>[^:\s]+)\s*:\s*(?P<caminho>\S.*?)\s*$")


class ApelidoEmUso(Exception):
    pass


class ApelidoDesconhecido(Exception):
    pass


@dataclass(frozen=True)
class Repo:
    apelido: str
    caminho: str


@dataclass(frozen=True)
class Leitura:
    repos: tuple[Repo, ...]
    invalidos: tuple[str, ...]


def caminho_do_cadastro() -> Path:
    return casa.caminho() / ARQUIVO


def ler(texto: str) -> Leitura:
    """Os repositórios na ordem do arquivo, mais as linhas que não servem."""
    aceitos: list[Repo] = []
    recusados: list[str] = []

    for linha in (texto or "").splitlines():
        nua = linha.strip()
        # Comentário e linha em branco não são erro: são o arquivo de alguém.
        if not nua or nua.startswith("#"):
            continue
        encontrada = _LINHA.match(linha)
        if encontrada is None:
            recusados.append(nua)
            continue
        aceitos.append(
            Repo(
                apelido=encontrada.group("apelido"),
                caminho=encontrada.group("caminho"),
            )
        )

    return Leitura(tuple(aceitos), tuple(recusados))


def leitura_atual() -> Leitura:
    """Relê o arquivo agora, com as linhas recusadas junto."""
    arquivo = caminho_do_cadastro()
    if not arquivo.exists():
        return Leitura((), ())
    return ler(arquivo.read_text(encoding="utf-8"))


def carregar() -> tuple[Repo, ...]:
    """Relê o arquivo agora. Nada fica guardado entre chamadas."""
    return leitura_atual().repos


def adicionar(texto: str, apelido: str, caminho: str) -> str:
    ja = {r.apelido: r.caminho for r in ler(texto).repos}
    if apelido in ja:
        raise ApelidoEmUso(f"`{apelido}` já aponta para {ja[apelido]}")

    if not texto:
        return f"- {apelido}: {caminho}\n"

    # Sem `rstrip`: linha em branco no fim é do arquivo de alguém, e comê-la é
    # reescrever o que a pessoa escreveu.
    prefixo = texto if texto.endswith("\n") else f"{texto}\n"
    return f"{prefixo}- {apelido}: {caminho}\n"


def remover(texto: str, apelido: str) -> str:
    linhas = (texto or "").splitlines()
    sobraram = [
        linha
        for linha in linhas
        if not (
            (encontrada := _LINHA.match(linha))
            and encontrada.group("apelido") == apelido
        )
    ]
    if len(sobraram) == len(linhas):
        raise ApelidoDesconhecido(f"`{apelido}` não está no cadastro")

    return "\n".join(sobraram) + "\n"


def resolver(texto: str, valor: str) -> Path:
    """Apelido primeiro, caminho depois — decidido aqui e não por surpresa."""
    for repo in ler(texto).repos:
        if repo.apelido == valor:
            return Path(repo.caminho)
    return Path(valor)


def resolver_cadastrado(valor: str) -> Path:
    """`resolver` contra o cadastro em disco, relido agora."""
    arquivo = caminho_do_cadastro()
    texto = arquivo.read_text(encoding="utf-8") if arquivo.exists() else ""
    return resolver(texto, valor)


def gravar(texto: str) -> None:
    arquivo = caminho_do_cadastro()
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(texto, encoding="utf-8")


def texto_atual() -> str:
    arquivo = caminho_do_cadastro()
    return arquivo.read_text(encoding="utf-8") if arquivo.exists() else ""


def existe(repo: Repo) -> bool:
    return Path(repo.caminho).is_dir()
