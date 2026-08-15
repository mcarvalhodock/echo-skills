# roteador-driver-invocacao — veredito

Base: `git diff 7f3b7d5 -- tooling/loop/` (arquivos novos `git_alvo.py`, `invocacao.py`, `tests/test_git_alvo.py`, `tests/test_invocacao.py`).

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

**I1** — `invocar` chama o executor uma vez por chamada, e o executor real é `subprocess.run` sem estado entre chamadas: não há objeto de sessão sobrevivendo a uma invocação. `comando_de` monta `("claude", "-p", prompt)` e nada mais; nenhuma flag de retomada entra no comando, e como o comando é a única coisa que o executor recebe, não existe caminho pelo qual a segunda fase herde a primeira. A retentativa não é caso especial no código — ela é outra chamada de `invocar`, igual a qualquer outra, que é exatamente o que o critério pede. Os testes cobrem os dois lados: `test_cada_invocacao_e_um_processo` (duas chamadas, dois comandos) e `test_nenhuma_invocacao_retoma_sessao` (ausência de `--resume`, `--continue`, `-c`, `--session-id`).

**I2** — `invocar` recebe `executor=None` e cai em `executar_de_verdade` só quando ninguém injeta. Os testes de `test_invocacao.py` passam `ExecutorFalso` em todas as chamadas, e `executar_de_verdade` — o único ponto que invoca `claude` — não é exercitado por nenhum teste. O caminho percorrido é o inteiro (montagem de comando, cwd, exit code, checagem de artefato, `ok`); o que é substituído é só a borda do processo.

**I3** — `Resultado.saida` guarda o texto e nenhum ramo de decisão o lê: `ok` consulta apenas `exit_code` e `artefato_presente`. Os dois testes que mais importam aqui são os adversariais — saída dizendo "FALHOU TUDO" com exit 0 dá `ok is True`, e saída dizendo "tudo certo, 15 criterios atendidos" com exit 1 dá `ok is False`. O texto pode mentir nos dois sentidos e não move o veredito. `Resultado` carrega também `fase` e `artefato_esperado`, mas são identificação do que foi pedido, não sinal de sucesso.

**I4** — `ok` é conjuntivo: exit code diferente de zero derruba antes de qualquer outra coisa, e artefato esperado ausente derruba mesmo com exit 0. Os quatro casos da matriz estão testados, inclusive os cruzados (`test_artefato_presente_nao_salva_exit_code_ruim` e `test_artefato_esperado_ausente_falha`), então não sobra combinação que produza sucesso silencioso. `test_artefato_e_procurado_dentro_do_alvo` fecha a brecha de o artefato ser encontrado fora do alvo. Registro sem julgar: a falha é sinalizada por um booleano de retorno, não por exceção — quem age sobre ela é o laço, que esta spec põe fora de escopo.

**I5** — `sujos` lê `git status --porcelain` e `impedimentos` transforma a lista num problema que nomeia os arquivos por extenso. O corte em `linha[2:]` respeita as duas colunas de status, então nomes de arquivo não perdem letra — inclusive para untracked (`??`), que é o caso do arquivo novo criado por uma fase. `test_working_tree_sujo_impede_comecar` verifica que tanto o untracked quanto o modificado aparecem no texto, e `test_working_tree_limpo_nao_impede` guarda o outro lado, para a guarda não ser um `assert True` disfarçado.

**I6** — `branch_default` consulta `git symbolic-ref refs/remotes/origin/HEAD` e só cai nos nomes convencionais quando não há remoto — que é o que o contrato técnico manda. `impedimentos` compara com o branch atual. Os testes cobrem os dois regimes: parametrizado em `main` e `master` sem remoto, e `test_branch_default_vem_do_remoto_quando_ele_existe`, onde o default é `entrega` — esse último é o que prova que a detecção é por remoto e não por nome chutado. Todos operam em repositório temporário criado pela suíte.

**I7** — `commitar_tentativa` faz um `add -A` seguido de um único `commit`, com assunto `loop(<spec>): codificar tentativa <n>` e trailer `SLE-Loop: <spec>#<n>` separados por linha em branco, o que faz o trailer cair no corpo. Os testes checam assunto e corpo literalmente, checam que duas mudanças viram **um** commit (contagem de `rev-list` sobe exatamente 1, e `show --name-only` traz os dois arquivos), e `test_o_rebase_posterior_acha_os_commits_do_loop` usa a régua declarada no contrato — `git log --grep='^SLE-Loop:'` — encontrando as duas tentativas.

**I8** — a função stageia e então pergunta `git diff --cached --name-only`; vazio, ela retorna `None` antes de chegar ao `commit`. Como a checagem é feita depois do `add -A`, ela enxerga também os untracked, que é onde um "nada mudou" falso poderia se esconder. `test_tentativa_sem_mudanca_nao_gera_commit_vazio` confirma retorno `None` e contagem de commits inalterada.

**I9** — o módulo só emite `rev-parse`, `symbolic-ref`, `status`, `add`, `commit`; nenhum verbo de reescrita ou de publicação aparece. `test_modulo_nao_reescreve_historico_nem_publica` lê o próprio fonte e proíbe `push`, `--amend`, `rebase`, `filter-branch`, `reset --hard`, `--force`, `cherry-pick` e `commit-tree`. É uma garantia estrutural, não comportamental — ela vale para este módulo e não impede outro módulo do loop de fazer push. Dentro do recorte da spec, que fala do driver de invocação, é o que dá para provar, e a lista de proibidos cobre os caminhos reais de reescrita.

**I10** — `head` devolve `git rev-parse HEAD` e é comparado contra o git direto em `test_head_devolve_o_sha_atual`. `test_head_muda_depois_do_commit_e_o_anterior_serve_de_base` mostra o SHA mudando após a tentativa e o SHA antigo servindo de ref base num `diff base..HEAD`. O "quando capturar" que a própria spec delega à `roteador-driver` não é exercitado aqui, corretamente: a capacidade está entregue, a sequência não.
