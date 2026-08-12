# loop-cli — veredito

Base: `git diff 95c4a88 -- tooling/loop scripts`. Julgado sobre o diff e a spec, sem executar a suíte.

- **S1** — atendido
- **S2** — atendido
- **S3** — atendido
- **S4** — atendido
- **S5** — atendido
- **S6** — atendido
- **S7** — atendido
- **S8** — atendido
- **S9** — atendido
- **S10** — atendido
- **S11** — atendido
- **S12** — atendido

## Por quê

**S1** — O subparser `pedir` recebe `--alvo` (via `_comuns`) e `--pedidos` com default `pedidos.md`; `main` roteia por `args.subcomando == "pedir"` para `rodar_pedidos`, que é o segmento 1 interativo, e `--comando-interativo` continua exposto. `test_pedir_roda_o_segmento_um` prova o roteamento. Ressalva registrada, não suficiente para reprovar: `--fusivel` e `--teto` migraram para dentro de `rodar`, então em `pedir` eles caem no default via `getattr` e não são mais ajustáveis pela linha de comando — é uma perda de superfície em relação ao "comportamento de hoje", ainda que o caminho de execução seja o mesmo.

**S2** — Subparser `rodar` com `--specs` obrigatório, split por vírgula em `Config.specs`, roteando para `rodar` (headless: usa `--comando`, não o interativo). `test_rodar_roda_o_segmento_dois` cobre.

**S3** — Sem subcomando, `main` chama `analisador.print_help()` e levanta `SystemExit(2)`. Com subcomando desconhecido, o próprio `argparse` recusa a escolha inválida, imprime o uso (que lista `{pedir,rodar}`) e sai com 2. `test_sem_subcomando_ou_com_desconhecido_mostra_ajuda_e_falha` parametriza os dois casos e checa código não-zero mais a presença de `pedir` na saída.

**S4** — `--seco` está em `_comuns`, portanto nos dois subparsers, com o mesmo texto de ajuda e o mesmo campo em `Config`. O significado é honrado no laço: o ramo `if config.seco` quebra antes de `invocar`, de `gravar` e do commit. `test_seco_vale_nos_dois_subcomandos` prova a propagação; `test_modo_seco_nao_invoca_homologar` prova que nem o registro nasce (`not registro.caminho_do_registro(alvo).exists()`) e que `homologar` não é chamada no ensaio.

**S6** — `GATES_PLANEJADOS = (Motivo.GATE_SPEC_APROVADA, Motivo.GATE_CHECKLIST)` e o retorno final é `0 if relato.final.decisao.motivo in GATES_PLANEJADOS else 1`. O ensaio (`--seco`) também retorna 0 antes disso, coerente com "nada foi tentado". `test_gate_planejado_sai_com_zero` parametriza os dois motivos.

**S7** — Os sete motivos de exceção caem no `else` do mesmo retorno e produzem 1. `test_excecao_sai_com_nao_zero` parametriza exatamente a lista da spec — os sete, sem faltar nenhum.

**S8** — O `break` que existia em `if fase is Fase.HOMOLOGAR` foi removido; a fase passa a percorrer o corpo normal do laço e chegar a `invocar`. `test_o_lote_esgotado_invoca_homologar` confirma uma invocação de `homologar`, e `test_homologar_conta_no_fusivel` confirma que ela conta como invocação (3: codificar, verificar, homologar), isto é, não é um caminho paralelo. A cláusula "com pelo menos uma spec fechada" continua sendo decisão do roteador, que o diff não toca; ela permanece consistente porque `lote-vazio` é motivo de escalada (S7) e não rota para `homologar`.

**S9** — `prompt_de` para `homologar` deixou de ser `"Use a skill homologar. Alvo: {alvo}."` e passa a compor os quatro insumos: specs do ciclo (`", ".join(decisao.fechadas)`), vereditos (`caminho_do_veredito` de cada fechada), ref base do ciclo e alvo. `test_o_prompt_de_homologar_carrega_specs_vereditos_e_base` verifica os quatro no prompt real com duas specs.

**S10** — `_base_do_ciclo` varre `registro.linhas` de cima para baixo e devolve a evidência da **primeira** linha `invocar:codificar`, e o laço usa essa função no ramo `fecha_o_ciclo` em vez de `_base_registrada(spec)`. O teste é falsificável de verdade: além de exigir a base inicial no prompt, exige que o HEAD final — que mudou por causa do commit de tentativa — **não** apareça no prompt.

**S11** — A saída é capturada em `saida_da_homologacao = resultado.saida` (o objeto inteiro, sem corte nem formatação) e concatenada nas partes do relato, junto com o texto de fechamento das três listas. Nada no caminho lê ou condiciona decisão sobre esse texto — a decisão vem de `resultado` e do roteador —, o que preserva a leitura de `D3` argumentada no contrato técnico. `test_a_saida_de_homologar_e_repassada_na_integra` checa `CHECKLIST in relato.texto` e o motivo `GATE_CHECKLIST`; os testes convertidos em `test_driver`, `test_alvo`, `test_agente` e `test_ciclo` (de `fase is Fase.HOMOLOGAR` para `motivo is Motivo.GATE_CHECKLIST`) mostram que a última parada do ciclo passou a ser o checklist em todos os cenários já existentes.

**S12** — `homologar` entra pelo mesmo `invocar` das demais, com `artefato_esperado=None` (coerente com "não tem artefato em disco"), e a falha cai no mesmo `break` de `FALHA_DE_INVOCACAO` que qualquer fase. A captura de `saida_da_homologacao` acontece **depois** desse break, então uma falha não repassa saída nem produz fechamento. `test_falha_de_homologar_escala_e_nao_fecha_o_ciclo` força exit 4 e exige `ESCALAR` + `FALHA_DE_INVOCACAO`.

## Observação fora dos critérios

No ramo `fecha_o_ciclo`, `spec` vira a lista concatenada (`"alfa, beta"`) e essa string é passada adiante para `registro.contar_tentativas(caminho_reg, spec)` e `_veredito_de(alvo, spec)` na montagem do `EstadoDoLote` pós-`homologar`. Não fere nenhum dos doze critérios — `spec_atual` foi corrigido para `ultima_spec` e o veredito só é calculado na fase `VERIFICAR` —, mas é um valor com dois significados no mesmo nome dentro do laço.
