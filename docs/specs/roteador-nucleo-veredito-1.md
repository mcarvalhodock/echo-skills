# Veredito — roteador-nucleo

Base: `git diff fbc8cbb -- tooling/loop/` (arquivos novos: `veredito.py`, `roteador.py`, `registro.py`, `tests/conftest.py`, `tests/test_veredito.py`, `tests/test_roteador.py`, `tests/test_registro.py`). Leitura estática do diff; a suíte não foi executada.

## Tabela de transições

- **C1** — **atendido**. `decidir` devolve `Decisao(INVOCAR, TRANSICAO, fase=VERIFICAR)` para `fase_concluida is Fase.CODIFICAR`, sem ramo de escalada nesse caminho. Coberto por `test_codificar_concluida_invoca_verificar`.

- **C2** — **atendido**. Em `_decidir_apos_verificar`, com classificação não vazia, sem `não verificável` e sem `não atendido`, o retorno é `INVOCAR` com `fase=HOMOLOGAR`. Coberto por `test_veredito_todo_atendido_invoca_homologar`.

- **C3** — **atendido**. Com pelo menos um `não atendido`, nenhum `não verificável` e `tentativas < teto`, devolve `INVOCAR` / `fase=CODIFICAR` com `tentativa=estado.tentativas + 1`. Coberto por `test_nao_atendido_abaixo_do_teto_volta_para_codificar`, que verifica também o incremento.

- **C4** — **atendido**. `tentativas >= teto` com `não atendido` remanescente devolve `ESCALAR` / `TETO_DE_TENTATIVAS` com `evidencia=estado.vereditos`, tupla que preserva a ordem de entrada. Coberto por `test_teto_estourado_escala_com_os_vereditos_em_ordem`. Observação sem efeito no veredito: a lista de caminhos vem do chamador, coerente com "descobrir o estado" estar fora de escopo.

- **C5** — **atendido**. O ramo de `não verificável` precede tanto o de `não atendido` quanto a checagem de teto. Os dois casos exigidos pelo critério estão testados: mistura com `não atendido` e tentativa sobrando (`test_nao_verificavel_tem_precedencia_sobre_nao_atendido`) e tentativas acima do teto (`test_nao_verificavel_tem_precedencia_tambem_sobre_o_teto`).

- **C6** — **atendido**. `ESPECIFICAR` é o primeiro ramo de `decidir` e retorna antes de qualquer leitura de veredito ou tentativa; nenhum caminho posterior é alcançável a partir dele. A segunda frase do critério é exercitada por varredura em `test_nenhuma_entrada_leva_de_especificar_para_codificar` (4 vereditos × 3 contagens).

- **C7** — **atendido**. `HOMOLOGAR` devolve `ESCALAR` / `GATE_CHECKLIST`. Coberto por `test_homologar_concluida_para_no_checklist`.

## Leitura do veredito

- **C8** — **não verificável**. O parser classifica os três estados e é tolerante a lista, tabela, acento e caixa — isso está implementado e testado. Mas o critério amarra o parser ao "formato que `verificar` produz`", e nada no diff estabelece essa correspondência: os exemplos dos testes são construídos no próprio arquivo de teste, não derivados do molde de `verificar`, e o diff está restrito a `tooling/loop/`. Não é possível decidir, com o que foi lido, se o formato real cai dentro da tolerância do parser.

- **C9** — **não atendido**. A primeira metade está atendida: classificação irreconhecível cai no `return Classificacao.NAO_VERIFICAVEL` final, e critério repetido com conflito fica com a pior severidade. A segunda metade — "nenhuma entrada ambígua é lida como `atendido`" — é falsificável e falha: `_classificacao_da_linha` faz teste de substring, então qualquer linha que contenha `atendido` sem conter `nao atendido`/`nao verificavel` é lida como `ATENDIDO`. Uma linha como `- **C1** — parcialmente atendido` (ou "atendido em parte", "quase atendido") é exatamente a entrada ambígua que o critério proíbe e é classificada como atendido. Nenhum teste cobre esse caso: `test_classificacao_irreconhecivel_vira_nao_verificavel` usa `"parcialmente ok, depende"`, string que não contém a palavra.

- **C10** — **atendido**. `classificar` devolve `{}` para `None`, vazio e texto sem identificador; `_decidir_apos_verificar` converte `{}` em `ESCALAR` / `VEREDITO_AUSENTE` antes de qualquer outro ramo, de modo que nenhum desses casos pode produzir `INVOCAR`. Coberto nos dois níveis: `test_veredito_sem_criterio_reconhecivel_devolve_vazio` e `test_veredito_ausente_ou_ilegivel_escala_nunca_invoca`.

## Registro

- **C11** — **atendido**. `registrar` monta um dicionário com exatamente os sete campos de `CAMPOS`, abre em modo `"a"` e escreve uma linha JSON terminada em `\n`. Campos de texto livre são estruturalmente impossíveis: os parâmetros são keyword-only e fechados, e um extra levanta `TypeError` (`test_registro_recusa_campo_de_texto_livre`). A não reescrita das linhas anteriores é verificada por prefixo em `test_append_nao_reescreve_linha_anterior`, e a ordem/conjunto de campos por `tuple(linhas[0]) == CAMPOS`. `caminho_do_registro` ancora `.sle/loop.jsonl` no alvo (`test_registro_mora_dentro_do_alvo`).

- **C12** — **atendido**. `contar_tentativas` filtra por `spec` e por `transicao == "invocar:codificar"`, devolve 0 para arquivo inexistente e ignora linhas em branco. Coberto por `test_conta_tentativas_de_codificar_por_spec` (inclui spec ausente e discriminação entre specs) e `test_registro_inexistente_conta_zero`. A segunda frase do critério ("é essa leitura que alimenta o teto") descreve a fiação, que por C13 pertence ao chamador e não aparece no diff; a leitura em si, que é o que o critério pede, existe.

## Fronteira de porte

- **C13** — **atendido**, com lacuna de evidência. A propriedade se sustenta por inspeção: `roteador.py` importa apenas `dataclasses`, `enum` e `veredito`, e `veredito.py` apenas `re`, `unicodedata` e `enum` — nenhum disco, relógio, rede ou API de harness em toda a cadeia; `instante` entra por parâmetro em `registrar`, como o contrato técnico exige. O determinismo é testado (`test_decidir_e_determinista`) e a barreira estrutural também (`test_roteador_nao_importa_relogio_nem_io`). Ressalva: o critério pede execução "com o sistema de arquivos **e o relógio** instrumentados para falhar", e só o sistema de arquivos é instrumentado (`monkeypatch` de `builtins.open` e `Path.open`); nenhum teste sabota `time`/`datetime`. Além disso, a checagem estrutural inspeciona somente a fonte de `roteador.py`, não a de `veredito.py`, que participa da mesma cadeia de pureza.

## Observações fora dos critérios

- O contrato técnico pede "marcador `spec:<ID>` nos testes". Os testes trazem `# spec:C1` como comentário, não como `pytest.mark`. Se a convenção vigente em `tooling/ci/` é comentário, está conforme; não foi verificado, por estar fora do escopo de leitura desta avaliação.
