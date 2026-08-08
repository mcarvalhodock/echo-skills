# Método SLE — Spec Loop Engineering
### Uma disciplina para unir rigor de engenharia e velocidade de IA, com invariantes que aguentam pressão

> Prompt não é trabalho. Prompt é intenção. O trabalho é o que acontece entre a intenção e o sistema que sobrevive em produção — e é aí que a estrutura precisa segurar quando o cansaço bate.

> **Status: em teste, v2 do método.** Sucessor do ECHO. Documento vivo — trate como hipótese bem fundamentada, não como regra pronta. A tese completa que originou esta versão está em [`propostas/spec-loop-engineering.md`](./propostas/spec-loop-engineering.md).

---

## Por que "SLE"

**Spec** — o contrato é a única fonte de verdade. Especificação primeiro, sempre.

**Loop** — não é linear. Cada tarefa entrega dados sobre a próxima. O que aprendemos na execução realimenta o desenho.

**Engineering** — disciplina de longo prazo, não atalho tático. Regras que sobrevivem à pressa.

Seis fases:

**D**efinir → **D**esenhar → **T**raduzir → **I**mplementar → **H**omologar → **O**bservar

Distribuídas em quatro skills — nunca uma skill faz mais do que seu papel:

| Skill | Fases | Papel |
| --- | --- | --- |
| `designer` | Definir + Desenhar | Spec, contrato arquitetural, protótipo N3 (não escreve código de produção) |
| `validator` | Traduzir + Homologar | Testes (BDD + contrato + fidelidade) ou plano manual; homologação (não implementa nem projeta) |
| `executor` | Implementar | Código de produção que passa nos testes existentes (não desenha nem valida) |
| `observer` | Observar | Sinais, drift, propostas de reconciliação (independente das outras) |

---

## As 4 invariantes

O método inteiro se apoia em regras que **não são aspiracionais**. Elas são verificadas por hooks in-session (`tooling/hooks/`) e por CI (`tooling/ci/`):

1. **Designer ≠ Executor.** Quem desenha (spec, contrato arquitetural, protótipo) não escreve código de produção. Bloqueado pelo hook `block-designer-writing-code`.
2. **Ninguém assina o que escreveu (v5).** Quem implementa não atesta a própria implementação. Escrever e atestar são atos distintos, e é o segundo que a invariante protege — o primeiro pode ser dirigido pelo humano quando corrigir é mais barato que cerimoniar.
3. **Nenhum agente é árbitro.** Decisões arquiteturais, disciplinares e de trade-off ficam com o humano em pontos explícitos ("gates").
4. **Observer é independente.** Quem observa e propõe reconciliações não é quem executou o que está sendo observado.

Se uma dessas invariantes é violada em silêncio, o método degrada — e degrada primeiro na direção que menos dói no curto prazo (aceitar a spec vaga, deixar o executor "consertar" o teste, homologar sem revisar).

**Sobre a invariante 2, que mudou na v5.** Ela dizia "Executor ≠ Validator: quem implementa não escreve os testes que validam a própria implementação", e era enforçada pelo hook `block-validator-writing-code`, que proibia o Validator de tocar em path de produção. O eixo estava errado: a proibição de *escrever* gerava cerimônia sem comprar segurança, e a de *atestar* — que é a que sustenta o generator/evaluator separation — ficava implícita. A v5 troca o eixo, e o hook acompanhou: ele passou a bloquear a escrita **sem emenda declarada e registrada** em vez de bloquear a escrita. O que ele verifica é o registro da dívida de atestação; quem assina é humano. Ver `tooling/hooks/block-validator-writing-code/README.md`.

Uma atestação não-independente **não bloqueia** a entrega: ela é dívida declarada, paga depois com uma passagem curta de outra sessão sobre o critério afetado. O que ela não pode ser é silenciosa.

---

## Regra de ouro

**Nenhuma linha de código antes de existir contrato; nenhum teste antes de existir spec traduzível; nenhuma implementação antes de existir teste (ou plano manual aprovado); nenhuma tarefa "pronta" sem verificação real e revisão humana.**

Tamanho escala com o risco:

- **N1 (micro):** spec de 5 linhas. Pula Desenhar. Pode ter TDD manual se codebase não sustenta.
- **N2 (padrão):** spec completa + contrato arquitetural. TDD ortodoxo ou parcial declarado no manifesto.
- **N3 (complexo):** spec enriquecida + contrato arquitetural + **protótipo preservado como artefato de fidelidade** (não descartado). Testes de fidelidade compõem a Camada 3 do Validator.

---

## Fase 1 — Definir (D)

**Objetivo:** transformar intenção vaga em contrato verificável.

O que a skill `designer` conduz:

- **O que**, em uma frase — comportamento esperado, não implementação.
- **Critérios de aceite** — cada um vai virar teste (ou item de plano manual) na próxima fase. Se um critério não pode virar verificação concreta, ele volta para reescrita.
- **Casos de borda** previsíveis, marcados por domínio em N2+.
- **Escopo negativo** — o que fica de fora.
- **Restrições não-funcionais** — performance, compatibilidade, segurança, convenção local.
- **Ambiente/destino** — onde roda, onde é salvo.

**Marcação por domínio (N2+):** cada critério e caso de borda é classificado como pertencente a um domínio, cross-cutting retido, ou miolo. Catálogo em [`dominios.md`](./dominios.md).

**Falsifiability gate:** a spec só é considerada pronta se cada critério pode ser objetivamente falseado (existe uma observação que provaria que o critério não foi atendido). Isso é checado pelo Designer antes do handoff, e reforçado pelo Validator na Fase T.

**Regra de fechamento:** decisão técnica pendurada = spec incompleta. Se surge dúvida durante o preenchimento, resolve na hora (com humano se for arquitetura), não vira TODO.

---

## Fase 2 — Desenhar (D)

**Objetivo:** dar precisão ao *como*, sem escrever código de produção.

O que a skill `designer` conduz nesta fase (só existe em N2 e N3):

- **Contrato arquitetural** — componentes, interfaces, invariantes de dados, decisões de trade-off resolvidas com base na spec. Também deve ser falsificável (cada cláusula precisa poder virar teste na Fase T).
- **Protótipo (só N3)** — código exploratório salvo em `docs/specs/<nome>-prototipo/`. Não é descartado (mudança v2 do método). Fica disponível como referência não-copiável para o Executor e como base para os testes de fidelidade do Validator.

**Handoff estrutural:** Fase D termina explicitando qual skill vem depois (`validator`), em qual sessão nova ela precisa rodar, e quais artefatos são passados como input (spec + contrato + protótipo se N3).

**Sinal de alerta:** designer tentando escrever código de produção "só um pouquinho" para testar. Isso é violação da invariante 1 — o hook bloqueia; se não bloquear, o CI pega no PR.

---

## Fase 3 — Traduzir (T)

**Objetivo:** transformar cada cláusula da spec em verificação concreta, antes de qualquer linha de código de produção.

O que a skill `validator` conduz nesta fase:

- **Camada 1 (BDD):** cada critério de aceite vira teste com formato Given/When/Then (ou equivalente na tech-stack).
- **Camada 2 (contrato arquitetural):** cada cláusula do contrato vira teste de invariante estrutural.
- **Camada 3 (fidelidade, só N3):** testes que confrontam a implementação com o protótipo preservado. O Validator tem acesso ao protótipo nesta fase.

**TDD contextualizado (v3 do método):** o manifesto local (`.sle/manifesto.md`) declara `tdd-aplicavel`:

- `ortodoxo` — tudo é teste automatizado. Camadas 1/2/3 obrigatórias.
- `parcial` — o que der, automatiza; o que não der, plano manual estruturado.
- `manual` — codebase legada onde TDD é inviável. Cria plano de validação manual (`docs/specs/<nome>-manual-validation.md`) com ações concretas, inputs esperados e evidências anexáveis. **Não existe critério "coberto por nada"**: se não vira teste, vira item explícito no plano manual.

**Poder estrutural (v2/v4):** se o Validator descobre que a spec é vaga a ponto de não conseguir escrever teste, ele **retorna estruturalmente para o Designer** (registra no log, sinaliza a spec como insuficiente). Se descobre bug semântico em um teste que o Executor tentou consertar sem alterar semântica, também tem poder de retorno.

**Emenda (v5):** retorno serve para spec que ainda não dá para traduzir, e para desenho que se mostrou errado inteiro. Para **spec que estava certa até o mundo mostrar o contrário**, o movimento é emendar: altera-se o critério, a régua ou o código; roda-se de novo só o que foi tocado; registra-se uma linha em `.sle/pressao-metodo.md`. Não volta fase, não reinicia ciclo, e vale **em qualquer fase, inclusive na Homologar, inclusive depois do verde**. Detalhe operacional na skill `validator`, seção "Emenda".

---

## Fase 4 — Implementar (I)

**Objetivo:** escrever código de produção fiel à spec, aos testes existentes e (em N3) ao protótipo — sem redesenhar, sem validar a si mesmo.

O que a skill `executor` conduz:

- Lê spec, contrato arquitetural, testes já escritos, e (em N3) protótipo como referência não-copiável.
- Implementa código estritamente para passar nos testes ou executar o plano manual.
- Pode fazer **refactor não-semântico** em testes (v4 do método): DRY, extração de fixtures, renomeação interna — desde que o hook `block-executor-writing-tests-semantically` confirme que a semântica (nomes de testes + hash agregado das assertions) permaneceu equivalente entre antes e depois.
- Não pode adicionar/remover teste, mudar assertion, ou desviar do contrato arquitetural. Se detectar bug semântico em teste, **retorna estruturalmente para o Validator**.

**Clean Code universal (v4):** o padrão de qualidade se aplica igualmente a código de produção e a código de teste. "Bom código de teste" é declarado no manifesto local — cada projeto define o próprio, dentro do razoável.

**Sinal de alerta:** re-prompting da mesma tarefa pela terceira vez tentando "acertar". Isso quase sempre significa que a spec ou o teste estavam ambíguos — retorno estrutural para a fase anterior, não insistência no prompt.

---

## Fase 5 — Homologar (H)

**Objetivo:** provar, com evidência, que o código atende ao contrato.

O que a skill `validator` conduz (mesma skill que Traduzir, agora em modo Homologar):

- Roda a suíte automatizada. Se falha, retorna para Executor.
- Executa o plano de validação manual (v3), anexando as evidências pedidas.
- Conduz **checklist de revisão arquitetural** — perguntas que o humano responde, o Validator não responde por ele. É o "músculo" que se treina aqui.
- Fecha o log de homologação (`docs/specs/<nome>-log.md`) com resultado real, não "deve ter funcionado".

**Isolamento em N3:** durante Homologar, o Validator **não** tem acesso ao protótipo (só na Fase T tinha). Isso evita que a homologação vire "conferir se o código bateu com o protótipo" — o protótipo é referência de fidelidade, não critério de aceite.

**Sinal de alerta:** revisão arquitetural marcada como "ok" sem ter sido respondida de verdade. Esvazia a fase e degrada o método na direção que menos dói no curto prazo.

---

## Fase 6 — Observar (O)

**Objetivo:** fechar o loop — aprender com o que aconteceu depois da entrega, e alimentar isso de volta em specs futuras.

O que a skill `observer` conduz:

Dois modos operacionais:

- **Event-driven** — bug de produção, drift entre spec e código, feedback qualitativo. Observer analisa, propõe reconciliação da spec, registra padrão em `.sle/pressao-metodo.md`.
- **Cadence-driven** — retrospectiva semanal/quinzenal. Observer varre pressão-método e pressão-catálogo, identifica padrões emergentes, propõe ajustes no template ou nos domínios.

**Saída estritamente propositiva:** o Observer nunca decide sozinho. Todo output é uma sugestão que o humano avalia e aceita/adapta/rejeita. Reservado exclusivamente ao humano: "calibração disciplinar" (medir se a pessoa está mesmo seguindo o método, ou entrando em modo atalho).

**Isolamento:** Observer não é a mesma skill que executou o trabalho observado. Isso preserva a invariante 4 e evita "avaliar o próprio serviço".

---

## Por que 4 skills e não 6

A tentação é ter uma skill por fase (`definir`, `desenhar`, `traduzir`, `implementar`, `homologar`, `observar`). A tese que originou o SLE argumenta que isso *fragmenta demais* — o custo de handoff estrutural entre "definir" e "desenhar" (ambos feitos pelo mesmo papel de Designer, no mesmo horizonte temporal) supera o benefício de granularidade.

A decisão final foi: **skill agrupa por papel, não por fase**. Papel é o que a invariante protege; fase é o que a disciplina organiza.

---

## Enforcement em duas camadas

O método não confia apenas na obediência do humano ou do modelo:

**Camada 1 — Hooks in-session** (`tooling/hooks/`)

- Bloqueia a operação no momento em que o agente tenta violar a invariante.
- Depende do harness (Claude Code, Cursor, etc.) suportar hooks e expor identidade do papel ativo.
- Tempo de detecção: imediato.

**Camada 2 — CI de repositório** (`tooling/ci/`)

- Verifica no PR: paridade spec/teste, cobertura de critério, coerência entre mudança de código e mudança de spec.
- Independente do harness — funciona mesmo se a Camada 1 falhar.
- Tempo de detecção: no PR, antes do merge.

As duas camadas se complementam. Um enforcement é sempre "esforço mínimo suficiente", nunca "policiamento completo" — o objetivo é que o método sobreviva em dia ruim, não que substitua julgamento humano.

---

## Por que isso é replicável em qualquer plataforma

O método não depende de nenhuma feature específica de nenhuma ferramenta. Cada fase mapeia para qualquer ambiente:

| Fase | Implementação neste repo (Claude Code) | Qualquer outra ferramenta |
| --- | --- | --- |
| Definir + Desenhar | skill `designer` | Documento de spec + contrato + prototipo (protótipo em pasta separada) versionados |
| Traduzir | skill `validator` (fase T) | Escrever testes + plano manual antes de qualquer código |
| Implementar | skill `executor` | Prompt/agente focado em passar nos testes existentes |
| Homologar | skill `validator` (fase H) | Rodar suíte + executar plano manual + revisão arquitetural humana |
| Observar | skill `observer` | Retro pessoal periódica + atualização de template + registro em log de pressão |

A ferramenta muda. O contrato entre intenção, execução e verificação, não.

---

## Checklist rápido (cole no seu fluxo)

- [ ] A spec está falsificável (cada critério tem uma observação que o prova ou refuta)?
- [ ] Em N2+, o contrato arquitetural cobre as decisões de trade-off?
- [ ] Em N3, existe protótipo preservado e vou usar como referência (não como cópia)?
- [ ] O TDD declarado no manifesto foi respeitado (ortodoxo/parcial/manual)?
- [ ] Se TDD é parcial/manual, existe plano de validação manual estruturado?
- [ ] Cada handoff entre skills é estrutural (nova sessão, artefatos explícitos)?
- [ ] O Executor não alterou semântica de teste sem retorno para Validator?
- [ ] A homologação rodou a suíte real e executou o plano manual, com evidência?
- [ ] A revisão arquitetural foi respondida de verdade, não marcada como "ok"?
- [ ] O Observer analisou os sinais e propôs reconciliação, e o humano decidiu?

---

*Documento vivo — revisado depois de aplicar em tarefas reais. Ajuste o que não encaixar; o método serve ao trabalho, não o contrário.*
