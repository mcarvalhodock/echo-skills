# sle-console — veredito

Lido: `docs/specs/sle-console.md` e `git diff d8a8698 -- tooling/loop`.

- **N1** — atendido
- **N2** — atendido
- **N3** — atendido
- **N4** — atendido
- **N5** — atendido
- **N6** — atendido
- **N7** — atendido
- **N8** — atendido
- **N9** — atendido
- **N10** — atendido
- **N11** — atendido
- **N12** — atendido
- **N13** — atendido

## Porquê

**N1** — `driver.main` registra `subcomandos.add_parser("console", help="modo interativo")` e despacha com `if args.subcomando == "console": return console.rodar()`. Coberto por `test_o_subcomando_console_entra_no_modo_interativo`, que substitui `console.rodar` e afirma que ele foi chamado e que o código é 0.

**N2** — `if not args.subcomando and console.e_terminal(): return console.rodar()`; caindo fora, `analisador.print_help()` seguido de `raise SystemExit(2)`. `console.e_terminal()` exige as duas pontas (`sys.stdin.isatty() and sys.stdout.isatty()`), com `getattr(..., lambda: False)` para objetos de entrada/saída sem `isatty`, como manda o contrato técnico. Três testes fecham o critério: com terminal abre o console, sem terminal `SystemExit.code == 2`, e `test_e_terminal_exige_as_duas_pontas` prova que uma ponta só não basta. A emenda ao `S3` da `loop-cli` está declarada na spec e o caminho sem terminal preserva o código 2.

**N3** — `console.rodar` retorna 0 no ramo `if comando == "sair"` e no `except (EOFError, StopIteration): return 0` — `EOFError` é o Ctrl-D real, `StopIteration` é o fim da entrada roteirizada dos testes. `driver.main` repassa esse retorno nos dois caminhos de entrada (subcomando `console` e `sle` puro em terminal). Testes `test_sair_encerra_com_zero` e `test_fim_de_entrada_encerra_com_zero`.

**N4** — `rotulo = selecionado or "nenhum repositório"` e o prompt é `f"sle[{rotulo}]> "`. `test_o_prompt_mostra_o_selecionado_ou_a_ausencia` captura os prompts das duas leituras e afirma "nenhum" na primeira e "api" na segunda — isto é, o prompt muda depois do `usar`, não só na abertura.

**N5** — `_selecionar` recusa `usar` sem argumento com o uso, e valida o apelido contra `repos.carregar()` (releitura do cadastro em disco). Apelido desconhecido escreve ``` `<apelido>` não está no cadastro — veja `repo list` ```, nomeando o que foi procurado. O retorno `None` é absorvido por `selecionado = _selecionar(...) or selecionado`, então uma recusa não apaga a seleção anterior e o laço continua. Coberto por `test_usar_seleciona_e_apelido_desconhecido_nao_derruba`.

**N6** — `_despachar` injeta a seleção: `driver.main([alvo_do_comando, "--alvo", selecionado, *resto])` para `tarefas`, `pedir` e `rodar`. O apelido chega inteiro ao `driver`, que o converte com `repos.resolver_cadastrado` (apelido primeiro, caminho depois), então o `--alvo` obrigatório de `_comuns` é satisfeito sem o usuário digitá-lo. Dois testes com caminhos distintos: `test_com_selecionado_os_comandos_nao_exigem_alvo` (via `driver.rodar`) e `test_pedir_tambem_usa_o_selecionado` (via `driver.rodar_pedidos`); ambos afirmam que a função de fase recebeu o `Path` do repositório cadastrado.

**N7** — O mesmo ramo começa com `if selecionado is None: escrever("selecione um repositório antes: `usar <apelido>`"); return selecionado` — não há fallback para "primeiro do cadastro" nem para o diretório corrente em lugar nenhum do console. `test_sem_selecionado_os_comandos_recusam` afirma as duas metades: nada foi chamado e a mensagem fala em selecionar.

**N8** — `_despachar` trata `repo`, `painel`, `pedir` e `rodar` pelos mesmos nomes dos subcomandos registrados em `driver.main`, e nenhum deles é reescrito no console. `tarefas` é o painel do selecionado por tradução de nome, não por segunda implementação: `alvo_do_comando = "painel" if comando == "tarefas" else comando`. `test_tarefas_e_o_painel_do_selecionado` e `test_repo_e_painel_funcionam_de_dentro` verificam pela saída real do programa (`capsys`), não pelo escritor da sessão.

**N9** — Ramo final de `_despachar`: `comando desconhecido: {comando} — `ajuda` lista os que existem`, com `return selecionado` — a seleção sobrevive e o laço volta ao topo. `test_comando_desconhecido_nao_derruba` afirma código 0 e o nome inventado na saída.

**N10** — O corpo do laço tem três redes, e as três são necessárias porque `except Exception` sozinho não cobre o que de fato escapa aqui: `SystemExit` (por onde o `argparse` sai tanto no `--help` quanto no argumento ruim — e é `BaseException`), `KeyboardInterrupt` (idem) e `Exception`. O `shlex.split` está dentro do `try`, então aspas não fechadas viram recusa do comando e não fim de sessão. O `KeyboardInterrupt` é tratado nas duas pontas — na leitura do prompt e no despacho —, e o comentário no código registra que tratar só uma deixaria a promessa pela metade. Os códigos de retorno de `driver.main` (1 ou 2) são ignorados de propósito, então comando que falha não encerra. Quatro testes: estouro no meio de `rodar` (com o comando seguinte ainda funcionando, provando que a sessão sobreviveu), aspas abertas, interrupção no despacho e interrupção no prompt.

**N11** — A espera: `_despachar` chama `driver.main(...)` de forma síncrona; não há thread, `Popen` solto nem `&` em lugar nenhum. `test_a_sessao_espera_o_comando_terminar` escolhe o falsificador certo — afirma dentro do `ler` que nenhuma execução está em voo, ou seja, testa a re-entrância, e não apenas a ordem das linhas. O terminal: `rodar_pedidos` passa `interativo=True` a `invocar`, que escolhe `executar_interativo` — um `subprocess.run(list(comando), cwd=...)` sem `capture_output`, sem `stdout`/`stderr`, sem `text`; o filho herda o terminal e a conversa acontece direto com o usuário. O comando interativo padrão é `("claude", "{prompt}")`, sem `-p`. Isso é verificado em `tests/test_interativo.py` (`test_a_sessao_interativa_nao_captura_saida` afirma a ausência de cada kwarg de captura). Observação, não ressalva: para `rodar` a captura permanece, e deve permanecer — o segmento 2 é headless por desenho, e a metade do critério sobre "a sessão interativa do agente" só tem sujeito em `pedir`.

**N12** — O console não chama funções internas do driver: chama `driver.main`, que é a própria porta dos subcomandos. Dentro de `main`, `segmento = rodar_pedidos if args.subcomando == "pedir" else rodar` resolve o nome nos globais do módulo no momento da chamada, então substituir `driver.rodar` alcança o console. `test_o_console_usa_as_mesmas_funcoes_do_subcomando` prova isso pelo efeito observável certo: substitui `driver.rodar` por uma versão que devolve o texto "SUBSTITUIDO" e afirma esse texto na saída do programa depois de um `rodar` digitado no console.

**N13** — `selecionado` é variável local de `console.rodar`, inicializada em `None` a cada entrada; não há `repos.gravar`, nem escrita em `casa`, nem qualquer persistência disparada por `usar` — `_selecionar` só lê. `test_a_selecao_nao_sobrevive_a_sessao` roda duas sessões: na segunda, sem `usar`, o comando é recusado por falta de seleção, e o teste ainda afirma que a pasta da casa contém exatamente `repos.md` — cobre as duas metades do critério, a que expira e a que não grava.

## Nota sobre o alcance do que foi verificado

Os critérios foram lidos contra o código e os testes do diff, não contra uma execução da suíte. Além disso, o diff introduz `prog="sle"` no `ArgumentParser`, mas não contém entry point, wrapper ou instalação que crie um executável chamado `sle`; a forma literal `sle console` de N1 e `sle` puro de N2 dependem disso existir fora de `tooling/loop`, que está fora do recorte pedido. O comportamento que os critérios descrevem — subcomando `console`, ausência de subcomando, regra do terminal — está implementado e coberto sob o nome que o diff expõe (`driver.py`).
