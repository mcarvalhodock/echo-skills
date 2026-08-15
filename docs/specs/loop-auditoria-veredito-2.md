# loop-auditoria — auditoria de critérios

Lido: `docs/specs/loop-auditoria.md` e `git diff da76ac3`.

- **F1** — atendido
- **F2** — não atendido
- **F3** — atendido
- **F4** — atendido
- **F5** — atendido
- **F6** — atendido
- **F7** — atendido
- **F8** — atendido
- **F9** — atendido
- **F10** — atendido
- **F11** — atendido
- **F12** — atendido

## Por quê

**F1** — atendido. Em `driver.rodar`, o bloco `if fecha_o_ciclo and not auditado:` está posicionado depois de `fecha_o_ciclo = fase is Fase.HOMOLOGAR` e antes da montagem do prompt e da invocação da fase, e sai por `break` quando há regressão. O flag `auditado` garante uma única passagem. `test_a_auditoria_roda_antes_de_homologar` afirma a ordem `["auditoria", "homologar"]` sobre as chamadas do executor.

**F2** — não atendido. `auditaveis()` varre `docs/specs/*.md`, o que cobre specs de fora do ciclo (`test_audita_todas_as_specs_do_alvo_nao_so_as_do_ciclo` prova isso), mas o filtro `_NAO_E_SPEC = ("-veredito", "-auditoria", "-manual-validation")` é aplicado como **substring** do `stem` (`if any(marca in arquivo.stem ...)`), não como sufixo. Uma spec chamada `loop-auditoria.md` tem `"-auditoria"` dentro do stem e é descartada como se fosse artefato de saída. O caso não é hipotético: a própria spec deste alvo é `docs/specs/loop-auditoria.md`, ou seja, ela nunca será auditada pela auditoria que ela especifica. O mesmo vale para qualquer spec cujo nome contenha `-veredito` ou `-manual-validation` em qualquer posição. "Todas as specs" não se sustenta. Nenhum teste do lote exercita nome de spec que colida com as marcas — todos usam `alfa`, `antiga`, `travada`.

**F3** — atendido. `auditaveis()` lê cada arquivo e pula os que têm `secoes.perguntas_em_aberto(texto)` não vazio, que é o critério de quarentena usado no resto do loop. `test_spec_em_quarentena_nao_e_auditada` roda com `SPEC_TRAVADA` no lote e afirma `"travada" not in executor.auditadas`.

**F4** — atendido. `_auditar` recebe `invocacoes`, faz `invocacoes += 1` a cada spec e devolve o valor, que `rodar` reatribui ao mesmo contador que alimenta `relato.invocacoes`. `test_cada_invocacao_da_auditoria_conta_no_fusivel` fixa 5 (codificar, verificar, 2 auditorias, homologar) e `test_homologar_conta_no_fusivel` foi corrigido de 3 para 4 — sinal de que o contador é o mesmo, e não um paralelo. Ressalva de leitura, não de veredito: o teste mede a contagem, não o disparo; o loop de auditoria não reconsulta o limite entre specs, então um fusível estourado no meio da varredura só será visto na volta ao `while`. Isso é comportamento do fusível, não descumprimento do texto do critério, que fala em contar.

**F5** — atendido. `_auditar` chama `invocar(...)` uma vez por nome devolvido por `auditaveis`, com prompt próprio por spec — cada `invocar` é um processo do CLI, que é a forma de sessão limpa que o loop já usa nas outras fases. `test_uma_invocacao_por_spec` afirma duas auditorias e dois prompts distintos (`len(set(...)) == 2`). O reuso de `Fase.VERIFICAR` é só rótulo de invocação, comentado como tal, e não injeta a skill no prompt (ver F7).

**F6** — atendido. `prompt_de` emite "Leia <spec> e o estado atual de <escopo> (relativo ao alvo)", sem ref base, sem `git diff`, sem menção a commit. `test_o_molde_pede_estado_atual_e_nao_diff` afirma `"estado atual" in prompt` e `"diff" not in prompt and "Ref base" not in prompt`.

**F7** — atendido. O `--stat` do diff não toca nenhum `*/SKILL.md`: só `README.md`, quatro arquivos em `docs/specs/`, `tooling/loop/{auditoria,driver,roteador}.py` e três de teste. A capacidade vive no driver, e o prompt não cita skill (`assert "Use a skill" not in prompt`, `"SKILL.md" not in prompt`). Ressalva declarada: a segunda metade da frase — "emite o molde **já existente**" — não é verificável dentro do limite de leitura imposto, porque `prompt_de` reescreve o texto do molde em `auditoria.py` em vez de chamar o emissor da leitura limpa, e comparar os dois exigiria abrir `agente.py`/`veredito.py`, fora do que foi autorizado ler. O que o diff mostra é texto equivalente, duplicado.

**F8** — atendido. `caminho_da_auditoria` devolve `Path(alvo)/"docs"/"specs"/f"{nome}-auditoria.md"`, o prompt fecha com `Saída em <esse caminho>`, `_auditar` passa `artefato_esperado=f"docs/specs/{nome}-auditoria.md"` e `test_o_resultado_vai_para_arquivo_proprio` checa a existência do arquivo.

**F9** — atendido. Nada no diff escreve, move ou remove `<nome>-veredito.md`: a auditoria só escreve no caminho de F8, e `_NAO_E_SPEC` mantém os vereditos fora da lista de alvos, então eles nunca viram destino de auditoria. `test_o_veredito_da_demanda_nao_e_tocado` compara o conteúdo do veredito depois da rodada e exige igualdade byte a byte.

**F10** — atendido. `regressoes()` classifica o arquivo com `veredito.classificar` e devolve todo identificador cuja classificação não seja `ATENDIDO` — o que engloba `não atendido` e `não verificável` (`test_regressao_escala_e_homologar_nao_roda` e `test_criterio_nao_verificavel_tambem_e_regressao`). Havendo regressão, `rodar` monta `_decisao_solta(Motivo.REGRESSAO_DE_CRITERIO, ...)` e faz `break` antes de invocar a fase, e o teste afirma que nenhum prompt `Use a skill homologar` foi emitido. `Motivo.REGRESSAO_DE_CRITERIO` existe em `roteador.py` com o valor `"regressao-de-criterio"`. Ressalva de leitura: `regressoes()` devolve vazio quando o arquivo não existe, isto é, auditoria não escrita conta como verde — a barreira contra isso é o `artefato_esperado` de `invocar`, cujo comportamento está fora do diff.

**F11** — atendido. Sem regressão, o bloco não faz `break` e a execução cai no fluxo normal da fase `HOMOLOGAR`. `test_auditoria_verde_segue_para_homologar` afirma `Motivo.GATE_CHECKLIST` e a presença do prompt de homologar.

**F12** — atendido. `_texto_da_escalada` já lista `evidência` (que, nesse motivo, são os nomes das specs) e acrescenta uma linha `auditoria em: <caminho>` por spec regredida, sem ler o conteúdo do arquivo. `test_o_relato_nomeia_a_spec_e_o_caminho_sem_transcrever` planta um segredo dentro da auditoria e exige nome + caminho presentes e segredo ausente.
