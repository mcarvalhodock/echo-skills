# Veredito — sle-console

Base: `git diff 7b52a87` (`tooling/loop/console.py` novo, `tooling/loop/driver.py` emendado, `tooling/loop/tests/test_console.py` novo). Suíte do arquivo: 17 passaram.

## Entrar e sair

- **N1** — atendido

`driver.py` registra `subcomandos.add_parser("console")` e, em `main`, `if args.subcomando == "console": return console.rodar()`. `console.rodar` é o laço interativo. `test_o_subcomando_console_entra_no_modo_interativo` prova o despacho.

- **N2** — atendido

`if not args.subcomando and console.e_terminal(): return console.rodar()`, colocado antes do caminho antigo, que permanece intacto para o caso sem terminal. `e_terminal()` exige `isatty()` verdadeiro em `sys.stdin` **e** `sys.stdout`, com `getattr(..., lambda: False)` para stream sem o método. Os três testes cobrem as três metades da regra: abre em terminal, `SystemExit(2)` sem terminal, e a conjunção das duas pontas.

- **N3** — atendido

`sair` retorna 0 explicitamente; `except (EOFError, StopIteration): return 0` cobre o fim de entrada. Ambos testados com asserção sobre o código.

## Trabalhar de dentro

- **N4** — atendido

`rotulo = selecionado or "nenhum repositório"` alimenta o prompt `sle[{rotulo}]> `, recalculado a cada volta do laço. `test_o_prompt_mostra_o_selecionado_ou_a_ausencia` inspeciona os prompts recebidos, não a saída — é o lugar certo de olhar.

- **N5** — atendido

`_selecionar` só aceita apelido presente em `repos.carregar()`; a recusa é `` `{apelido}` não está no cadastro — veja `repo list` ``, que nomeia o que foi procurado. O `or selecionado` na atribuição preserva a seleção anterior em vez de zerá-la, e o laço segue.

- **N6** — atendido

`_despachar` injeta `--alvo selecionado` para `tarefas`, `pedir` e `rodar`. O teste exercita só `rodar` (`vistos == [casa_com_repo]`), mas os três compartilham o mesmo ramo do código, e `test_tarefas_e_o_painel_do_selecionado` exercita o segundo. `pedir` não é exercitado por nenhum teste.

- **N7** — atendido

Mesmo ramo: `if selecionado is None`, escreve "selecione um repositório antes: `usar <apelido>`" e retorna sem chamar nada. `test_sem_selecionado_os_comandos_recusam` assegura a parte forte do critério — `chamados == []`, ou seja, não escolheu por conta.

- **N8** — atendido

Os nomes despachados são literalmente `repo`, `painel`, `pedir`, `rodar`, repassados a `driver.main` sem tradução. `tarefas` é o único mapeamento: `alvo_do_comando = "painel" if comando == "tarefas" else comando`, com o `--alvo` do selecionado — painel do repositório, não uma segunda implementação. Os testes passam, o que confirma que o parser de `painel` aceita `--alvo`.

## Não derrubar a sessão

- **N9** — atendido

`_despachar` termina com `escrever(f"comando desconhecido: {comando} — ...")` e retorna a seleção intacta; o laço continua.

- **N10** — não atendido

A parte de erro dentro de comando está coberta: `except SystemExit` traduz a saída do `argparse` em recusa, e `except Exception` reporta `{tipo}: {mensagem}` — testado com `RuntimeError` e com um comando subsequente que ainda roda.

O que falha é a segunda frase, "nada além de `sair` e do fim de entrada encerra o console". `partes = shlex.split(linha.strip())` está **fora** do `try`, e `shlex.split` levanta `ValueError` em aspas não fechadas. Verificado executando o console com a entrada `usar "api`:

```
DERRUBOU: ValueError No closing quotation
```

A sessão morre com traceback numa entrada digitada trivialmente — sem nenhum teste cobrindo essa linha. Também fora de alcance: `KeyboardInterrupt` (Ctrl-C) é `BaseException`, não é pego por `except Exception`, e portanto encerra o console pela via de exceção não tratada.

- **N11** — atendido

`driver.main(...)` é chamada síncrona dentro do laço: a próxima leitura só acontece depois do retorno, e o console não redireciona `stdin`/`stdout` — os descritores do terminal são herdados por quem `driver.main` chamar, que é o que a segunda cláusula pede.

Ressalva sobre a evidência: `test_a_sessao_espera_o_comando_terminar` é tautológico. O duble `demorado` empilha `"comecou"` e `"terminou"` em sequência, sem concorrência nem ponto de suspensão; a lista `["leu", "leu", "comecou", "terminou", "leu"]` sairia igual se a chamada fosse assíncrona. Quem sustenta o critério é a estrutura do código, não esse teste.

## Não duplicar regra

- **N12** — atendido

Nenhum ramo de `_despachar` reimplementa fase: todos passam por `driver.main`, que é a mesma porta dos subcomandos. `test_o_console_usa_as_mesmas_funcoes_do_subcomando` substitui `driver.rodar` e observa `SUBSTITUIDO` na saída do programa — exatamente a falsificação que o critério nomeia.

- **N13** — atendido

`selecionado` é variável local de `rodar`, sem leitura ou escrita em disco; `_selecionar` só *lê* `repos.carregar()`. O teste roda duas sessões: a segunda começa sem seleção (o comando é recusado), e o diretório da casa contém apenas `repos.md` depois de tudo — cobre as duas metades, "começa sem seleção" e "nada é gravado".

## Nota fora dos critérios

O contrato técnico pede `readline` quando disponível, para histórico e edição de linha. O diff não importa nem menciona `readline`. Não é critério numerado, então não entra em veredito; fica registrado.
