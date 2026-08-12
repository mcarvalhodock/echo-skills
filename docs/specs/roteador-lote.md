# roteador-lote

## Intenção
O loop recebe um lote de specs aprovadas de uma vez e o percorre inteiro: uma spec sem insumo suficiente é bloqueada localmente, não interrompe o ciclo, e leva consigo apenas quem depende dela.

## Depende de
`roteador-nucleo` — a tabela de transições, o parser de veredito e o registro. Esta spec só acrescenta a semântica de lote em cima daquela decisão.

## Critérios

- [ ] **L1** `[miolo]` — O parser lê a seção `## Depende de` de uma spec e devolve os nomes das specs declaradas; `nenhuma` devolve lista vazia.
- [ ] **L2** `[miolo]` — Veredito verde com specs pendentes no lote resulta em `invocar: codificar` na próxima spec pendente. Não escala, e não passa por `especificar`.
- [ ] **L3** `[miolo]` — Lote sem spec pendente e com pelo menos uma spec fechada resulta em `invocar: homologar`.
- [ ] **L4** `[miolo]` — Spec com a seção `## Perguntas em aberto` não vazia entra em quarentena, e o lote segue nas demais. A decisão não escala nesse momento.
- [ ] **L5** `[miolo]` — Spec que declara dependência de uma spec em quarentena entra em quarentena. A propagação é **transitiva**: se C depende de B e B depende de A em quarentena, C também está em quarentena.
- [ ] **L6** `[miolo]` — Spec em quarentena nunca resulta em `invocar: codificar`, em nenhuma entrada.
- [ ] **L7** `[miolo]` — Ciclo de dependência entre specs do lote resulta em `escalar` com motivo `dependencia-circular`. Nunca em laço nem em quarentena silenciosa de todas.
- [ ] **L8** `[miolo]` — Lote com todas as specs em quarentena resulta em `escalar` com motivo `lote-vazio`, **nunca** em `invocar: homologar`. Homologar um ciclo onde nada fechou mede o nada.
- [ ] **L9** `[miolo]` — A decisão que encerra o lote carrega três listas: specs fechadas, specs em quarentena, e o insumo faltante de cada spec em quarentena.

## Contrato técnico

- **O insumo faltante é declarado pela fase que o detectou, não inferido pelo roteador.** `especificar` escreve em `## Perguntas em aberto` qual insumo falta; o roteador só lê se a seção está vazia ou não. Inferir insumo exigiria ler conteúdo, e o roteador é agnóstico ao conteúdo por desenho.
- A ordem de execução do lote respeita a ordem de dependência declarada; entre specs independentes, a ordem é a do lote como aprovado.
- Nada aqui toca disco ou relógio: vale a mesma pureza de `C15` da `roteador-nucleo`.

## Fora de escopo

- **Fusível global de iterações** — é guarda de recurso do driver, não decisão de roteamento, e escala com motivo próprio (`fusível`) para que uma parada por recurso nunca se leia como diagnóstico de convergência.
- **Montar o lote** (descobrir quais specs existem e quais foram aprovadas) — o chamador informa, mesma fronteira da `roteador-nucleo`.
- **Reprocessar quarentena na mesma execução** — spec destravada entra no lote seguinte. Destravar exige insumo novo, e insumo novo vem de você.

## Plano

1. `tooling/loop/dependencia.py` — parser de `## Depende de`, resolução transitiva e detecção de ciclo (L1, L5, L7).
2. `tooling/loop/lote.py` — a semântica de lote sobre a decisão do núcleo (L2, L3, L4, L6, L8, L9).
3. `tooling/loop/tests/test_dependencia.py` e `test_lote.py`.

Sem fatias: L5 e L7 são o mesmo grafo que L2 percorre, e separá-los produziria reconciliação.

## Perguntas em aberto

Nenhuma.
