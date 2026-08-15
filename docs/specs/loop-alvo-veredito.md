# loop-alvo — veredito

Leitura limpa contra `docs/specs/loop-alvo.md` e o diff de `7f3b7d5..HEAD` limitado a `tooling/loop`, `verificar` e `metodologia-sle.md`.

- **T1** — atendido
- **T2** — atendido
- **T3** — atendido
- **T4** — atendido
- **T5** — atendido
- **T6** — atendido
- **T7** — atendido
- **T8** — atendido
- **T9** — atendido

## Por quê

**T1** — `driver.rodar` abre com `if not alvo.is_dir()` e devolve uma escalada `guarda-do-alvo` cuja evidência é `f"alvo não existe: {alvo}"`; `_texto_da_escalada` imprime essa evidência, então o caminho procurado aparece na saída. A checagem vem antes de qualquer leitura de spec ou chamada de git, que são as duas fontes possíveis de stack trace nesse ponto. `test_alvo_inexistente_escala_nomeando_o_caminho` exercita os dois lados: ação `ESCALAR` e o nome do diretório no texto.

**T2** — `git_alvo.raiz` devolve `None` quando `rev-parse --show-toplevel` falha, e o driver segue com `com_git = False` em vez de parar. O aviso é acrescentado uma única vez, no ramo `else` da abertura, e nomeia exatamente as duas perdas que o critério exige: "sem commit por tentativa e sem diff na leitura limpa". Como `avisos` é montado fora do laço e concatenado uma vez em `Relato`, repetição por fase é estruturalmente impossível. `test_pasta_sem_git_roda_em_modo_degradado_e_avisa_uma_vez` fixa a contagem em exatamente 1 e confirma que o executor foi chamado — modo degradado não é modo parado.

**T3** — Em `com_git = False` o driver pula `impedimentos`, nunca entra em `git_alvo.head` (guardado por `if com_git and fase is Fase.CODIFICAR`) e nunca chama `commitar_tentativa` (mesma guarda). Sobra a sonda, que é o que estabelece o modo — e o contrato técnico da spec a nomeia como a única. `test_modo_degradado_so_sonda_o_git_e_nao_opera` instala um espião em `git_alvo._git` e afirma igualdade exata: `chamadas == [("rev-parse", "--show-toplevel")]`. Igualdade, não `in`, é o que torna o critério falsificável — qualquer operação adicional quebra o teste.

**T4** — `prompt_de` bifurca em `if base is None` e devolve "Sem git no alvo: leia o estado atual de {escopo} (relativo ao alvo)", sem a substring "Ref base" que o ramo com git carrega. `base` só é preenchido sob `com_git`, então a bifurcação é acionada pelo modo, não por acaso. `test_modo_degradado_pede_estado_atual_e_nao_passa_ref_base` filtra os prompts pelo início da frase — não por substring, evitando o falso-positivo do caminho temporário do pytest — e exige "estado atual" presente e "Ref base" ausente em todos. Do lado da skill, `verificar/SKILL.md` ganhou a segunda variante do molde ("Leia ... e o estado atual de `<escopo>`") e o parágrafo que declara a degradação, fechando o critério na parte que não é código.

**T5** — `git_alvo.sujos` passa `-- .` ao `status --porcelain`, com `cwd` no alvo: o pathspec é resolvido pelo git a partir da subárvore, não filtrado em Python depois, como o contrato técnico exige. Os dois lados estão exercitados: `test_sujeira_fora_da_subarvore_nao_impede` suja `packages/web`, afirma `impedimentos() == ()` e roda o ciclo inteiro até `homologar`; `test_sujeira_dentro_da_subarvore_ainda_impede` mostra que a guarda não foi só afrouxada.

**T6** — `subarvore` calcula o relativo do alvo contra o toplevel e o caso raiz cai em `.`. `test_alvo_na_raiz_mantem_o_comportamento_de_hoje` verifica os dois lados do "comportamento atual": a subárvore é `.` e a sujeira na raiz continua impedindo. Como `-- .` a partir da raiz é o repositório inteiro, o caminho antigo é literalmente o caso particular do novo — não há ramo separado que possa divergir.

**T7** — O prompt com git diz "limitado a {escopo} (relativo à raiz do repositório)", e o escopo vem de `git_alvo.subarvore`. O molde propagou para os dois lugares onde ele é contrato: `verificar/SKILL.md` (primeira linha do bloco fixo, mais o escopo entre os insumos obrigatórios, com o "Pare e diga qual" já existente passando a cobri-lo) e `metodologia-sle.md`, que carrega a mesma linha. Três testes: `test_subarvore_e_o_caminho_relativo_a_raiz`, `test_prompt_de_verificar_limita_o_diff_a_subarvore` (afirma `packages/api` no prompt) e `test_subarvore_sobrevive_a_caminho_com_acento`, que fecha o furo de codepage que faria o limite deixar de casar com o disco num Windows pt-BR.

**T8** — `commitar_tentativa` usa `add -A -- . :!.sle/loop*.jsonl` com `cwd` no alvo, então o `.` é a subárvore e a escrituração do loop fica de fora. `test_commit_recolhe_so_a_subarvore` suja `packages/web`, roda em `packages/api` e afirma que **todo** caminho do commit começa com `packages/api/` — a asserção é universal, não existencial. Ressalva sobre o alcance da evidência: o `add` é escopado, mas o `commit` seguinte grava o índice inteiro. Mudança já **staged** fora da subárvore não é vista pela guarda de T5 (que por desenho só olha a subárvore) e entraria no commit. O diff não contém teste para esse estado inicial, então o critério está atendido em tudo que o diff exercita, com esse caminho não coberto.

**T9** — Duas não-interferências, ambas afirmadas em `test_subarvores_irmas_nao_interferem`: o registro nasce em `packages/api/.sle/` e não existe em `packages/web` — consequência de `registro.caminho_do_registro` ancorar no alvo, não no toplevel —, e nenhum caminho do commit começa com `packages/web/`. O lado "não reporta" também está coberto pelo escopo do prompt (T7), que impede a leitura limpa de julgar contra o diff do repositório inteiro. Vale aqui a mesma ressalva de T8: a via pelo índice pré-carregado é o único caminho em que uma irmã apareceria no commit, e ele não está exercitado.
