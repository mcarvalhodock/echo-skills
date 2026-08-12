# roteador-lote — veredito

Base: `docs/specs/roteador-lote.md` contra `git diff 95a7479 -- tooling/loop/`.
Suíte de `tooling/loop/tests` executada: 66 passed.

- **L1** — atendido
- **L2** — atendido
- **L3** — atendido
- **L4** — atendido
- **L5** — atendido
- **L6** — atendido
- **L7** — atendido
- **L8** — atendido
- **L9** — atendido

## Porquê

**L1** — `secoes.declaradas` recorta a seção por `^##\s+Depende\s+de` e colhe os nomes entre crases na ordem em que aparecem; corpo que começa por "nenhuma" (com normalização de acento) devolve `()`, e seção ausente também. O plano previa esse parser em `dependencia.py` e ele foi para `secoes.py` — mudança de arquivo, não de comportamento; o critério fala do parser, não do módulo. Coberto por `tests/test_secoes.py`, inclusive o caso invertido "Nenhuma. `roteador-lote` depende desta", que declara quem depende de mim e não uma aresta.

**L2** — Em `lote.decidir_lote`, a decisão do núcleo é consultada primeiro; quando ela é `INVOCAR/HOMOLOGAR` (a spec fechou) e existe pendente, o retorno é `Decisao(INVOCAR, TRANSICAO, fase=CODIFICAR)` com `proxima_spec` preenchida. Não há caminho para `ESCALAR` nem para `Fase.ESPECIFICAR` nesse ramo. A pendente é a primeira de `em_ordem_de_dependencia`, o que satisfaz também a cláusula de ordem do contrato técnico. `test_veredito_verde_com_pendentes_vai_para_a_proxima_spec` e `test_a_proxima_spec_respeita_a_ordem_de_dependencia`.

**L3** — Sem pendente (`_proxima_pendente` devolve `None`) e com `fechadas` não vazio, o retorno é `INVOCAR/HOMOLOGAR` com `proxima_spec is None`. A spec que acabou de fechar é somada a `fechadas` antes da checagem, então o último verde do lote conta. `test_lote_esgotado_com_algo_fechado_vai_para_homologar`.

**L4** — `spec_do_lote` deriva `insumo_faltante` de `secoes.perguntas_em_aberto`; seção não vazia (lista de itens ou prosa corrida) produz tupla não vazia, "Nenhuma" e seção vazia produzem `()`. Quem tem insumo faltante entra em `bloqueadas` e daí em `quarentena`, e o fluxo segue para a próxima pendente em vez de escalar — só escala se a quarentena engolir o lote inteiro (L8). `test_spec_sem_insumo_entra_em_quarentena_e_o_lote_segue` e `test_pergunta_em_aberto_na_spec_bloqueia_pelo_markdown`.

**L5** — `dependencia.propagar` roda ponto-fixo: repete a varredura enquanto alguém novo é alcançado, então C→B→A cai junto. Ramo independente não é alcançado. `test_quarentena_propaga_transitivamente` e `test_quarentena_nao_alcanca_ramo_independente`; o efeito no lote está em `test_quarentena_arrasta_quem_depende_dela`.

**L6** — Duas barreiras. `_proxima_pendente` filtra `nome not in quarentena` ao escolher a próxima, e `atual_bloqueada` desvia o fluxo para esse mesmo seletor mesmo quando o núcleo mandaria reincidir na spec atual (veredito vermelho → codificar). O único ramo que devolve a decisão do núcleo com `proxima=spec_atual` exige `not atual_bloqueada`. O ramo de ciclo devolve `proxima_spec=None`. Não sobra entrada que resulte em codificar sobre spec em quarentena. `test_spec_em_quarentena_nunca_e_invocada` e `test_retentativa_de_spec_em_quarentena_nao_acontece`.

**L7** — `ciclo_em` faz eliminação de folhas (remove quem só depende de resolvidos) e devolve o resto; num grafo finito o resíduo só existe por ciclo. Arestas para fora do lote são descartadas antes, então dependência de spec fechada em outro lote não vira ciclo falso. A checagem é a primeira de `decidir_lote`, retornando `ESCALAR` com `Motivo.DEPENDENCIA_CIRCULAR` — não há laço nem quarentena total silenciosa. `test_ciclo_de_dependencia_escala_em_vez_de_travar` e `test_dependencia_para_fora_do_lote_nao_e_ciclo`. Observação factual, não correção: a evidência devolvida inclui também quem depende do ciclo sem estar nele; a spec não fixa o conteúdo da evidência.

**L8** — Dois pontos cobrem o caso. `len(quarentena) == len(nomes)` escala com `Motivo.LOTE_VAZIO` antes de qualquer consulta ao núcleo, e o ramo tardio `if not fechadas` escala com o mesmo motivo quando não há pendente e nada fechou. Como `propagar` só acrescenta chaves do próprio dicionário de dependências, a quarentena é sempre subconjunto do lote e a igualdade de tamanho significa mesmo "todas". Nenhum dos dois caminhos pode devolver `HOMOLOGAR`. `test_lote_todo_em_quarentena_escala_e_nunca_homologa`.

**L9** — `DecisaoDoLote` carrega as três listas e `_fechar` as preenche em todos os retornos: `fechadas` e `quarentena` na ordem do lote, e `_insumos_da_quarentena` emparelha cada spec em quarentena com o insumo declarado ou, para a arrastada, com a dependência que a bloqueou — de modo que nenhuma spec parada aparece sem motivo. `test_fechamento_carrega_fechadas_quarentena_e_insumo_faltante` e `test_fechamento_diz_por_que_a_arrastada_esta_parada`. O ramo de ciclo é a exceção deliberada: fecha com `quarentena=()` e `insumos_faltantes=()`, porque ali a quarentena nem chega a ser calculada; as três listas continuam presentes e coerentes entre si, o que `test_ciclo_nao_reporta_quarentena_nem_insumo` fixa.

## Contrato técnico e escopo

- **Insumo declarado, não inferido** — respeitado: o roteador só pergunta se a seção está vazia; o conteúdo dos itens é transportado, nunca interpretado.
- **Ordem de dependência** — respeitada por `em_ordem_de_dependencia`, que é topológica e estável (entre independentes, a ordem do lote), com `test_ordem_topologica_estavel`.
- **Pureza (`C15`)** — `test_cadeia_de_decisao_nao_importa_relogio_nem_io` passou a cobrir `lote` e `dependencia`. `secoes.py` não é varrido por esse teste; por leitura, importa apenas `re` e `unicodedata` e não toca disco nem relógio.
- **Fora de escopo** — o diff não monta lote, não reprocessa quarentena na mesma execução e não introduz fusível de iterações.
