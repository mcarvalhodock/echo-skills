# roteador-driver-invocacao — veredito

Base: `git diff 7f3b7d5 -- tooling/loop/` (`git_alvo.py`, `invocacao.py`, `tests/test_git_alvo.py`, `tests/test_invocacao.py`).
Suíte dos dois arquivos rodada: **20 passed**.

- **I1** — atendido
- **I2** — atendido
- **I3** — atendido
- **I4** — atendido
- **I5** — atendido
- **I6** — atendido
- **I7** — atendido
- **I8** — atendido
- **I9** — atendido
- **I10** — não verificável

## Porquê

**I1 — processo novo por fase.** `invocar` monta o comando do zero a cada chamada e `executar_de_verdade` é um `subprocess.run` por invocação: não há objeto de sessão, handle persistente nem estado entre chamadas. `comando_de` devolve `("claude", "-p", prompt)` e nada mais — `test_nenhuma_invocacao_retoma_sessao` fixa a ausência de `--resume`, `--continue`, `-c` e `--session-id`, que é o que faria duas fases (ou uma retentativa) compartilharem sessão. A régua é estrutural, não observacional: `test_cada_invocacao_e_um_processo` só constata duas chamadas com comandos diferentes, e eles diferem porque os prompts diferem — não porque houve dois processos. Ainda assim a garantia se sustenta, porque não existe caminho no módulo que reaproveite processo.

**I2 — invocador injetável.** `invocar(..., executor=None)` cai em `executar_de_verdade` só quando ninguém passa nada; `test_invocacao.py` passa `ExecutorFalso` em todas as chamadas. Nenhum dos dois arquivos de teste executa `claude`, e o único ponto que o executaria (`executar_de_verdade`) nunca é chamado pela suíte. O caminho exercitado é o caminho inteiro do módulo — montagem do comando, cwd, exit code, checagem de artefato, `Resultado` — com o processo trocado na fronteira.

**I3 — texto registrado, nunca interpretado.** `Resultado.saida` guarda a string; `Resultado.ok` lê apenas `exit_code` e `artefato_presente`. Não há parsing, regex ou busca de palavra na saída em lugar nenhum do módulo. Os dois testes fecham o par: saída catastrófica com exit 0 dá `ok is True`, saída triunfalista com exit 1 dá `ok is False`. O texto não move nada.

**I4 — falha explícita.** `ok` é `False` para exit não-zero e para artefato esperado ausente, e há testes para exit 2, artefato ausente, artefato presente e artefato procurado no diretório errado (relativo ao alvo, não ao método). `presente = bool(artefato_esperado) and (Path(alvo)/artefato_esperado).exists()` combinado com `artefato_esperado is None or artefato_presente` fecha as bordas: sem artefato esperado, decide só o exit code; com artefato esperado inexistente, falha. Não há combinação que devolva `ok is True` sem exit 0. Duas ressalvas que não derrubam o critério: a combinação exit não-zero **com** artefato presente não tem teste próprio (o curto-circuito do exit code a cobre por construção), e a "falha explícita" aqui é um booleano no resultado, não uma exceção — quem a transforma em parada é o laço, que está fora de escopo.

**I5 — working tree sujo.** `sujos` lê `git status --porcelain` e corta as duas colunas de status, com o comentário explicando por que não são três — o corte errado comeria a primeira letra do nome quando índice e working tree estão ambos marcados. `impedimentos` transforma isso numa mensagem que **nomeia** os arquivos. O teste suja um arquivo novo e um rastreado e exige os dois nomes na mensagem; o caso limpo devolve `()`. Fica de fora o caminho com aspas do git (`core.quotepath`, nomes com espaço/acento), que voltaria escapado — degradação cosmética da mensagem, não falha da guarda.

**I6 — branch default.** `branch_default` tenta `git symbolic-ref refs/remotes/origin/HEAD` e pega o último segmento; sem remoto, cai no par `("main", "master")`. `impedimentos` compara com o branch atual e recusa. Testado por parametrização em `main` e `master`, em repositório sem remoto, e o caso feliz (`trabalho`) devolve `()`. O fallback é escrito de forma auto-referente — devolve o branch atual se ele for um dos dois nomes — o que dá o mesmo resultado da comparação pretendida; funciona, mas o ramo com remoto configurado não tem teste, porque a suíte não cria origin.

**I7 — um commit marcado.** `commitar_tentativa` faz `add -A` e um único `commit` com assunto `loop(<spec>): codificar tentativa <n>` e corpo `SLE-Loop: <spec>#<n>`. Três testes cobrem as três faces do critério: formato exato de assunto e trailer; contagem de commits +1 com os dois arquivos dentro do mesmo commit e tree limpa depois; e a régua do contrato técnico, `git log --grep='^SLE-Loop:'`, achando as duas tentativas. É a régua declarada na spec, rodando de verdade contra um repositório temporário.

**I8 — sem commit vazio.** Depois do `add -A`, o módulo checa `git diff --cached --name-only` e devolve `None` se estiver vazio, antes de chamar `commit`. O teste confirma retorno `None` e contagem de commits inalterada. Não há `--allow-empty` no arquivo.

**I9 — nunca push, amend ou reescrita.** Os únicos subcomandos usados no módulo são `rev-parse`, `symbolic-ref`, `status`, `add`, `diff` e `commit` sem flags de reescrita. O teste é estrutural — lê o próprio fonte e proíbe `push`, `--amend`, `rebase`, `filter-branch`, `reset --hard`, `--force`, `cherry-pick` e `commit-tree`. É a forma mais honesta disponível para uma proibição: não dá para testar a ausência de um efeito, só a ausência do verbo. Vale enquanto `_git` for chamado apenas de dentro do módulo com literais; é uma função pública o bastante para aceitar qualquer argumento de um chamador externo, e o teste não veria isso.

**I10 — ref base.** O que o diff entrega é `head(alvo)`, que devolve o SHA de `HEAD`, testado contra `git rev-parse HEAD` e testado de novo como base de um `diff base..HEAD` depois de uma tentativa. O que o critério pede além disso — que esse SHA seja capturado **antes da primeira invocação de `codificar` de uma spec** e devolvido **como ref base daquela spec** — não existe neste diff e não pode existir nele: `head` não conhece spec, não há armazenamento por spec, e a ordenação "antes da primeira" é decisão do laço, que a própria spec põe em "Fora de escopo". A capacidade está pronta e correta; o critério, como escrito, fala de um comportamento sequencial cujo dono não está aqui, então nada no diff o confirma nem o refuta.
