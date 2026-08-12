# Veredito — roteador-nucleo

Base: `docs/specs/roteador-nucleo.md` e `git diff fbc8cbb -- tooling/loop/`. Leitura estática do diff; nenhuma execução de teste.

## Tabela de transições

- **C1** — atendido. `decidir` trata `Fase.CODIFICAR` antes de qualquer ramo de escalada e devolve `Decisao(Acao.INVOCAR, Motivo.TRANSICAO, fase=Fase.VERIFICAR)`. Não há caminho de `ESCALAR` a partir dessa fase. `test_codificar_concluida_invoca_verificar` (`spec:C1`).

- **C2** — atendido. Em `_decidir_apos_verificar`, ausência de `não verificável` e de `não atendido` cai em `Decisao(INVOCAR, fase=Fase.HOMOLOGAR)`. `test_veredito_todo_atendido_invoca_homologar` (`spec:C2`). A interceptação por lote é fora de escopo desta spec.

- **C3** — atendido. O ramo final devolve `INVOCAR` com `fase=CODIFICAR` e `tentativa=estado.tentativas + 1`, alcançado só depois de descartar `não verificável` e com `estado.tentativas < estado.teto`. A evidência carrega os identificadores não atendidos. `test_nao_atendido_abaixo_do_teto_volta_para_codificar` assere ação, fase, `tentativa == 2` e `evidencia == ("C2",)`.

- **C4** — atendido. `estado.tentativas >= estado.teto` devolve `ESCALAR` com `Motivo.TETO_DE_TENTATIVAS` e `evidencia=estado.vereditos`, uma tupla — a ordem informada pelo chamador é preservada sem reordenação. `test_teto_estourado_escala_com_os_vereditos_em_ordem` compara a tupla inteira, não um conjunto. O roteador não produz os caminhos; recebe-os no estado, o que é coerente com "descobrir o estado" estar fora de escopo.

- **C5** — atendido. O teste de `não verificável` é o primeiro dentro de `_decidir_apos_verificar`, antes do cálculo de `não atendido` e antes da comparação com o teto; devolve `ESCALAR` com `Motivo.DEFEITO_DE_SPEC`. Os dois lados da precedência estão exercitados: `test_nao_verificavel_tem_precedencia_sobre_nao_atendido` (misto, `tentativas=0`) e `test_nao_verificavel_tem_precedencia_tambem_sobre_o_teto` (`tentativas=9`, `teto=3`).

- **C6** — atendido. `Fase.ESPECIFICAR` é a primeira guarda e devolve `ESCALAR` com `Motivo.GATE_SPEC_APROVADA`, ignorando veredito e tentativas — nenhum parâmetro do estado é lido depois dela. A segunda metade do critério ("nenhuma entrada produz `invocar: codificar`") está exercitada por varredura em `test_nenhuma_entrada_leva_de_especificar_para_codificar`, sobre quatro vereditos e três contagens de tentativa.

- **C7** — atendido. `Fase.HOMOLOGAR` devolve `ESCALAR` com `Motivo.GATE_CHECKLIST`, sem fase. `test_homologar_concluida_para_no_checklist` (`spec:C7`).

## Leitura do veredito

- **C8** — atendido. `_LINHA_DO_MOLDE` ancora em `^`, exige marcador de lista, captura o identificador e só então entrega o texto após o travessão a `_classificacao`, que normaliza acento (`unicodedata` NFD), remove `*` e crase, e compara em minúsculas. Os três estados e a variação de ênfase/acento/caixa estão nos testes `test_classifica_os_tres_estados_no_molde` e `test_enfase_acento_e_caixa_nao_alteram_o_resultado`. Ressalva sem impacto no veredito: a normalização de caixa cobre a classificação, não o identificador — `[A-Z]\d{1,3}` exige o ID em maiúscula, que é a forma que o molde de `verificar` emite.

- **C9** — atendido. Linha sem marcador de lista ou sem o separador não casa o regex e é descartada com `continue`; a classificação nunca é procurada na linha inteira. Coberto por dois ângulos: `test_linha_fora_do_molde_e_ignorada` (linha de tabela e prosa citando `C2`) e `test_justificativa_que_cita_criterio_nao_classifica_o_criterio_citado`, que roda sobre um veredito realista com continuação indentada citando `C1` — a regressão que a spec nomeia.

- **C10** — atendido. `_classificacao` termina em `return Classificacao.NAO_VERIFICAVEL` quando nenhum prefixo casa. `test_classificacao_irreconhecivel_vira_nao_verificavel` usa "depende do ambiente" e confirma que o critério vizinho continua classificado.

- **C11** — atendido. `_PREFIXOS` é ordenado do mais específico para o mais genérico, e `_TERMINADOR` exige que só venha pontuação depois do prefixo: `atendido em parte` casa `atendido` mas o resto `" em parte"` não é pontuação, então cai em `NAO_VERIFICAVEL`; `parcialmente atendido` e `quase atendido` não casam prefixo nenhum. As três formas estão parametrizadas em `test_entrada_ambigua_nunca_e_lida_como_atendido`, e `test_nao_atendido_nunca_e_lido_como_atendido` cobre o sufixo perigoso. O desempate do contrato técnico está implementado por `_SEVERIDADE` e testado em `test_identificador_repetido_com_conflito_fica_com_o_pior`.

- **C12** — atendido. `classificar` devolve `{}` para `None`, string vazia, só espaços, ou texto sem linha no molde; `_decidir_apos_verificar` converte dicionário vazio em `ESCALAR` com `Motivo.VEREDITO_AUSENTE` antes de qualquer outro ramo — não existe caminho de `INVOCAR` a partir daí. `test_veredito_sem_linha_no_molde_devolve_vazio` e `test_veredito_ausente_ou_ilegivel_escala_nunca_invoca`.

## Registro

- **C13** — atendido. `registrar` monta um dicionário com exatamente os sete campos de `CAMPOS`, na mesma ordem, e escreve uma linha (`json.dumps` + `\n`) em modo `"a"`. Não há campo de texto livre e a assinatura é keyword-only fechada: qualquer chave extra levanta `TypeError`, o que `test_registro_recusa_campo_de_texto_livre` transforma em critério executável. `test_append_nao_reescreve_linha_anterior` confirma que o conteúdo anterior é prefixo do novo. `caminho_do_registro` devolve `<alvo>/.sle/loop.jsonl`, relativo ao alvo, coberto por `test_registro_mora_dentro_do_alvo`.

- **C14** — atendido. `contar_tentativas` filtra por `spec` e por `transicao == "invocar:codificar"` — a mesma string que `_transicao` produz a partir da decisão, sem literal duplicado —, devolve `0` para arquivo inexistente e ignora linhas em branco. `test_conta_tentativas_de_codificar_por_spec` verifica isolamento entre specs e `test_registro_inexistente_conta_zero` o caso vazio. A leitura tem a forma que C3/C4 consomem: um inteiro de tentativas por spec.

## Fronteira de porte

- **C15** — atendido. `roteador.py` importa apenas `dataclasses`, `enum` e `veredito`; `veredito.py` apenas `re`, `unicodedata` e `enum`. Nenhum dos dois toca disco, relógio, rede ou harness, e `Decisao`/`Estado` são `frozen`, o que sustenta o determinismo. A verificação exigida pela spec está feita nos dois modos: `test_decidir_nao_toca_disco_nem_relogio` sabota `builtins.open`, `Path.open` e três funções de `time` antes de chamar `decidir`; e `test_cadeia_de_decisao_nao_importa_relogio_nem_io` lê a fonte dos dois módulos e recusa importações de I/O e relógio, fechando o buraco do import tardio dentro de função. `test_decidir_e_determinista` cobre a igualdade de saída para a mesma entrada. O instante entra por parâmetro em `registrar`, nunca lido dentro da decisão, como o contrato técnico exige.
