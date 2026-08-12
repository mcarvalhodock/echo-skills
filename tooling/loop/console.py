"""O console: você entra e trabalha de dentro.

Porta de entrada, não regra nova. Todo comando aqui despacha para a mesma
função que o subcomando chama — é o que impede duas portas divergirem no
comportamento, que é o defeito clássico de interface nova.

A seleção de repositório vive só na sessão. Persistir "último usado" seria
estado autorado que ninguém autorou, e reabriria a porta de a ferramenta agir
sobre um alvo que você não escolheu desta vez.
"""

from __future__ import annotations

import shlex
import sys

try:  # histórico e edição de linha quando o sistema oferece
    import readline  # noqa: F401
except ImportError:  # ausência degrada, não bloqueia
    pass

import driver
import repos

AJUDA = """comandos:
  usar <apelido>        seleciona um repositório do cadastro
  tarefas               o que o selecionado espera de você
  painel                o que todos esperam
  repo add|list|rm      cadastro de repositórios
  pedir [--pedidos X]   escreve as specs do selecionado, conversando
  rodar --specs a,b     executa o lote do selecionado
  ajuda                 isto
  sair                  encerra"""


def e_terminal() -> bool:
    """As duas pontas: em CI, só uma delas mente."""
    return bool(
        getattr(sys.stdin, "isatty", lambda: False)()
        and getattr(sys.stdout, "isatty", lambda: False)()
    )


def rodar(*, ler=input, escrever=print) -> int:
    """O laço da sessão. Só `sair` e o fim de entrada encerram."""
    selecionado: str | None = None
    escrever("sle — `ajuda` lista os comandos, `sair` encerra.")

    while True:
        rotulo = selecionado or "nenhum repositório"
        try:
            linha = ler(f"sle[{rotulo}]> ")
        except (EOFError, StopIteration):
            return 0
        except KeyboardInterrupt:
            # Ctrl-C no prompt cancela a linha, igual ao do despacho. Tratar só
            # um dos dois deixa a promessa do critério pela metade.
            escrever("")
            continue

        try:
            # A quebra em palavras entra no `try`: aspas não fechadas levantam
            # ValueError, e uma linha malformada é recusa do comando, não fim
            # da sessão.
            partes = shlex.split(linha.strip())
            if not partes:
                continue
            comando, resto = partes[0], partes[1:]

            if comando == "sair":
                return 0
            if comando == "ajuda":
                escrever(AJUDA)
                continue
            if comando == "usar":
                selecionado = _selecionar(resto, escrever) or selecionado
                continue

            selecionado = _despachar(comando, resto, selecionado, escrever)
        except SystemExit as saida:
            # `argparse` sai por exceção tanto no `--help` quanto no argumento
            # ruim. Rotular os dois de "inválido" seria a ferramenta mentindo
            # sobre o que aconteceu; o que importa é a sessão não morrer.
            if saida.code:
                escrever("argumento inválido para esse comando")
        except KeyboardInterrupt:
            # Ctrl-C cancela a linha, como em qualquer REPL. Só `sair` e o fim
            # de entrada encerram — e `KeyboardInterrupt` não é `Exception`.
            escrever("")
        except Exception as erro:  # a sessão sobrevive a qualquer comando
            escrever(f"{type(erro).__name__}: {erro}")


def _selecionar(resto, escrever) -> str | None:
    if not resto:
        escrever("uso: usar <apelido>")
        return None

    apelido = resto[0]
    if any(r.apelido == apelido for r in repos.carregar()):
        return apelido

    escrever(f"`{apelido}` não está no cadastro — veja `repo list`")
    return None


def _despachar(comando: str, resto, selecionado: str | None, escrever) -> str | None:
    """Cada comando cai na mesma função que o subcomando usaria."""
    if comando == "repo":
        driver.main(["repo", *resto])
        return selecionado

    if comando == "painel":
        driver.main(["painel", *resto])
        return selecionado

    if comando in ("tarefas", "pedir", "rodar"):
        if selecionado is None:
            escrever("selecione um repositório antes: `usar <apelido>`")
            return selecionado
        # `tarefas` é o painel do selecionado — mesma função, não uma segunda
        # implementação. A sessão espera o comando terminar: o loop escreve no
        # repositório, e soltá-lo em paralelo com você digitando no mesmo alvo
        # cria conflito de working tree.
        alvo_do_comando = "painel" if comando == "tarefas" else comando
        driver.main([alvo_do_comando, "--alvo", selecionado, *resto])
        return selecionado

    escrever(f"comando desconhecido: {comando} — `ajuda` lista os que existem")
    return selecionado
