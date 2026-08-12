# sle-ferramenta — veredito

Base: `docs/specs/sle-ferramenta.md` contra `git diff 31198b7`
(`tooling/loop/console.py`, `tooling/loop/driver.py`, `tooling/loop/tests/test_ferramenta.py`).

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

**W1** — `driver.py` acrescenta `--comando` e `--comando-interativo` ao subparser `console` e repassa os dois para `console.rodar(comando=…, comando_interativo=…)`, já quebrados em tupla por `split()`. `console.rodar` passou a aceitar os dois parâmetros e semeia com eles o estado `ferramenta` da sessão. Exercitado por `test_abertura_define_os_comandos_da_sessao` (efeito na invocação) e `test_o_subcomando_console_repassa_os_comandos` (repasse do subcomando). Ressalva de cobertura: os dois testes só usam `--comando`; o caminho de `--comando-interativo` é simétrico no código, mas nenhum teste o observa.

**W2** — Sem os argumentos, `rodar` cai em `invocacao.COMANDO_PADRAO` / `invocacao.COMANDO_INTERATIVO_PADRAO`, e `driver.py` usa os mesmos valores como `default` do argparse — o default global não foi tocado, coerente com o contrato de não emendar o `G2`. `test_sem_argumento_a_sessao_abre_com_o_default` afirma exatamente `invocacao.COMANDO_PADRAO` na invocação.

**W3** — `_ferramenta` com `resto` vazio imprime as duas linhas rotuladas (`headless:` e `interativo:`), e o comando aparece no `AJUDA`. `test_ferramenta_sem_argumento_mostra_os_dois` confere as duas strings do default na saída.

**W4** — `ferramenta --comando` / `--interativo` reescrevem em lugar as posições 0 e 1 da lista `ferramenta`, que vive no escopo do laço e é lida a cada despacho; por isso a troca vale para o resto da sessão. `test_troca_por_template_vale_nas_invocacoes_seguintes` faz uma invocação antes e outra depois da troca e afirma a sequência `[default, cursor]` — verifica o "vale nas seguintes" e, de quebra, que a anterior não foi afetada retroativamente. Mesma ressalva de W1: só o ramo `--comando` é observado.

**W5** — O ramo de template chama `invocacao.marcador_ausente(template)`; ausente, escreve `f"template sem o marcador {invocacao.MARCADOR}: …"` — nomeia o marcador que falta — e faz `continue` **sem** atribuir, de modo que a posição correspondente segue com o valor anterior. `test_template_sem_marcador_e_recusado_e_a_sessao_segue` cobre os dois lados: `MARCADOR` presente na saída e a invocação seguinte ainda com `COMANDO_PADRAO`.

**W9** — `AGENTES` tem exatamente as duas chaves pedidas, `claude` mapeando para os defaults de `invocacao` e `cursor` para `("agent","-p",MARCADOR)` / `("agent",MARCADOR)`, e `ferramenta <nome>` atribui os dois de uma vez (`ferramenta[0], ferramenta[1] = AGENTES[nome]`). Casa com a expansão declarada no contrato técnico. `test_nome_troca_os_dois_de_uma_vez` verifica o headless via invocação e o interativo via `ferramenta` sem argumento logo depois — os dois lados do "de uma vez". A "mesma economia de `usar <apelido>`" é um argumento de forma, não falsificável por teste; o que dá para ler é que a troca é um token só, como o `usar`.

**W10** — Nome fora de `AGENTES` produz `f"agente desconhecido: {nome} — conhecidos: {', '.join(AGENTES)}"` e retorna sem tocar no estado. `test_nome_desconhecido_lista_os_que_existem` afirma o nome errado na saída, os dois conhecidos listados, e que a invocação seguinte ainda usa o default — a sessão seguiu com o anterior.

**W6** — No `_despachar`, os argumentos da sessão são montados em `da_sessao` e inseridos **antes** de `*resto`, exatamente a ordem que o contrato técnico declara; com `argparse` guardando a última ocorrência, o que veio na linha vence. `test_comando_na_linha_sobrepoe_o_da_sessao` troca para `cursor` e passa `--comando 'outro -p {prompt}'` na chamada, afirmando `("outro","-p","{prompt}")` — a chamada sobrepôs a sessão.

**W7** — A sobreposição só existe na lista `argv` daquele despacho; a lista `ferramenta` não é escrita no ramo de invocação, então nada precisa ser restaurado. `test_depois_da_chamada_a_sessao_volta_ao_dela` afirma a sequência `[("outro",…), CURSOR_HEADLESS]` — a chamada seguinte voltou ao comando da sessão.

**W8** — O estado é uma lista local a `rodar`, sem leitura ou escrita de arquivo em nenhum dos caminhos de `_ferramenta`; nada no diff persiste a escolha. `test_a_troca_nao_sobrevive_a_sessao` fecha uma sessão com `cursor` e abre outra, afirmando o default. `test_a_troca_nao_escreve_arquivo_nenhum` compara o conteúdo da casa e do alvo antes e depois. Ressalva de cobertura: essa segunda comparação usa só `p.name` (casa) e `p.as_posix()` (alvo) — ela pega criação e remoção, mas não pegaria um arquivo existente **alterado**, que é a outra metade do que W8 diz. O código sustenta a metade não coberta, o teste não.

## Limites desta verificação

- Só a spec e o diff de `31198b7` foram lidos; nenhum teste foi executado. Os vereditos descrevem o que o código e as asserções afirmam, não uma suíte verde observada.
- Símbolos usados pelo diff mas definidos fora dele — `invocacao.MARCADOR`, `invocacao.marcador_ausente`, `invocacao.COMANDO_PADRAO`, `COMANDO_PADRAO` sem qualificação em `driver.py`, os argumentos `--comando`/`--comando-interativo` do subparser `rodar` e o tokenizador da linha do console (que precisa preservar `'agent -p {prompt}'` como um token só) — foram tomados como presentes e corretos. W1, W5, W6 e W7 dependem disso.
- O contrato técnico registra que a expansão real do nome `cursor` nunca foi exercitada contra o executável; o diff exercita a troca, não a invocação do `agent`.
