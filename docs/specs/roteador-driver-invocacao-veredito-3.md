# roteador-driver-invocacao — veredito

Base: `git diff 7f3b7d5 -- tooling/loop/git_alvo.py tooling/loop/invocacao.py tooling/loop/tests/test_git_alvo.py tooling/loop/tests/test_invocacao.py` (quatro arquivos novos).
Suíte dos dois arquivos de teste: 24 passaram.

## Processo

- **I1** — atendido

`invocar` chama o executor uma vez por chamada, e `comando_de` devolve `(claude, -p, prompt)` — nenhuma flag de retomada. `test_nenhuma_invocacao_retoma_sessao` fixa isso como régua, verificando a ausência de `--resume`, `--continue`, `-c` e `--session-id` no comando; `test_cada_invocacao_e_um_processo` mostra duas chamadas independentes. Como não há estado de sessão em lugar nenhum do módulo, retentativa é indistinguível de primeira tentativa — que é exatamente o que o critério pede.

- **I2** — atendido

`invocar(..., executor=None)` cai em `executar_de_verdade` só por omissão; todos os testes de `test_invocacao.py` passam `ExecutorFalso`, e nenhum deles atinge `subprocess`. O caminho exercitado é o inteiro: `invocar` → comando → resultado → `ok`. A palavra `claude` só aparece na constante `EXECUTAVEL`, nunca num teste executado.

- **I3** — atendido

`Resultado.saida` guarda o texto e `Resultado.ok` não o consulta: só `exit_code` e `artefato_presente`. Os dois testes que importam são os invertidos — saída dizendo "FALHOU TUDO" com exit 0 dá `ok is True`, e saída dizendo "tudo certo, 15 criterios atendidos" com exit 1 dá `ok is False`. É a forma falsificável do critério, e ela está lá.

- **I4** — atendido

`ok` é conjuntivo: exit não-zero reprova, e artefato esperado ausente reprova, e um bom não compensa o outro (`test_artefato_presente_nao_salva_exit_code_ruim`). O artefato é procurado em `Path(alvo) / artefato_esperado`, com teste dedicado a garantir que é relativo ao alvo e não ao método. A falha é um `ok is False` no valor de retorno, não uma exceção — o critério pede falha explícita, não interrupção, e um campo booleano que ninguém pode confundir com sucesso atende à letra dele. Nenhuma combinação das quatro produz `ok is True` indevido.

## Guardas antes de começar

- **I5** — não atendido

A guarda funciona no essencial: `impedimentos` recusa e nomeia os arquivos sujos (`test_working_tree_sujo_impede_comecar` cobre modificado e não-rastreado), `--untracked-files=all` evita o diretório novo virar uma linha só, e o corte de duas colunas em vez de três preserva a primeira letra do nome. A exceção da escrituração também está lá, e o teste que a defende é o certo: rodar duas vezes seguidas não se auto-bloqueia.

O que falha é o desenho da exceção. O critério a delimita a `.sle/loop*.jsonl`; o código a implementa como `caminho.startswith(".sle/loop")`, prefixo puro, sem extensão. Logo `.sle/loop-anotacoes.md`, `.sle/loopback.py` ou qualquer arquivo cujo nome comece por `loop` dentro de `.sle/` fica sujo e **não é nomeado** — a guarda deixa passar sujeira que o critério manda apontar. Nenhum teste exercita esse caso: `test_escrituracao_do_loop_nao_conta_como_sujeira` prova o lado permissivo com dois `.jsonl` e o lado restritivo com `.sle/manifesto.md`, que não começa por `loop` e por isso não distingue as duas leituras. Reforça o diagnóstico o fato de `commitar_tentativa` usar o pathspec `:!.sle/loop*.jsonl` — a extensão está no filtro do commit e sumiu no filtro da sujeira, então as duas metades do mesmo conceito discordam entre si.

- **I6** — atendido

`branch_default` consulta `git symbolic-ref refs/remotes/origin/HEAD` primeiro e só cai nos nomes convencionais quando não há remoto — `test_branch_default_vem_do_remoto_quando_ele_existe` prova que, com `origin/HEAD` apontando para `entrega`, é `entrega` que impede, e não `main`. O fallback devolve o branch atual apenas quando ele está em `("main", "master")`, o que produz o impedimento pedido sem inventar verdade sobre repositório sem remoto. Parametrizado nos dois nomes, e o impedimento carrega o nome do branch na mensagem.

## Histórico

- **I7** — atendido

`commitar_tentativa` faz um `git add -A -- . :!.sle/loop*.jsonl` seguido de um único `commit`, então tudo que a tentativa mudou entra junto — `test_commit_de_tentativa_recolhe_tudo_num_commit_so` confere contagem de commits mais um e conjunto de arquivos igual a `{a.py, b.py}`. Assunto e trailer são conferidos literalmente contra `--format=%s` e `%b`: `loop(alfa): codificar tentativa 2` e `SLE-Loop: alfa#2`. A exclusão da escrituração tem teste próprio, e `test_o_rebase_posterior_acha_os_commits_do_loop` fecha o contrato pelo lado de quem vai usá-lo, com `git log --grep=^SLE-Loop:` achando as duas tentativas — que é a régua nomeada no contrato técnico.

- **I8** — atendido

Depois do `add`, `git diff --cached --name-only` vazio faz retornar `None` antes de qualquer `commit`. `test_tentativa_sem_mudanca_nao_gera_commit_vazio` verifica as duas consequências: retorno `None` e contagem de commits inalterada. Não há `--allow-empty` no módulo.

- **I9** — atendido

Os únicos subcomandos que o módulo emite são `rev-parse`, `symbolic-ref`, `status`, `add` e `commit` — nada que saia da máquina ou toque commit existente. `test_modulo_nao_reescreve_historico_nem_publica` transforma isso em régua estrutural, lendo o próprio fonte e proibindo `push`, `--amend`, `rebase`, `filter-branch`, `reset --hard`, `--force`, `cherry-pick` e `commit-tree`. Critério negativo tem evidência negativa; a leitura do módulo inteiro confirma o que o teste afirma.

- **I10** — atendido

`head` devolve `rev-parse HEAD` e o teste o compara com o git direto. `test_head_muda_depois_do_commit_e_o_anterior_serve_de_base` cobre a segunda metade: o SHA muda após a tentativa, e o `diff base..HEAD` mostra exatamente o arquivo da tentativa — quer dizer, o valor de antes serve mesmo de ref base. O critério exclui explicitamente a sequência (quando capturar), e o módulo não a assume: `head` é consulta pura, sem estado guardado.
