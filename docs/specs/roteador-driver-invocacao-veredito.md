# roteador-driver-invocacao — veredito

Base: `docs/specs/roteador-driver-invocacao.md` e `git diff 7f3b7d5 -- tooling/loop/git_alvo.py tooling/loop/invocacao.py tooling/loop/tests/test_git_alvo.py tooling/loop/tests/test_invocacao.py`.

- **I1** — atendido
- **I2** — atendido
- **I3** — atendido
- **I4** — atendido
- **I5** — atendido
- **I6** — atendido
- **I7** — atendido
- **I8** — atendido
- **I9** — atendido
- **I10** — atendido

## Porquê

**I1 — atendido.** `invocar` chama o executor uma vez por chamada, e o caminho real (`executar_de_verdade`) é um `subprocess.run` por invocação: não há objeto de sessão, handle ou estado que sobreviva entre chamadas, então retentativa é necessariamente processo novo. `comando_de` devolve `("claude", "-p", prompt)` e nada mais; `test_nenhuma_invocacao_retoma_sessao` confirma a ausência de `--resume`, `--continue`, `-c` e `--session-id` no comando, e `test_cada_invocacao_e_um_processo` confirma duas execuções distintas para dois prompts. A evidência é estrutural (comando montado e ausência de estado), não observação de PIDs — mas observar PID exigiria chamar `claude`, que I2 e o contrato técnico proíbem; dentro da régua que a própria spec fixa, o critério está exercitado.

**I2 — atendido.** `invocar` recebe `executor=None` e cai em `executar_de_verdade` só por omissão; `test_invocacao.py` passa `ExecutorFalso` em todas as invocações e registra comando e cwd. Nenhum teste do diff invoca `claude`, e `test_o_executor_e_injetavel_e_a_suite_nao_chama_claude` ainda confere que o cwd repassado é o alvo.

**I3 — atendido.** `Resultado.saida` guarda o texto integral e `Resultado.ok` só lê `exit_code` e `artefato_presente` — o texto não entra em nenhuma decisão, nem por parsing nem por heurística. Os dois sentidos estão cobertos: `test_saida_e_registrada_e_nao_interpretada` (saída catastrófica com exit 0 → `ok is True`) e `test_saida_otimista_nao_salva_exit_code_ruim` (saída triunfal com exit 1 → `ok is False`). "Registrado" aqui é o campo do resultado; persistir em disco é escrituração, de outro módulo, e a spec não pede isso daqui.

**I4 — atendido.** `ok` é conjuntivo: exit não-zero reprova sempre, e artefato esperado ausente reprova mesmo com exit 0. As quatro combinações relevantes estão nos testes (`exit 2`, artefato ausente, artefato presente com exit 0, artefato presente com exit 1). Não existe caminho em que `ok` seja `True` sem `exit_code == 0`, e o único caso em que a existência de artefato não é exigida é quando não há artefato esperado (`artefato_esperado is None`), que é ausência de expectativa, não sucesso silencioso. `test_artefato_e_procurado_dentro_do_alvo` fecha a brecha de o artefato ser encontrado fora do alvo.

**I5 — atendido.** `impedimentos` chama `sujos`, que roda `git status --porcelain --untracked-files=all` — o `--untracked-files=all` é o que permite nomear arquivo por arquivo em vez de colapsar diretório novo numa linha — e devolve os caminhos, que entram na mensagem `"working tree sujo: ..."`. A exceção é `_E_ESCRITURACAO = ^\.sle/loop[^/]*\.jsonl$`, exatamente `.sle/loop*.jsonl` e nada mais. Cobertura nos dois sentidos: sujeira real impede e é nomeada, limpo não impede, `.sle/loop.jsonl` e `.sle/loop-1.jsonl` não impedem, e `test_arquivo_de_alguem_em_sle_com_nome_parecido_ainda_e_sujeira` prova que `.sle/loop-anotacoes.md` continua sendo sujeira — que era a armadilha do prefixo solto.

**I6 — atendido.** `branch_default` consulta `git symbolic-ref refs/remotes/origin/HEAD` primeiro e só cai nos nomes convencionais quando não há remoto; `impedimentos` compara com `branch_atual` e acrescenta o problema nomeando o branch. Os testes cobrem `main`, `master` (parametrizado) e o caso do remoto mandando em nome não convencional (`entrega`), onde o critério passaria se a implementação fosse só a lista fixa.

**I7 — atendido.** `commitar_tentativa` estagia com `git add -A -- . :!.sle/loop*.jsonl` — um único `git commit` depois, logo um commit por tentativa — e monta assunto `loop(<spec>): codificar tentativa <n>` com corpo `SLE-Loop: <spec>#<n>`. Os testes conferem assunto e trailer literalmente, conferem que duas mudanças viram um commit só com os dois arquivos, conferem que a escrituração fica de fora do commit e — o que fecha o contrato — `test_o_rebase_posterior_acha_os_commits_do_loop` usa a própria régua da spec, `git log --grep='^SLE-Loop:'`, e acha as duas tentativas.

**I8 — atendido.** Depois de estagiar, a função testa `git diff --cached --name-only` e devolve `None` sem commitar quando está vazio. `test_tentativa_sem_mudanca_nao_gera_commit_vazio` confere retorno `None` e contagem de commits inalterada. O caso em que só a escrituração mudou cai no mesmo ramo, porque ela foi excluída do `add`.

**I9 — atendido.** Nenhuma das funções chama push, amend ou qualquer reescrita: os verbos usados são `rev-parse`, `symbolic-ref`, `status`, `add`, `diff --cached` e `commit`. `test_modulo_nao_reescreve_historico_nem_publica` é estrutural — lê o fonte e proíbe as substrings `push`, `--amend`, `rebase`, `filter-branch`, `reset --hard`, `--force`, `cherry-pick`, `commit-tree`. É a forma cabível de verificar uma proibição (ausência não se prova por execução), com o efeito colateral conhecido de também barrar essas palavras em comentários.

**I10 — atendido.** `head()` é `git rev-parse HEAD` e devolve o SHA. `test_head_devolve_o_sha_atual` confere contra o git direto e `test_head_muda_depois_do_commit_e_o_anterior_serve_de_base` confere que o SHA muda após uma tentativa e que o SHA anterior serve de base num `diff base..HEAD`. A parte de *quando* capturar como ref base é explicitamente de outra spec e corretamente não aparece aqui.
