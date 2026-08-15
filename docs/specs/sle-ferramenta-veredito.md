# sle-ferramenta — veredito

Base: `docs/specs/sle-ferramenta.md` contra `git diff 31198b7`
(`tooling/loop/console.py`, `tooling/loop/driver.py`, `tooling/loop/tests/test_ferramenta.py`).
`python -m pytest tests/test_ferramenta.py` em `tooling/loop`: 14 passed.

## Veredito por critério

- **W1** — atendido
- **W2** — atendido
- **W3** — atendido
- **W4** — atendido
- **W5** — atendido
- **W9** — atendido
- **W10** — atendido
- **W6** — atendido
- **W7** — atendido
- **W8** — atendido

## Porquê

**W1** — O subparser `console` em `driver.py` ganhou `--comando` e `--comando-interativo`, e `main` repassa os dois já quebrados em tupla (`tuple(args.comando.split())`) para `console.rodar(comando=…, comando_interativo=…)`. `rodar` semeia com eles o estado `ferramenta` da sessão, que é o que todo despacho lê depois. Os dois ramos são observados, cada um por um teste: `test_o_subcomando_console_repassa_os_comandos` (o repasse do subcomando, headless) e `test_abertura_define_os_comandos_da_sessao` (efeito na invocação de `rodar`); `test_o_interativo_tambem_e_configuravel_na_abertura` cobre o interativo pelo efeito em `driver.rodar_pedidos`. Ressalva: o ramo interativo é exercitado passando `comando_interativo=` direto a `console.rodar`, não pela linha `sle console --comando-interativo …`; o trecho de `driver.py` que faz esse repasse é simétrico ao do headless, mas nenhum teste passa por ele.

**W2** — Sem os argumentos, o `default` do argparse é `" ".join(COMANDO_PADRAO)` e `" ".join(invocacao.COMANDO_INTERATIVO_PADRAO)`, e `rodar` cai nos mesmos constantes quando chamado sem parâmetro (`comando or invocacao.COMANDO_PADRAO`). Os dois caminhos chegam ao mesmo valor, e nenhum default global foi tocado — coerente com a promessa de não emendar o `G2`. `test_sem_argumento_a_sessao_abre_com_o_default` afirma `invocacao.COMANDO_PADRAO` na invocação.

**W3** — `_ferramenta` com `resto` vazio escreve as duas linhas rotuladas, `headless:` e `interativo:`, com os comandos em vigor lidos do estado da sessão (não de constante), e o comando entrou no bloco `AJUDA`. `test_ferramenta_sem_argumento_mostra_os_dois` confere as duas strings do default na saída; `test_nome_troca_os_dois_de_uma_vez` confere que a mesma listagem reflete um estado já trocado — isto é, "em vigor", não "default".

**W4** — Os ramos `--comando` e `--interativo` reescrevem em lugar as posições 0 e 1 da lista `ferramenta`, que vive no escopo do laço de `rodar` e é lida a cada `_despachar`; por construção a troca vale do ponto da troca até o fim da sessão. `test_troca_por_template_vale_nas_invocacoes_seguintes` (headless) e `test_o_interativo_tambem_troca_no_meio_da_sessao` (interativo) fazem uma invocação antes e outra depois, e afirmam a sequência `[default, novo]` — cobrem as duas metades do critério: a seguinte usa o novo, e a anterior não foi afetada retroativamente.

**W5** — O ramo de template chama `invocacao.marcador_ausente(template)`; ausente, escreve `f"template sem o marcador {invocacao.MARCADOR}: …"` — nomeia o marcador que falta, não só recusa — e faz `continue` **sem** atribuir, de modo que a posição segue com o valor anterior. Não existe caminho em `_ferramenta` que limpe o estado, então "nunca fica sem comando" vale também quando as duas chaves vêm na mesma linha e só uma é ruim. `test_template_sem_marcador_e_recusado_e_a_sessao_segue` afirma `MARCADOR` na saída e a invocação seguinte ainda com `COMANDO_PADRAO`.

**W9** — `AGENTES` tem exatamente as duas chaves pedidas, `claude` mapeando para os defaults de `invocacao` e `cursor` para `("agent","-p",MARCADOR)` / `("agent",MARCADOR)` — a mesma expansão declarada no contrato técnico. `ferramenta <nome>` atribui os dois numa tacada (`ferramenta[0], ferramenta[1] = AGENTES[nome]`), e o ramo é escolhido por `not resto[0].startswith("--")`, o que separa nome de template sem ambiguidade para os nomes que existem. `test_nome_troca_os_dois_de_uma_vez` verifica o headless pela invocação e o interativo pela listagem logo depois — os dois lados do "de uma vez". A cláusula "com a mesma economia de `usar <apelido>`" é argumento de forma, não falsificável por teste; o que dá para ler é que a troca custa um token, como o `usar`.

**W10** — Nome fora de `AGENTES` produz `f"agente desconhecido: {nome} — conhecidos: {', '.join(AGENTES)}"` — lista os que existem, e a lista sai do próprio dicionário, então não pode divergir dele — e retorna sem tocar no estado. `test_nome_desconhecido_lista_os_que_existem` afirma o nome errado na saída, os dois conhecidos listados, e a invocação seguinte ainda no default.

**W6** — Em `_despachar`, os argumentos da sessão são montados em `da_sessao` e inseridos **antes** de `*resto` na `argv` passada a `driver.main`, exatamente a ordem que o contrato técnico declara; com o `argparse` guardando a última ocorrência, o que veio digitado na linha vence. A montagem é pulada para `painel`/`tarefas`, que não invocam agente. `test_comando_na_linha_sobrepoe_o_da_sessao` troca para `cursor` e passa `--comando 'outro -p {prompt}'` na chamada, afirmando `("outro","-p","{prompt}")`. A suíte verde também resolve a dependência que o diff sozinho não mostrava: os subparsers `rodar` e `pedir` aceitam os dois argumentos que `da_sessao` sempre anexa — se algum não aceitasse, o `SystemExit` do argparse viraria "argumento inválido" e os testes de `pedir` falhariam.

**W7** — A sobreposição existe só na `argv` daquele despacho; a lista `ferramenta` não é escrita em nenhum ponto do ramo de invocação, então não há o que restaurar — o "volta" é consequência de nunca ter saído. `test_depois_da_chamada_a_sessao_volta_ao_dela` afirma a sequência `[("outro",…), CURSOR_HEADLESS]`: a chamada seguinte, sem argumento, voltou ao comando da sessão.

**W8** — O estado é uma lista local a `rodar`; nenhum caminho de `_ferramenta` lê ou escreve arquivo, e nada no diff persiste a escolha. As duas metades do critério têm teste próprio: `test_a_troca_nao_sobrevive_a_sessao` fecha uma sessão com `cursor`, abre outra e afirma o default; `test_a_troca_nao_escreve_nem_altera_arquivo_nenhum` compara casa e alvo por caminho **e conteúdo** (`read_bytes`) antes e depois, o que pega criação, remoção e alteração — a alteração é a metade que uma comparação só de nomes deixaria passar. Ressalva de escopo: a comparação cobre a casa (`SLE_CASA` do fixture) e a raiz do alvo; escrita fora dessas duas árvores não seria observada, embora o critério só fale delas.

## Limites desta verificação

- Foram lidos apenas a spec e o diff de `31198b7`; o único fato externo usado é o resultado de `pytest tests/test_ferramenta.py`, que passou inteiro. Nenhum outro teste da suíte foi rodado, então regressão em critério de outra spec não está coberta aqui.
- Símbolos usados pelo diff mas definidos fora dele — `invocacao.MARCADOR`, `invocacao.marcador_ausente`, `invocacao.COMANDO_PADRAO`, `COMANDO_PADRAO` sem qualificação em `driver.py` — foram tomados como corretos; a suíte verde é evidência indireta de que existem e se comportam como o diff supõe.
- O contrato técnico já registra que a expansão do nome `cursor` nunca foi exercitada contra o executável real. O diff e os testes exercitam a troca e o que chega ao invocador, não a invocação do `agent`.
