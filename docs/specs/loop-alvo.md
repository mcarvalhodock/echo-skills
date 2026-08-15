# loop-alvo

## Intenção
O alvo passa a ser uma **subárvore**, não um repositório: o loop roda num pacote de monorepo sem tropeçar no trabalho dos outros times, e roda numa pasta sem git em modo degradado em vez de estourar.

## Depende de
`roteador-driver` e `roteador-driver-invocacao` — são elas que falam com o git e montam o prompt.

## Critérios

**Forma do alvo**

- [ ] **T1** `[plataforma]` — Alvo que não existe resulta em `escalar` nomeando o caminho procurado. Nunca em stack trace.
- [ ] **T2** `[plataforma]` — Alvo que não é repositório git roda em **modo degradado**, avisando **uma vez** o que deixa de existir: commit por tentativa e diff.
- [ ] **T3** `[plataforma]` — Em modo degradado nenhuma operação de git é tentada — nem guarda, nem commit, nem leitura de `HEAD`.
- [ ] **T4** `[integração]` — Em modo degradado o prompt de `verificar` pede leitura contra o **estado atual** do alvo, não contra diff, e não passa ref base.

**Subárvore**

- [ ] **T5** `[plataforma]` — A guarda de sujeira considera só a subárvore do alvo. Arquivo sujo fora dela não impede o ciclo de começar.
- [ ] **T6** `[plataforma]` — Alvo que é a raiz do repositório mantém o comportamento atual: a subárvore é o repositório inteiro.
- [ ] **T7** `[integração]` — O prompt de `verificar` limita o diff à subárvore do alvo, e o molde da leitura limpa carrega esse limite.
- [ ] **T8** `[plataforma]` — O commit de tentativa recolhe só o que mudou dentro da subárvore.
- [ ] **T9** `[plataforma]` — Duas subárvores irmãs do mesmo repositório não interferem: rodar em `packages/a` não commita nem reporta nada de `packages/b`.

## Contrato técnico

- **Identificadores começam em `T` de propósito.** `criterion_coverage` mantém um conjunto **global** de IDs cobertos: um `spec:A1` escrito para esta spec marcaria como coberto o `A1` de `docs/specs/instaladores-sle.md`. Enquanto essa ferramenta não separar por spec, prefixo repetido apaga lacuna alheia.
- Detecção: `git rev-parse --show-toplevel` com o cwd no alvo. Falhou, não é git — e essa é a única sonda; nada de procurar `.git` subindo diretórios à mão.
- Subárvore = caminho do alvo relativo ao toplevel; alvo na raiz dá `.`, e o comportamento é o de hoje.
- O limite entra como pathspec no `status` e no `diff`, não como filtro em Python depois: quem sabe separar caminho de repositório é o git.
- **O molde da leitura limpa ganha duas variantes** — com diff e com estado atual. É custo aceito e o segundo desvio no molde desde que ele existe; os dois vieram de rodar, não de projetar. `verificar` passa a declarar o escopo entre os insumos.
- Modo degradado avisa **uma vez**, na abertura. Avisar a cada fase treina a pessoa a ignorar o aviso.
- O registro (`.sle/loop*.jsonl`) e o teto continuam funcionando sem git: eles nunca dependeram dele.

## Fora de escopo

- **Rodar `git init` no alvo.** Criar repositório no diretório de outra pessoa sem pedir é o tipo de mágica que se descobre tarde. O aviso do `T2` diz o que fazer; fazer é decisão de quem roda.
- **VCS que não seja git.** Nenhum outro está em uso aqui, e suportar o que ninguém usa é peso sem retorno.
- **Vários alvos numa execução.** Uma fase por vez já é regra; dois alvos multiplicariam o problema sem resolver nenhum.
- **Namespace de identificador de critério por spec.** É defeito do `criterion_coverage`, não desta demanda — aqui só se desvia dele.

## O que a degradação custa, declarado

Sem diff, a leitura limpa julga o estado atual do alvo. Critério satisfeito por código que já existia **antes** da demanda é lido como atendido — o que é literalmente verdade, e ainda assim esconde que a demanda pode não ter feito nada. É a diferença entre "isto é verdade" e "isto passou a ser verdade", e em modo degradado só a primeira é observável.

## Plano

1. `tooling/loop/git_alvo.py` — detecção de toplevel e de não-git, subárvore, guarda e commit escopados (T1, T3, T5, T6, T8, T9).
2. `tooling/loop/driver.py` — modo degradado, aviso único e escopo no prompt (T2, T4, T7).
3. `verificar/SKILL.md` — o escopo entra nos insumos e o molde ganha a variante sem diff (T4, T7).
4. `tooling/loop/tests/test_git_alvo.py` e `test_alvo.py`, com repositório temporário, monorepo temporário e pasta sem git.

## Perguntas em aberto

Nenhuma.
