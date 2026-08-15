# sle-console — veredito

Base: `docs/specs/sle-console.md` contra `git diff 7b52a87` (`tooling/loop/console.py`, `tooling/loop/driver.py`, `tooling/loop/tests/test_console.py`). Julgado pelo que o diff mostra; o que depende de código fora do diff está marcado como tal.

## Entrar e sair

- **N1** — atendido

`driver.main` ganhou `subcomandos.add_parser("console", ...)` e, antes do encadeamento de subcomandos, `if args.subcomando == "console": return console.rodar()`. `console.rodar` é o laço de leitura, com `ler=input` por padrão. `test_o_subcomando_console_entra_no_modo_interativo` substitui `console.rodar` e verifica que `driver.main(["console"])` cai nele e devolve 0.

- **N2** — atendido

`if not args.subcomando and console.e_terminal(): return console.rodar()`. `e_terminal()` só é verdadeiro com `isatty()` verdadeiro em `sys.stdin` **e** `sys.stdout`, como o contrato técnico pede. Sem terminal, o fluxo cai no encadeamento antigo — `test_sle_puro_sem_terminal_mantem_ajuda_e_saida_dois` prende `SystemExit` e afere `code == 2`, isto é, a emenda ao `S3` está aplicada exatamente na fronteira declarada. `test_e_terminal_exige_as_duas_pontas` exercita as duas pontas separadamente.

- **N3** — atendido

`sair` retorna 0 no topo do despacho. `EOFError` na chamada de `ler` retorna 0. Dois testes, um para cada porta (`test_sair_encerra_com_zero`, `test_fim_de_entrada_encerra_com_zero`). O `StopIteration` capturado junto é artifício do dublê de entrada dos testes, não caminho de produção — `input()` não levanta `StopIteration`.

## Trabalhar de dentro

- **N4** — atendido

`rotulo = selecionado or "nenhum repositório"` e o prompt `f"sle[{rotulo}]> "` são recalculados a cada volta do laço. `test_o_prompt_mostra_o_selecionado_ou_a_ausencia` captura os prompts e confere "nenhum" antes e "api" depois de `usar api`.

- **N5** — atendido

`_selecionar` valida o apelido contra `repos.carregar()` e, quando não acha, escreve ``` `<apelido>` não está no cadastro — veja `repo list` ``` — nomeia o que foi procurado. Devolve `None`, e o chamador faz `selecionado = _selecionar(...) or selecionado`: a seleção anterior é preservada e o laço continua. `test_usar_seleciona_e_apelido_desconhecido_nao_derruba` cobre o par.

- **N6** — atendido

`_despachar` injeta `--alvo selecionado` para `pedir`, `rodar` e `tarefas`. Testado para `rodar` (`test_com_selecionado_os_comandos_nao_exigem_alvo`) e para `pedir` (`test_pedir_tambem_usa_o_selecionado`), ambos afirmando que a `config` recebida pela função de fase carrega o caminho resolvido do repositório; `tarefas` cai no mesmo ramo e é exercitado em `test_tarefas_e_o_painel_do_selecionado`. A resolução apelido→caminho é código anterior ao diff, mas os testes afirmam o resultado resolvido, o que fecha o critério.

- **N7** — atendido

No mesmo ramo, `if selecionado is None:` escreve "selecione um repositório antes: `usar <apelido>`" e retorna sem despachar. `test_sem_selecionado_os_comandos_recusam` prova as duas metades: a função de fase não é chamada (`chamados == []`) e a mensagem sai. Não há nenhum caminho no arquivo que escolha um repositório sozinho — a única escrita em `selecionado` vem de `usar`.

- **N8** — atendido

`repo`, `painel`, `pedir` e `rodar` são despachados por `driver.main([<mesmo nome>, ...])` — os nomes são literalmente os dos subcomandos. `tarefas` é traduzido para `painel` com `--alvo selecionado` (`alvo_do_comando = "painel" if comando == "tarefas" else comando`), sem segunda implementação. `test_repo_e_painel_funcionam_de_dentro` e `test_tarefas_e_o_painel_do_selecionado` cobrem. Ressalva de escopo: o diff não mostra o corpo do parser `painel`, então o suporte a `--alvo` nele é herdado de `sle-painel`, não estabelecido aqui.

## Não derrubar a sessão

- **N9** — atendido

Queda final de `_despachar`: "comando desconhecido: {comando} — `ajuda` lista os que existem", com `return selecionado` — o laço continua. `test_comando_desconhecido_nao_derruba` confere a mensagem e o código 0 no `sair` seguinte.

- **N10** — atendido

O corpo do laço tem três capturas: `SystemExit` (a saída por exceção do `argparse` quando o argumento não presta), `KeyboardInterrupt` (que não é `Exception` e escaparia), e `Exception` genérica, que imprime `tipo: mensagem`. A quebra em palavras por `shlex.split` está **dentro** do `try`, então aspas não fechadas viram recusa do comando e não fim de sessão — há teste dedicado (`test_linha_com_aspas_abertas_nao_derruba`). `test_erro_dentro_de_um_comando_nao_derruba` ainda verifica que o comando **seguinte** executou, que é a prova real da sobrevivência, não só o código de saída. As únicas saídas do laço continuam sendo `sair` e o fim de entrada. Observação sem efeito no critério: um `SystemExit(0)` legítimo (por exemplo `repo --help`) é rotulado como "argumento inválido"; a mensagem mente, mas a sessão sobrevive, que é o que o critério cobra.

- **N11** — não verificável

A primeira metade está atendida: a chamada a `driver.main` é síncrona, não há thread, subprocesso solto nem `await`, e `test_a_sessao_espera_o_comando_terminar` falsifica a re-entrância — o leitor de linha levanta se for chamado com o comando em voo. A segunda metade — "a sessão interativa do agente recebe o terminal enquanto isso" — não é decidível por este diff: quem entrega (ou captura) stdin/stdout do agente é `driver.rodar`/`rodar_pedidos`, cujo código não aparece aqui, e todos os testes substituem essas funções por dublês. Nenhum teste do lote exercita o terminal chegando ao agente, e nada em `console.py` o repassa explicitamente — ele depende de herança de descritores que o diff não mostra.

## Não duplicar regra

- **N12** — atendido

`_despachar` não chama nenhuma lógica própria: todo comando entra por `driver.main`, o mesmo ponto que a linha de comando usa. `test_o_console_usa_as_mesmas_funcoes_do_subcomando` é o falsificador literal do critério — substitui `driver.rodar` e vê o efeito na saída produzida de dentro do console.

- **N13** — atendido

`selecionado` é variável local de `rodar`, e não há escrita em disco em nenhum caminho da seleção. `test_a_selecao_nao_sobrevive_a_sessao` fecha as duas metades: uma segunda sessão recusa `rodar` por falta de seleção, e o diretório do cadastro contém apenas `repos.md` — nada foi gravado por causa dela.

## Nota de leitura

`console.py` importa `painel` sem usá-lo — o despacho de `tarefas` vai por `driver.main`. Não afeta nenhum critério; registrado por ser a única coisa no diff que não é exigida por nenhum deles.
