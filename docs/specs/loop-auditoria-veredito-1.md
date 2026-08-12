# loop-auditoria — auditoria de critérios

Lido: `docs/specs/loop-auditoria.md` e `git diff da76ac3 -- tooling/loop`.

- **F1** — atendido
- **F2** — atendido
- **F3** — atendido
- **F4** — atendido
- **F5** — atendido
- **F6** — atendido
- **F7** — não verificável
- **F8** — atendido
- **F9** — atendido
- **F10** — atendido
- **F11** — atendido
- **F12** — atendido

## Porquê

**F1** — Em `driver.rodar`, o bloco `if fecha_o_ciclo and not auditado:` está dentro do laço, antes da linha que monta `spec` e antes de qualquer `invocar` da fase `HOMOLOGAR`. A guarda `auditado` impede repetição se o laço voltar a passar por ali. `test_a_auditoria_roda_antes_de_homologar` afirma a ordem observada nos prompts (`["auditoria", "homologar"]`).

**F2** — `auditoria.auditaveis` varre `Path(alvo)/"docs"/"specs"` com `glob("*.md")`, sem qualquer filtro por ciclo, lote ou `decisao.fechadas`. O que entra é o conteúdo da pasta no momento da chamada. `test_audita_todas_as_specs_do_alvo_nao_so_as_do_ciclo` roda o ciclo só com `alfa` e cobra `["alfa", "antiga"]`.

**F3** — `auditaveis` pula todo arquivo cujo texto satisfaz `secoes.perguntas_em_aberto(texto)`, que é o mesmo predicado de quarentena usado no resto do driver. `test_spec_em_quarentena_nao_e_auditada` passa `SPEC_TRAVADA` e cobra a ausência dela em `auditadas`.

**F4** — `_auditar` recebe `invocacoes`, faz `invocacoes += 1` a cada spec e devolve o total, que `rodar` reatribui na mesma expressão do `break`. `test_cada_invocacao_da_auditoria_conta_no_fusivel` fixa 5 (codificar, verificar, duas auditorias, homologar) e `test_homologar_conta_no_fusivel` foi corrigido de 3 para 4 — sinal de que a contagem é real e não paralela. Ressalva que não derruba o critério: o texto pede que conte, e conta; o limite não é reavaliado *entre* as auditorias, então um lote de treze specs estoura o teto antes de o driver reler o fusível.

**F5** — `_auditar` chama `invocar(...)` uma vez por nome devolvido por `auditaveis`, cada chamada com seu próprio prompt e seu próprio `artefato_esperado`. Não há acúmulo de contexto entre elas no código do diff. `test_uma_invocacao_por_spec` cobra duas chamadas distintas. A limpeza da sessão em si é propriedade de `invocacao.invocar`, que o diff não altera — usa o mesmo caminho das demais fases.

**F6** — `prompt_de` monta `"Leia <spec> e o estado atual de <escopo> (relativo ao alvo)"`. Não há ref base, não há menção a diff, não há `git`. `test_o_molde_pede_estado_atual_e_nao_diff` afirma `"estado atual" in prompt` e a ausência de `"diff"` e `"Ref base"`.

**F7** — O comando pedido restringe o diff a `tooling/loop`, então mudança em arquivo de skill fora desse caminho não apareceria aqui; a primeira metade do critério não é observável no material lido. A segunda metade também fica em aberto: `prompt_de` **reconstrói** o texto do molde como literal próprio dentro de `auditoria.py`, em vez de chamar o emissor já existente. O prompt resultante é coerente com a variante sem diff e não cita skill (`"Use a skill" not in prompt`, afirmado em dois testes), mas que seja *o molde já existente*, e não uma segunda cópia que pode divergir, não se decide sem abrir o emissor original — leitura que este escopo exclui.

**F8** — `caminho_da_auditoria` devolve `<alvo>/docs/specs/<nome>-auditoria.md`; o prompt fecha com `"Saída em {caminho_da_auditoria(...)}"` e `_auditar` passa o mesmo caminho relativo como `artefato_esperado`. As três pontas concordam. `test_o_resultado_vai_para_arquivo_proprio` cobra a existência.

**F9** — Nenhuma linha do diff escreve, move ou remove `-veredito.md`. A escrita da auditoria vai para caminho distinto por construção, e `_NAO_E_SPEC` inclui `-veredito`, então o veredito nem sequer entra na lista de auditáveis — não há como ser lido como spec e reescrito. `test_o_veredito_da_demanda_nao_e_tocado` compara o conteúdo do veredito byte a byte depois do ciclo.

**F10** — `regressoes` classifica o arquivo com `veredito.classificar` e devolve todo identificador cuja classificação `is not Classificacao.ATENDIDO` — o que cobre `não atendido` e `não verificável` sem enumerá-los. No driver, lista não vazia leva a `_decisao_solta(Motivo.REGRESSAO_DE_CRITERIO, ...)` seguido de `break`, que sai do laço antes da linha que invocaria `homologar`. `Motivo.REGRESSAO_DE_CRITERIO` existe em `roteador.py` como membro próprio, separado de `DEFEITO_DE_SPEC`. Dois testes cobrem os dois rótulos, e um deles afirma que nenhum prompt de `homologar` foi emitido. Ressalva: `regressoes` devolve `()` quando o arquivo não existe, então auditoria não escrita seria lida como verde — o que segura isso é o `artefato_esperado` passado a `invocar`, código fora deste diff.

**F11** — Sem regressões, o bloco só marca `auditado = True` e deixa o fluxo cair na linha seguinte, que segue o caminho de `homologar` inalterado. `test_auditoria_verde_segue_para_homologar` cobra `Motivo.GATE_CHECKLIST` no fim e a presença do prompt de `homologar`.

**F12** — A evidência da decisão é `tuple(sorted(regredidas))`, ou seja, nomes de spec. `_texto_da_escalada` acrescenta, só quando o motivo é `REGRESSAO_DE_CRITERIO`, uma linha `auditoria em: <caminho>` por nome. O conteúdo do arquivo nunca é lido ali. `test_o_relato_nomeia_a_spec_e_o_caminho_sem_transcrever` planta uma marca dentro da auditoria vermelha e cobra nome e caminho presentes, marca ausente.
