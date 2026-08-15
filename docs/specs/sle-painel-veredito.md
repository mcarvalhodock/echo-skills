# sle-painel — veredito

Base: `git diff 56fcc46` (`tooling/loop/painel.py`, `driver.py`, `registro.py`, `tests/test_painel.py`).
`tests/test_painel.py`: 17 passaram.

## Veredito

- **V1** — atendido
- **V2** — atendido
- **V3** — atendido
- **V4** — atendido
- **V5** — atendido
- **V6** — atendido
- **V7** — atendido
- **V8** — atendido
- **V9** — atendido
- **V10** — atendido
- **V11** — atendido
- **V12** — atendido

## Por quê

**V1** — `_comando_painel` itera `repos.carregar()` e imprime um `painel.linha_de(apelido, caminho)` por repositório; `linha_de` produz exatamente uma linha `apelido: rótulo — detalhe`. `test_o_painel_lista_todos_os_cadastrados` cadastra dois alvos em estados distintos e vê os dois apelidos e os dois rótulos na saída.

**V2** — o subparser `painel` declara `--alvo`, e o ramo correspondente resolve por `repos.resolver_cadastrado` e imprime só aquela linha, com `return` antes do laço. `test_alvo_mostra_so_aquele` confirma que o outro cadastrado não sai; `test_alvo_aceita_caminho_alem_de_apelido` cobre a metade "ou caminho" — passa um alvo **não cadastrado** pelo caminho e ainda assim obtém a linha, o que exercita a metade que a resolução por apelido não cobriria.

**V3** — `_comando_painel` retorna `0` nos dois ramos, sem exceção nem código de saída derivado do estado. `test_sai_com_zero_mesmo_com_travado` monta um alvo escalado por `fusivel` — motivo que cai no ramo "travado" — e afirma `== 0`.

**V4** — `estado_de` devolve `Estado("não começou", "sem registro de ciclo")` quando `registro.linhas` volta vazio, antes de qualquer outra derivação. A distinção pedida é honrada por construção: "ocioso" e "pronto" não existem como rótulos em lugar nenhum de `painel.py` — o único rótulo terminal possível é "aguarda você: checklist de homologação". O fixture `_alvo` cria `docs/specs/` sempre, então o teste de V4 roda com specs presentes e sem `loop.jsonl`, que é exatamente o caso nomeado no contrato técnico.

**V5** — `_ROTULO_POR_MOTIVO[GATE_SPEC_APROVADA]` = `"aguarda você: aprovação do lote"`, alcançado só quando `transicao == escalar`. `test_gate_de_spec_aprovada_pede_aprovacao_do_lote` grava essa decisão e lê o rótulo.

**V6** — mesmo mapa, `GATE_CHECKLIST` → `"aguarda você: checklist de homologação"`. Coberto por `test_gate_de_checklist_pede_checklist`. `test_pronto_nunca_e_afirmado` fecha o flanco do "Fora de escopo": um alvo cuja última linha é `invocar:homologar` cai no ramo `_TERMINAL_DE_FECHAMENTO`, que reusa o rótulo de checklist — em nenhum caminho o painel diz "pronto".

**V7** — qualquer motivo de escalada fora do mapa cai em `Estado("travado", f"{motivo} em \`{spec}\`")`, ou seja, o motivo cru vai para o detalhe e o detalhe entra na linha via `linha_de`. `test_outra_escalada_e_travado_e_nomeia_o_motivo` usa `teto-de-tentativas` e afirma tanto o rótulo quanto a presença do motivo no detalhe.

**V8** — o ramo final extrai a fase de `transicao.split(":")[-1]` e monta `"{fase} em \`{spec}\`"` sob o rótulo "em andamento". `test_linha_nao_terminal_e_em_andamento_com_fase_e_spec` verifica fase (`codificar`) e spec (`cobranca`) juntas no detalhe. Uma observação de leitura, não de defeito: `invocar:homologar` é desviado antes desse ramo e não aparece como "em andamento" — o que é coerente com o contrato técnico de que a última linha distingue terminal de interrompido, e com V6.

**V9** — `estado_de` deriva tudo de `registro.linhas(registro.caminho_do_registro(alvo))`, isto é, do `.sle/loop.jsonl` do próprio alvo; não há leitura nem escrita de arquivo de estado em `painel.py`, e o módulo não importa `casa`. `test_nao_ha_armazenamento_proprio_de_estado` afirma que, depois de um `painel`, a casa contém exatamente `["repos.md"]` — nenhum cache nasceu. O contrato "nada de cache" também se sustenta na estrutura: `Estado` é `frozen` e derivado por chamada, sem variável de módulo guardando resultado.

**V10** — o roteamento `if args.subcomando == "painel": return _comando_painel(args)` acontece antes de qualquer caminho que invoque agente, e `_comando_painel` chama apenas `repos` e `painel`, nenhum dos quais escreve. Dois testes atacam as duas metades: `test_o_painel_nao_invoca_agente` substitui `driver.invocar` por uma função que estoura e mesmo assim obtém `0`; `test_o_painel_nao_escreve_nada_no_alvo` compara o mapa completo de arquivos do alvo com seus `st_mtime_ns` antes e depois — comparação de dicionários, então arquivo novo ou arquivo alterado reprovariam igualmente. Registro e commit estão cobertos por esse mesmo mapa, já que ambos se manifestariam como escrita em disco no alvo.

**V11** — `estado_de` testa `caminho.is_dir()` primeiro e devolve `Estado("inacessível", …)` em vez de levantar; como o laço de `_comando_painel` só imprime, um alvo sumido não interrompe os seguintes. `test_um_inacessivel_nao_impede_os_outros` cadastra um vivo e um morto e exige os dois na saída, com `0` de retorno.

**V12** — o desenho somente-leitura é o mesmo que sustenta V9/V10, e não há lock, espera nem retry em nenhum ponto do caminho. `test_o_painel_le_com_ciclo_em_andamento_sem_esperar` compara os bytes do registro antes e depois. O caso mais duro do critério — ler enquanto o outro terminal escreve — é coberto por `test_le_com_a_ultima_linha_sendo_escrita`, que anexa um JSON truncado e ainda espera o estado correto derivado da última linha **íntegra**; isso só passa por causa da mudança em `registro.linhas`, que agora pula linha inválida em vez de propagar `JSONDecodeError`. Essa mudança é o que torna V12 uma propriedade e não uma coincidência de timing.
