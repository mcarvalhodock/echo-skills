# loop-especificar

## Intenção
O loop passa a escrever as specs também: dado um arquivo de pedidos, roda `especificar` uma vez por demanda e para no gate com um relatório que dá para triar.

## Depende de
`roteador-driver`, `roteador-driver-invocacao` e `loop-agente` — a invocação, o histórico e o comando configurável. Não depende de `roteador-lote`: aqui não há veredito para classificar nem quarentena a propagar, só uma fila.

## Critérios

**A entrada**

- [ ] **P1** `[miolo]` — O driver lê `<alvo>/pedidos.md` e devolve, na ordem do arquivo, o nome e o texto de cada demanda — um `##` por demanda.
- [ ] **P2** `[miolo]` — Cabeçalho que não é nome de spec válido (`[a-z0-9-]+`) resulta em `escalar` nomeando o cabeçalho recusado. Nenhum nome é derivado, corrigido ou inventado a partir do título.
- [ ] **P3** `[miolo]` — Arquivo de pedidos ausente, vazio, ou sem nenhum `##` resulta em `escalar`. Nunca em fila vazia tratada como sucesso.
- [ ] **P4** `[miolo]` — Pedido cuja spec já existe em `<alvo>/docs/specs/` é pulado sem invocação, e o relatório diz que foi pulado.

**A execução**

- [ ] **P5** `[integração]` — Cada pedido vira uma invocação de `especificar` em processo novo, com o texto do pedido, o nome da spec e o alvo no prompt.
- [ ] **P6** `[plataforma]` — O artefato esperado é `<alvo>/docs/specs/<nome>.md`. Ausência dele resulta em `escalar`, como qualquer falha de invocação.
- [ ] **P7** `[plataforma]` — Spec produzida com sucesso vira um commit com assunto `loop(<nome>): especificar` e trailer `SLE-Loop: <nome>#spec`.
- [ ] **P8** `[miolo]` — Terminada a fila, o driver **para**. Nenhuma entrada leva de `especificar` a `codificar` na mesma execução.

**O relatório do gate**

- [ ] **P9** `[miolo]` — O relatório lista, por spec produzida: quantos critérios ela tem e quais domínios aparecem neles.
- [ ] **P10** `[miolo]` — Spec com `## Perguntas em aberto` não vazia aparece marcada como bloqueada, com as perguntas listadas.
- [ ] **P11** `[miolo]` — Spec que estoura o teto de 15 critérios aparece marcada no relatório. O teto é de `especificar`, e o relatório expõe quando ele foi furado em vez de deixar passar.

## Contrato técnico

- **`pedidos.md` é o único artefato novo**, e mora no alvo. Um `##` por demanda; o texto abaixo do cabeçalho, até o próximo `##`, é o pedido.
- **O cabeçalho É o nome da spec, sem slugificação.** Derivar `cadastro-de-clientes` de `## Cadastro de Clientes` é a classe de mágica que produz arquivo com nome que ninguém esperava — e o driver precisa saber o caminho do artefato **antes** de invocar, para poder cobrar sua existência.
- **Aprovação não é campo, é ato.** Não existe `aprovada: sim` na spec: um campo desses é um lugar onde se mente barato e sem esforço. A aprovação é você rodar o segundo comando, com `--specs`.
- `--pedidos` e `--specs` são mutuamente exclusivos; passar os dois é erro de invocação, recusado antes de qualquer leitura.
- Reusa `invocacao`, `git_alvo` e `registro` como estão. A fila é sequencial e **não passa por `roteador.decidir`**: não há veredito para classificar, e forçar a tabela de transições aqui seria inventar estado.
- O commit usa o mesmo trailer da tentativa de `codificar`, para que uma limpeza posterior ache tudo com uma régua só.
- A contagem de critérios e a leitura de domínios saem de `secoes.py`, que já lê seção de spec.

## Fora de escopo

- **Encadear direto em `codificar`.** Existe um gate humano entre os dois segmentos, e ele é o ponto onde sua atenção mais paga: sua própria experiência diz que a falha residual do método vem de spec incompleta.
- **Emendar spec que já existe.** `P4` pula; reescrever spec sua a partir de um pedido antigo destruiria trabalho revisado.
- **Gerar pedidos a partir de ticket, Jira ou issue.** Cada um tem API própria e nenhum está em uso aqui.
- **Aprovar sozinho, ou marcar spec como aprovada.** É o gate; automatizá-lo esvazia a única parada que sobrou antes do código.
- **Quarentena e dependência entre pedidos.** Isso é de `roteador-lote`, e vale no segundo segmento, sobre as specs já escritas.

## Plano

1. `tooling/loop/secoes.py` — leitura de `## Critérios`: identificadores e domínios (P9, P11).
2. `tooling/loop/pedidos.py` — parser do arquivo e validação do nome (P1, P2, P3).
3. `tooling/loop/driver.py` — a fila, o pulo de spec existente, o commit e o relatório do gate (P4–P11).
4. `tooling/loop/tests/test_pedidos.py` e `test_especificar.py`, com executor falso e alvo temporário.

Sem fatias: `plataforma` e `integração` não fecham sem a fila, e separá-los produziria reconciliação.

## Perguntas em aberto

Nenhuma.
