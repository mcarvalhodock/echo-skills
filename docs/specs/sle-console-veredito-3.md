# Veredito — sle-console

Contra `git diff d8a8698 -- tooling/loop`.

- **N1** — atendido
- **N2** — atendido
- **N3** — atendido
- **N4** — atendido
- **N5** — atendido
- **N6** — atendido
- **N7** — atendido
- **N8** — atendido
- **N9** — atendido
- **N10** — não atendido
- **N11** — atendido
- **N12** — atendido
- **N13** — atendido

## Por quê

**N1** — `driver.main` ganhou `subcomandos.add_parser("console", ...)` e o ramo
`if args.subcomando == "console": return console.rodar()`. `console.rodar` é o laço
de leitura, com `ler=input`/`escrever=print` por padrão. `test_o_subcomando_console_entra_no_modo_interativo`
amarra o despacho.

**N2** — `if not args.subcomando and console.e_terminal(): return console.rodar()`,
e logo abaixo `if not args.subcomando: analisador.print_help(); raise SystemExit(2)`.
`e_terminal()` testa `isatty()` **nas duas pontas**, `sys.stdin` e `sys.stdout`, com
`getattr(..., lambda: False)` para objeto de entrada que não tem o método. Os três
testes cobrem os três caminhos: terminal abre console, não-terminal sai 2 com ajuda,
e uma ponta sozinha não basta.

**N3** — `if comando == "sair": return 0` e `except (EOFError, StopIteration): return 0`
em volta da leitura. `driver.main` devolve esse mesmo inteiro.

**N4** — o prompt é montado a cada volta: `rotulo = selecionado or "nenhum repositório"`,
`ler(f"sle[{rotulo}]> ")`. O teste inspeciona os prompts efetivamente passados ao leitor,
não a saída — que é a única forma honesta de verificar um prompt.

**N5** — `_selecionar` confere o apelido contra `repos.carregar()` e, quando não acha,
escreve ``` `<apelido>` não está no cadastro — veja `repo list` ``` — nomeando o que foi
procurado — e devolve `None`, que o `or selecionado` transforma em "nada mudou". O laço
segue para a próxima linha.

**N6** — `_despachar` injeta `"--alvo", selecionado` na chamada de `pedir`, `rodar` e
`tarefas`, e `driver.main` resolve o apelido por `repos.resolver_cadastrado`. Testado
para `rodar` e para `pedir` (comparando `config.alvo` com o caminho real do repositório
cadastrado); `tarefas` cai no mesmo ramo.

**N7** — o mesmo ramo começa com `if selecionado is None: escrever("selecione um
repositório antes: `usar <apelido>`"); return selecionado`. O teste checa as duas metades
do critério: a recusa é dita **e** `driver.rodar` não foi chamado — ou seja, não houve
escolha por conta própria.

**N8** — os nomes batem: `repo` e `painel` repassam `driver.main([comando, *resto])` sem
mais nada, `pedir` e `rodar` repassam com o alvo, e `tarefas` vira `painel --alvo <selecionado>`
(`alvo_do_comando = "painel" if comando == "tarefas" else comando`) — o painel do
selecionado, sem segunda implementação.

**N9** — a última linha de `_despachar` é `escrever(f"comando desconhecido: {comando} —
`ajuda` lista os que existem")` e devolve a seleção intacta; o laço continua.

**N10** — a primeira metade está atendida: o `try` em volta do despacho pega `SystemExit`
(por onde `argparse` sai tanto no `--help` quanto no argumento ruim), `KeyboardInterrupt`
levantado *dentro* de um comando, e `Exception` genérica, escrevendo `tipo: mensagem` e
seguindo. O `shlex.split` está dentro do `try`, então aspas abertas viram recusa da linha,
não fim de sessão. O que falha é a segunda frase — "Nada além de `sair` e do fim de entrada
encerra o console". A chamada de leitura tem `try` próprio, e ele só captura
`(EOFError, StopIteration)`. Ctrl-C **no prompt**, enquanto o console espera a linha,
levanta `KeyboardInterrupt` dentro de `ler(...)`, fora do alcance do tratamento de dentro
do despacho, e propaga para fora de `console.rodar` — a sessão morre por algo que não é
`sair` nem fim de entrada. A assimetria é visível no próprio código: `KeyboardInterrupt`
foi tratado deliberadamente no despacho, com comentário de REPL, e não na leitura. Nenhum
teste exercita Ctrl-C no prompt; os dois que mencionam interrupção o levantam de dentro de
`driver.rodar`.

**N11** — `_despachar` chama `driver.main([...])` de forma síncrona; a próxima iteração do
`while` só acontece depois do retorno. O teste falsifica pela re-entrância: o leitor afirma
`not em_execucao[0]` a cada linha, então uma chamada solta em paralelo reprovaria. O terminal
chegar à sessão do agente vem do outro lado: `pedir` roda `invocar(..., interativo=True,
template=config.comando_interativo)`, e `invocacao.executar_interativo` faz
`subprocess.run(comando, cwd=...)` **sem capturar** stdout/stderr — o processo filho herda o
terminal. `rodar` (segmento 2) segue headless por desenho da própria spec.

**N12** — nenhum comando do console tem lógica: todos passam por `driver.main`, que resolve
`segmento = rodar_pedidos if args.subcomando == "pedir" else rodar` por busca de nome global
no momento da chamada. Trocar `driver.rodar` portanto muda o console, e é exatamente isso
que `test_o_console_usa_as_mesmas_funcoes_do_subcomando` afirma, conferindo que o texto
"SUBSTITUIDO" do dublê sai pela saída do programa. `repo`, `painel` e `tarefas` idem.

**N13** — `selecionado` é variável local do laço de `rodar`; não há leitura nem escrita de
arquivo por causa dela, e `_selecionar` só lê o cadastro. Nova chamada a `console.rodar`
começa em `None`. O teste roda uma sessão que seleciona, roda outra do zero conferindo que
os comandos recusam por falta de seleção, e ainda verifica que a casa contém apenas
`repos.md` — nada foi gravado.
