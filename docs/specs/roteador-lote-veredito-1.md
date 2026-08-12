# roteador-lote — veredito

Base: `docs/specs/roteador-lote.md` contra `git diff 95a7479 -- tooling/loop/`.
Julgado por leitura do diff (código e testes do próprio diff). Nada foi executado.

- **L1** — atendido
- **L2** — atendido
- **L3** — atendido
- **L4** — não atendido
- **L5** — atendido
- **L6** — atendido
- **L7** — atendido
- **L8** — atendido
- **L9** — não atendido

## Porquê

**L1 — atendido.** `dependencia.declaradas` casa `^## Depende de` até a próxima seção (`_SECAO_DEPENDE_DE`) e extrai os nomes entre crases na ordem em que aparecem. O caso `nenhuma` é tratado antes da extração: se o corpo, sem acento e em minúsculas, começa com `nenhuma`, devolve `()` — o que também neutraliza a forma real do repositório `Nenhuma. \`roteador-lote\` depende desta.`, que declararia a aresta invertida. Ausência da seção também devolve `()`. Quatro testes cobrem as quatro formas.

**L2 — atendido.** Em `decidir_lote`, quando a decisão do núcleo é `INVOCAR/HOMOLOGAR` (fim da spec atual), o lote a intercepta, marca a spec atual como fechada e, havendo pendente, devolve `Decisao(INVOCAR, TRANSICAO, fase=CODIFICAR)` com `proxima_spec`. Não há caminho para `ESCALAR` nem para `Fase.ESPECIFICAR` nesse ramo. `test_veredito_verde_com_pendentes_vai_para_a_proxima_spec` e `test_a_proxima_spec_respeita_a_ordem_de_dependencia` exercitam o ramo, este último também a ordenação topológica estável de `em_ordem_de_dependencia`. Ressalva de escopo: o reconhecimento do "fim de spec" é `base.acao is INVOCAR and base.fase is HOMOLOGAR`, isto é, depende do contrato de `roteador.decidir` — que é da `roteador-nucleo` e não foi reaberto aqui.

**L3 — atendido.** Esgotadas as pendentes (`_proxima_pendente` devolve `None`) e existindo pelo menos uma fechada, o `return` final entrega `INVOCAR/HOMOLOGAR` com `proxima_spec=None`. `test_lote_esgotado_com_algo_fechado_vai_para_homologar` cobre, inclusive a inclusão da spec atual em `fechadas`.

**L4 — não atendido.** A metade da quarentena está lá: uma spec com `insumo_faltante` não vazio entra em `bloqueadas`, é excluída de `_proxima_pendente`, o lote segue nas demais e a decisão não escala (`test_spec_sem_insumo_entra_em_quarentena_e_o_lote_segue`). Falta o gatilho que o critério nomeia: nada no diff lê a seção `## Perguntas em aberto`. `dependencia.py` só tem regex para `## Depende de`; `SpecDoLote.insumo_faltante` é preenchido pelo chamador, e o comentário no campo apenas descreve de onde o dado deveria vir. Não existe função que receba o texto de uma spec e conclua "esta está bloqueada", nem teste que parta do texto — logo o critério, como escrito ("Spec com a seção `## Perguntas em aberto` não vazia entra em quarentena"), não é exercitado por nada. Note que o contrato técnico da própria spec atribui a leitura da seção ao roteador ("o roteador só lê se a seção está vazia ou não"), e "Fora de escopo" delega ao chamador só a montagem do lote, não essa leitura.

**L5 — atendido.** `propagar` faz ponto-fixo: repete a varredura enquanto alguém novo é alcançado, então C→B→A fecha em uma segunda passada independentemente da ordem do dicionário. `test_quarentena_propaga_transitivamente` é exatamente o caso C/B/A do critério; `test_quarentena_nao_alcanca_ramo_independente` guarda o falso positivo, e `test_quarentena_arrasta_quem_depende_dela` prova a propagação já dentro de `decidir_lote`.

**L6 — atendido.** É invariante estrutural, não caso: `codificar` só sai de `_proxima_pendente`, que filtra `nome not in quarentena`. O único outro ramo que devolve a decisão crua do núcleo (`if not fecha_a_spec and not atual_bloqueada`) é guardado por `atual_bloqueada`, de modo que uma spec em quarentena nunca recebe nem a retentativa que o núcleo mandaria (`test_retentativa_de_spec_em_quarentena_nao_acontece`, com veredito vermelho, desvia para a próxima spec). `test_spec_em_quarentena_nunca_e_invocada` cobre a outra entrada.

**L7 — atendido.** `ciclo_em` faz remoção sucessiva de nós sem requisitos pendentes; o resíduo é o conjunto preso em ciclo. Arestas para fora do lote são descartadas antes (`dentro_do_lote`), então dependência externa não vira ciclo falso. A checagem é a primeira coisa em `decidir_lote`, antes de calcular quarentena — o que satisfaz o "nunca em laço nem em quarentena silenciosa de todas", já que o ciclo escala mesmo quando todas as envolvidas também estariam bloqueadas. `Motivo.DEPENDENCIA_CIRCULAR = "dependencia-circular"` bate com o texto do critério, e a evidência carrega os nomes. Testes: ciclo direto, indireto, acíclico e aresta externa, mais `test_ciclo_de_dependencia_escala_em_vez_de_travar`.

**L8 — atendido.** Dois caminhos, ambos com `Motivo.LOTE_VAZIO = "lote-vazio"`: o precoce, quando `len(quarentena) == len(nomes)`, e o tardio, quando não há pendente nem fechada. `propagar` só devolve nomes que são chaves de `dependencias` (ou seja, do lote), então a comparação por tamanho é válida. O `return` de homologar está depois de ambos, logo é inalcançável com o lote todo em quarentena. `test_lote_todo_em_quarentena_escala_e_nunca_homologa` afirma as duas metades — escala com o motivo certo e não é homologar.

**L9 — não atendido.** As três listas existem em `DecisaoDoLote` (`fechadas`, `quarentena`, `insumos_faltantes`) e `_fechar` as preenche em toda saída, na ordem do lote. A terceira, porém, não é "o insumo faltante de cada spec em quarentena": `insumos_faltantes` é montada por `if spec.insumo_faltante`, isto é, só as bloqueadas na origem. As specs arrastadas por propagação (L5) aparecem em `quarentena` sem nenhuma entrada correspondente, então quem lê a decisão vê o nome em quarentena e não encontra por que ela está lá. `test_fechamento_carrega_fechadas_quarentena_e_insumo_faltante` não pega isso porque o caso montado tem uma única bloqueada e nenhuma dependente. Segundo desvio, menor: na saída por `DEPENDENCIA_CIRCULAR` o `_fechar` recebe `quarentena=()` explicitamente, então a decisão que encerra o lote nesse caminho carrega quarentena vazia mesmo havendo specs com insumo faltante — enquanto `insumos_faltantes` vem preenchida, deixando as duas listas em desacordo.
