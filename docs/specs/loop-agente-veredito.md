# loop-agente — veredito

Leitura estática da spec `docs/specs/loop-agente.md` contra `git diff 7f3b7d5 -- tooling/loop`. Nada foi executado; onde o veredito depende de execução, está dito.

- **G1** — atendido
- **G2** — atendido
- **G3** — atendido
- **G4** — atendido
- **G5** — atendido
- **G6** — atendido
- **G7** — atendido
- **G8** — atendido
- **G9** — atendido
- **G10** — atendido
- **G11** — atendido

## Por quê

**G1** — `invocacao.comando_de(prompt, template)` recebe o template como parâmetro; `driver.Config.comando` o carrega e `rodar` o repassa a `invocar(..., template=config.comando)`. Na linha de comando entra por `--comando`. No código do laço não há executável literal: a única string `"claude"` está em `invocacao.COMANDO_PADRAO`, que é o default exigido por G2. `test_agente.test_o_comando_configurado_chega_ao_executor` prova que o template configurado chega ao processo (`executados[0][0] == "cursor-agent"`).

**G2** — `COMANDO_PADRAO = ("claude", "-p", MARCADOR)`, usado como default em `comando_de`, em `Config.comando` e no `--comando` da CLI. `test_sem_configuracao_o_comando_e_o_claude` fixa as duas pontas (função e constante).

**G3** — a substituição é por marcador em cada argumento (`arg.replace(MARCADOR, prompt) for arg in template`), não append no fim. `test_o_prompt_pode_vir_antes_de_outras_flags` usa `("agente", "{prompt}", "--headless")` e obtém o prompt na posição do meio, sem mudança de código.

**G4** — `invocacao.marcador_ausente` é chamado em `rodar` na abertura, antes do laço e antes de qualquer chamada a `invocar`; escala com `Motivo.GUARDA_DO_ALVO` e a evidência inclui `invocacao.MARCADOR`, ou seja, nomeia `{prompt}`. `test_template_sem_marcador_e_recusado_antes_de_invocar` afirma `executor.chamadas == []` e `"{prompt}" in relato.texto`.

**G5** — `executavel_ausente` resolve por `shutil.which(template[0])` e devolve o nome procurado; `rodar` escala com `f"executável não encontrado no PATH: {faltando}"`, retornando `Relato` em vez de deixar `subprocess.run` levantar `FileNotFoundError`. A guarda é condicionada a `executor is None`, que é exatamente o caminho real (`main` chama `rodar(config, executor=None)`); com executor injetado a camada de processo foi substituída e o PATH não diz nada. `test_executavel_ausente_escala_antes_de_gerar_processo` exercita o caminho real, com `invocacoes == 0` e o nome do executável no texto.

**G6** — `skills_instaladas.divergencias(alvo, metodo=CLONE_DO_METODO)` é chamado uma vez na abertura, antes do laço, e o retorno entra em `avisos`, que só é concatenado ao texto — nenhum ramo transforma divergência em `ESCALAR`. Itera as quatro de `SKILLS = ("especificar", "codificar", "verificar", "homologar")` e a mensagem nomeia a skill. `CLONE_DO_METODO = Path(__file__).resolve().parents[2]` é a raiz do clone, e o layout `<raiz>/<nome>/SKILL.md` bate com o que o README do próprio diff descreve para o instalador. `test_skill_divergente_avisa_e_a_execucao_continua` verifica os dois lados: um único aviso nomeando `codificar` e o lote seguindo até `HOMOLOGAR`. Ressalva não fatal ao critério: `if not no_clone.exists(): continue` faz uma skill ausente **no clone** sair da comparação em silêncio — é o lado do clone, não o da instalação, que o critério trata.

**G7** — os dois casos são ramos distintos com textos distintos: `f"skill \`{nome}\` ausente na instalação"` quando `_instalada` devolve `None`, e `"instalada difere da do clone"` só quando os hashes discordam. `test_skill_ausente_e_avisada_como_ausencia` afirma `all("ausente" in a)` e `not any("difere" in a)`.

**G8** — `_instalada` percorre `(Path(alvo)/".claude"/"skills", global_)` nessa ordem e retorna no primeiro `SKILL.md` existente. `test_escopo_local_tem_precedencia_sobre_o_global` monta global divergente e local igual ao clone e exige `divergencias(...) == ()`; sem a precedência o teste veria quatro divergências.

**G9** — `prompt_de` emite `"Use a skill codificar. Spec: docs/specs/<nome>.md. Alvo: <alvo>."` e, para verificar, o mesmo par mais `"Ref base do diff: <base>, limitado a <escopo> (relativo à raiz do repositório)"`. O ref base vem de `_base_registrada`/`git_alvo.head`, capturado antes da primeira tentativa. Há o ramo sem git, que declara a ausência de diff em vez de omiti-la. `test_o_prompt_cita_a_skill_e_passa_os_insumos` cobre nome da skill, caminho da spec, alvo e presença de `Ref base`.

**G10** — nenhum ponto de `prompt_de` lê spec ou veredito: as leituras de conteúdo (`montar_specs`, `_veredito_de`) alimentam o roteamento, não o texto enviado. `_texto_da_escalada` também só publica caminhos. `test_o_prompt_nao_carrega_o_corpo_da_spec_nem_do_veredito` planta uma marca dentro da spec e exige que nenhum prompt a contenha, mais a ausência de `"atendido"` (corpo de veredito) nos prompts.

**G11** — o comando só é lido em `invocar`; as decisões vêm de `_abertura`, `decidir_lote` e `registro.contar_tentativas`, nenhum dos quais recebe `config.comando`. `test_trocar_o_comando_nao_muda_a_sequencia_de_decisoes` roda o mesmo lote com `COMANDO_PADRAO` e com `cursor-agent`, lê as transições do registro em cada alvo e exige igualdade — e exige a lista não vazia, o que impede o teste de passar por vacuidade.

## Limite deste veredito

O julgamento é do texto do diff, não de execução: os testes de `tooling/loop/tests/test_agente.py` foram lidos, não rodados. Um veredito de execução exigiria rodar a suíte.
