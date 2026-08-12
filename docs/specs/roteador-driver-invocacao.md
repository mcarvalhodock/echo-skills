# roteador-driver-invocacao

## Intenção
A fronteira entre o loop e o mundo — processo, exit code e histórico do alvo — fica isolada e testável sem chamar LLM e sem sujar repositório real.

## Depende de
`roteador-nucleo` — os tipos da decisão.

## Critérios

**Processo**

- [ ] **I1** `[plataforma]` — Cada fase é invocada em processo novo. Duas fases nunca compartilham sessão, nem quando a segunda é retentativa da primeira.
- [ ] **I2** `[integração]` — O invocador é injetável: a suíte exercita o caminho inteiro sem chamar `claude`.
- [ ] **I3** `[integração]` — O texto de retorno da fase é registrado e nunca interpretado. O resultado de uma invocação é exit code mais existência do artefato esperado, e nada além disso.
- [ ] **I4** `[plataforma]` — Exit code não-zero, ou artefato esperado ausente, produz falha explícita. Nenhuma combinação produz sucesso silencioso.

**Guardas antes de começar**

- [ ] **I5** `[plataforma]` — Working tree do alvo sujo no início do ciclo faz o driver recusar-se a começar, nomeando os arquivos sujos. **A escrituração do próprio loop (`.sle/loop*.jsonl`) não conta como sujeira** — ela é escrita pelo loop, e contá-la o impediria de rodar duas vezes seguidas no mesmo alvo.
- [ ] **I6** `[plataforma]` — Alvo posicionado no branch default (`main`/`master`) faz o driver recusar-se a começar.

**Histórico**

- [ ] **I7** `[plataforma]` — Concluída com sucesso uma invocação de `codificar`, tudo que mudou no alvo **exceto a escrituração do loop** vira **um** commit, com assunto `loop(<spec>): codificar tentativa <n>` e trailer `SLE-Loop: <spec>#<n>`. O commit é da demanda; o registro é escrituração.
- [ ] **I8** `[plataforma]` — Invocação de `codificar` que não muda arquivo nenhum não gera commit vazio.
- [ ] **I9** `[plataforma]` — O driver nunca faz push, nunca faz amend e nunca reescreve commit existente.
- [ ] **I10** `[plataforma]` — O SHA de `HEAD` do alvo é legível, e muda após um commit de tentativa. **Quando** capturá-lo como ref base é do laço (`D8` da `roteador-driver`): sequência não se observa daqui, e um critério assim faria esta spec depender de quem vem depois.

## Contrato técnico

- **Nenhum teste chama `claude`.** O invocador entra por parâmetro; a suíte passa um falso. Teste que depende de LLM não é régua, é aposta.
- Os testes de git operam em repositório temporário criado pela própria suíte. Nada toca o repositório do método.
- Invocação real: `claude -p` headless, um processo por fase, com o cwd no alvo.
- **Assunto e trailer são contrato, não estilo.** O ciclo produz um commit por tentativa, inclusive das que falharam, e o rebase posterior que os limpa precisa achá-los por padrão fixo. `git log --grep='^SLE-Loop:'` é a régua.
- Branch default detectado por `git symbolic-ref refs/remotes/origin/HEAD`, com fallback para os nomes `main` e `master` quando não há remoto.
- Este módulo é impuro por definição; `roteador.py`, `lote.py`, `veredito.py`, `secoes.py` e `dependencia.py` continuam sem disco e sem relógio.

## Fora de escopo

- **O laço** — quem decide o que invocar é a `roteador-driver`. Esta spec entrega a capacidade de invocar e de registrar no histórico, não a ordem.
- **Push, PR e qualquer coisa que saia da máquina** — o loop roda sozinho; publicar não.
- **Limpar o histórico** — o rebase que junta os commits de tentativa é operação humana, depois. O driver só garante que eles sejam encontráveis.
- **Commit após `verificar` ou `homologar`** — essas fases não mudam código de produção; se mudarem, é defeito e aparece na guarda de working tree sujo do ciclo seguinte.

## Plano

1. `tooling/loop/git_alvo.py` — guardas (I5, I6), commit marcado (I7, I8, I9) e leitura de `HEAD` (I10).
2. `tooling/loop/invocacao.py` — invocador injetável e resultado da invocação (I1, I2, I3, I4).
3. `tooling/loop/tests/test_git_alvo.py` e `test_invocacao.py`, com repositório temporário e invocador falso.

A ordem é por dependência real: a invocação de `codificar` termina em commit, e o commit é do módulo de git.

## Perguntas em aberto

Nenhuma.
