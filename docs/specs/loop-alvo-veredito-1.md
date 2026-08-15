# loop-alvo — veredito

- **T1** — atendido
- **T2** — atendido
- **T3** — atendido
- **T4** — atendido
- **T5** — atendido
- **T6** — atendido
- **T7** — atendido
- **T8** — não verificável
- **T9** — não verificável

## Por quê

**T1** — `driver.rodar` abre com `if not alvo.is_dir():` e devolve uma decisão de escalada com o motivo `GUARDA_DO_ALVO` e o texto `f"alvo não existe: {alvo}"`, antes de qualquer sonda de git ou leitura de spec. O caminho procurado está nomeado no impedimento e o retorno é um `Relato` normal — nenhum caminho de exceção. `test_alvo_inexistente_escala_nomeando_o_caminho` afirma `Acao.ESCALAR` e a presença do nome do caminho em `relato.texto`.

**T2** — quando `git_alvo.raiz(alvo)` devolve `None`, `com_git` é falso e o ciclo segue: as specs são montadas, o registro é gravado e o executor é invocado como sempre. O aviso é acrescentado uma única vez a `avisos`, fora do laço de fases, e entra no relato só no retorno final (`"\n".join([*avisos, texto])`); nomeia exatamente o que deixa de existir — "sem commit por tentativa e sem diff na leitura limpa". `test_pasta_sem_git_roda_em_modo_degradado_e_avisa_uma_vez` afirma que houve chamadas, que a fase final é `HOMOLOGAR` e que "degradado" aparece uma vez só.

**T3** — em modo degradado a guarda (`git_alvo.impedimentos`) fica no ramo `if com_git`; `base` é fixado em `None` sem chamar `_base_registrada` nem `git_alvo.head`; e `commitar_tentativa` está condicionado a `com_git and fase is Fase.CODIFICAR`. As três operações que o critério nomeia — guarda, commit e leitura de `HEAD` — ficam todas atrás do mesmo interruptor. A única invocação de git que resta é a sonda `rev-parse --show-toplevel`, que é a própria detecção autorizada no contrato técnico. `test_modo_degradado_so_sonda_o_git_e_nao_opera` instrumenta `git_alvo._git` e afirma a igualdade exata `chamadas == [("rev-parse", "--show-toplevel")]` — igualdade, não continência, então nenhuma outra operação passa.

**T4** — `prompt_de` ganhou um ramo anterior ao prompt normal de `verificar`: com `base is None`, o texto é "Sem git no alvo: leia o estado atual de {escopo}" e a frase "Ref base do diff" não é montada — a ref base não é passada porque a string que a carregaria não é a devolvida. Em modo degradado `base` é forçado a `None` no laço, então o ramo é o alcançado. `verificar/SKILL.md` declara a variante correspondente. `test_modo_degradado_pede_estado_atual_e_nao_passa_ref_base` afirma "estado atual" presente e "Ref base" ausente em todos os prompts de verificar.

**T5** — `sujos` passa `"--", "."` ao `git status --porcelain --untracked-files=all`, e o comando roda com `cwd=alvo`; o pathspec `.` é resolvido pelo git relativo ao cwd, então a listagem cobre só a subárvore do alvo. O limite é pathspec no git, não filtro em Python depois, como o contrato técnico exige. Dois testes fecham os dois lados: `test_sujeira_fora_da_subarvore_nao_impede` (arquivo sujo em `packages/web`, `impedimentos(packages/api) == ()`, ciclo chega a `HOMOLOGAR`) e `test_sujeira_dentro_da_subarvore_ainda_impede`, que garante que a guarda não foi apenas desligada.

**T6** — `subarvore` devolve `"."` quando o relativo é vazio, e com o alvo na raiz o pathspec `-- .` no cwd da raiz abrange o repositório inteiro: o comportamento é o de antes do diff, não um caso especial escrito à parte. `test_alvo_na_raiz_mantem_o_comportamento_de_hoje` afirma `subarvore(repo) == "."` e que um arquivo solto na raiz ainda impede.

**T7** — os três lugares em que o limite precisa aparecer aparecem. No prompt: `f"Ref base do diff: {base}, limitado a {escopo}."`, com `escopo = git_alvo.subarvore(alvo, raiz_do_repo)`. No molde da leitura limpa em `verificar/SKILL.md`: "o diff de `<base>..HEAD` limitado a `<escopo>`", com `<escopo>` também acrescentado à lista de insumos obrigatórios — o que faz a skill parar se ele faltar, em vez de assumir a raiz. Em `metodologia-sle.md` o molde canônico recebeu a mesma linha, então as duas cópias do molde não divergem. `test_prompt_de_verificar_limita_o_diff_a_subarvore` afirma `packages/api` em todo prompt de verificar; `test_subarvore_e_o_caminho_relativo_a_raiz` e o teste com acento cobrem a função. Fica registrado, sem ser defeito contra o critério: o `<escopo>` é relativo à raiz do repositório enquanto o `<alvo>` do mesmo prompt já é a subárvore, e o molde não diz contra qual dos dois o `<escopo>` deve ser resolvido.

**T8** — `git_alvo.commitar_tentativa` não é tocada pelo diff. O único trecho de `git_alvo.py` alterado abaixo de `subarvore` é o `sujos`; a chamada em `driver.py` mudou apenas a condição (`com_git and ...`), não os argumentos. Se o commit recolhe só a subárvore, isso depende de código anterior a `ba06072`, que está fora do que esta leitura pode observar. `test_commit_recolhe_so_a_subarvore` afirma a propriedade — com sujeira plantada em `packages/web` para que o teste tenha o que reprovar —, mas o veredito é sobre o diff, e um teste não executado nesta leitura é asserção, não evidência. Não é "não atendido": nada no diff contradiz o critério; é que o diff não contém a resposta.

**T9** — mesma razão, pela metade que depende do commit: "não commita nada de `packages/b`" recai sobre `commitar_tentativa`, ausente do diff. A outra metade — "não reporta nada de `packages/b`" — se apoia em `registro.caminho_do_registro(alvo)`, que também não é tocado pelo diff e já resolvia o registro a partir do alvo. `test_subarvores_irmas_nao_interferem` afirma as duas metades, mas ambas as implementações são anteriores a `ba06072`. O que o diff efetivamente muda a favor deste critério é o escopo da guarda (T5) e o escopo do prompt (T7), já contados lá; a não interferência no commit e no registro permanece fora do observável.
