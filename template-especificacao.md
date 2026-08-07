# Template de Especificação — Fases Definir e Desenhar do SLE

> Este template é usado pela skill [`designer`](./designer/SKILL.md), que conduz as Fases Definir e Desenhar do método SLE (Spec Loop Engineering). Serve tanto pra uso manual (copiar e preencher) quanto como referência de como a skill conduz a conversa.

Regra de escala: **o tamanho da spec acompanha o risco da tarefa, não a vontade de ir rápido.** Por isso são 3 níveis. Escolha um antes de começar — a escolha em si já é uma decisão consciente, não um atalho.

Regra de fechamento: **nenhuma spec é considerada pronta com decisão técnica pendurada** — nem no meio do texto, nem como observação depois dela. Se, ao preencher, surgir uma decisão que depende de você (qual datasource, onde salvar, qual porta), resolva na hora e escreva a resposta no campo — nunca deixe como pergunta solta pro final.

Regra de falsificabilidade (SLE, gate obrigatório em N2 e N3): **cada critério de aceite e cada cláusula do contrato arquitetural precisa ser falsificável.** Antes de fechar, aplique o gate: *"como esse item é falsificado? descreva concretamente o teste ou verificação que, se falhar, prova que este item não foi atendido."* Itens que "sempre passam", que dependem de julgamento não-verificável, ou que usam frases vagas ("é seguro", "é performático", "é limpo") sem critério concreto — são rejeitados. Reformule antes de fechar.

---

## Nível 1 — Micro (tarefas de minutos, baixo risco, reversíveis)

Cole isso direto no prompt ou num comentário do ticket. Se não conseguir preencher em 1 minuto, não é nível 1.

```
Intenção:
Pronto quando:
Fora de escopo:
```

---

## Nível 2 — Padrão (a maioria das tarefas do dia a dia)

```markdown
## Spec: [nome da tarefa]

### Intenção
[Uma frase: o comportamento esperado, não a implementação]

### Contexto
[Por que isso é necessário agora — 1-2 frases. Se não souber, é sinal de que a Fase Definir ainda não terminou.]

### Critérios de aceite (comportamento — BDD-flavored)
- [ ] Dado [X], quando [Y], então [Z]
- [ ] ...

(cada um precisa passar o gate de falsificabilidade — se não dá pra falsificar concretamente, está vago demais)

### Contrato arquitetural
[Cláusulas explícitas sobre decisões estruturais que precisam ser respeitadas pela implementação: dependências obrigatórias, patterns exigidos, formatos de dados, interfaces expostas. Cada cláusula precisa ser falsificável — se não pode virar teste de contrato, é intenção comportamental disfarçada e deve ir na seção de critérios de aceite.]
- [ ]
- [ ]

Se a tarefa não tem cláusulas arquiteturais explícitas (comum em N2), declare literalmente ("Sem cláusulas arquiteturais explícitas") em vez de omitir a seção.

### Casos de borda considerados
-
-

### Domínios envolvidos
[Classifique **cada** critério de aceite, **cada** cláusula do contrato arquitetural e **cada** caso de borda acima em uma de três opções. Catálogo canônico e regras em [`dominios.md`](./dominios.md) — não invente nome fora dele. Se o repositório tiver `.sle/manifesto.md` (ou `.echo/manifesto.md` como alias legado), use só os domínios ativos lá.]

| item | classificação |
|---|---|
| [critério, cláusula ou caso de borda] | `dominio` / cross-cutting retido / miolo |

- **domínio** — pertence a uma disciplina do catálogo, candidato a delegação a especialista
- **cross-cutting retido** — toca vários domínios de forma inseparável; **não se delega**, fica com o orquestrador
- **miolo** — regra de negócio, comportamento central; fica com o dono da demanda

Marcar tudo como `miolo` é resultado legítimo, não erro de preenchimento. Domínio listado sem nenhum item apontando pra ele é sinal de decomposição vaga — refine antes de fechar.

### Fora de escopo
[O que a IA/você NÃO deve fazer aqui, mesmo que pareça relacionado]

### Restrições
[Performance, compatibilidade, convenção do projeto, segurança — só o que for relevante]

### Ambiente / destino
[Onde isso roda ou é salvo, se relevante — pasta/repo de destino, datasource, porta, variável de ambiente. Se a resposta depende de uma escolha sua, resolva agora e preencha com a decisão — não deixe em branco.]

### Nível de risco
[ ] Reversível fácil (deploy trivial de desfazer)
[ ] Difícil de reverter (migração, dado, API pública) → considerar Nível 3
```

---

## Nível 3 — Complexo (features de dias/semanas, mudança arquitetural, dado sensível, difícil de reverter)

Tudo do Nível 2 — incluindo o **contrato arquitetural obrigatório** (não pode ficar vazio em N3) e a seção **Domínios envolvidos** — mais:

```markdown
### Alternativas consideradas
[Pelo menos uma alternativa de design e por que foi descartada — obriga você a pensar antes de comprometer]

### Dependências e impacto
[O que mais no sistema é afetado, direta ou indiretamente]

### Plano de verificação
[Como vai ser testado além de teste unitário — staging, canary, rollback plan]

### Decisão de reversibilidade
[Se der errado, qual é o caminho de volta, concretamente]

### Perguntas em aberto
[O que você genuinamente ainda não sabe — incerteza real de escopo/negócio, nomeada explicitamente. Isso é diferente de decisão técnica esquecida: aquela deve ser resolvida agora, não listada aqui.]

### Artefatos de fidelidade (opcional, apenas se prototipou e há aspectos observáveis a preservar)
[Só preencha se houver protótipo N3 preservado em `docs/specs/[nome]-prototipo/` e existirem aspectos visuais / de UX / de microinteração que precisam ser preservados no resultado final, mas que não cabem como critério BDD ou cláusula arquitetural.

Lista os aspectos, um por linha. Cada um pode virar teste de fidelidade (Camada 3) escrito pelo Validator.]

- Aspecto visual: [ex: "modal de confirmação com padding e sombra consistentes com o protótipo"]
- Aspecto de UX: [ex: "fluxo de 3 passos com breadcrumb visível em todas as etapas"]
- Microinteração: [ex: "transição entre passos com animação de 300ms; feedback de loading após submit"]

**Caminho do protótipo preservado:** `docs/specs/[nome]-prototipo/`

Se não houve protótipo ou nenhum aspecto de fidelidade merece preservação além do que já está em critérios/cláusulas, escreva "Sem artefatos de fidelidade" em vez de omitir a seção.
```

### Consolidação e spec enriquecida (Nível 3, apenas se prototipou)

Se, durante a Fase Desenhar, você prototipou (só permitido em N3):

- **Consolidação é obrigatória** — o aprendizado do protótipo é extraído em três destinos:
  - **Comportamentos aprendidos** → vão para esta spec, marcada como **spec enriquecida** (adicione seção "spec original — v1" preservando o texto original + seção "consolidação após protótipo — v2 em <data>"). Uma spec ativa por vez.
  - **Decisões arquiteturais** → viram cláusulas explícitas no plano da Fase Desenhar (na seção "Contrato arquitetural do desenho"), não aqui.
  - **Aspectos de fidelidade** (visuais, de UX, microinteração) → viram entradas na seção "Artefatos de fidelidade (N3)" acima.
- **Protótipo é preservado** (não descartado) em `docs/specs/[nome]-prototipo/`, com `README.md` no topo declarando que é código não-produção, apenas referência de fidelidade. Isso permite ao Executor implementar do zero (sem copiar código) preservando o observável, e ao Validator escrever testes de fidelidade (Camada 3) na Fase Traduzir.

---

## Exemplo preenchido (Nível 2, pra calibrar o "tamanho certo")

```markdown
## Spec: Endpoint de cancelamento de assinatura

### Intenção
Usuário autenticado consegue cancelar a própria assinatura via API, com efeito imediato no fim do ciclo pago.

### Contexto
Hoje o cancelamento só é feito manualmente pelo suporte — está gerando fila e reclamação.

### Critérios de aceite
- [ ] Dado usuário autenticado com assinatura ativa, quando POST /subscriptions/cancel, então assinatura marcada como `cancel_at_period_end`
- [ ] Dado usuário sem assinatura ativa, quando POST /subscriptions/cancel, então HTTP 404 com body `{ code: "no_active_subscription" }`
- [ ] Dado usuário autenticado que cancelou, quando fim do período pago, então status muda para `canceled` e cobrança futura é bloqueada
- [ ] Dado cancelamento aceito, quando processamento concluído, então e-mail de confirmação enviado com template `subscription_canceled`

### Contrato arquitetural
- [ ] Endpoint respeita padrão de erro já usado nos outros endpoints do serviço (formato `{ code, message, details }`)
- [ ] Nenhuma nova dependência de biblioteca externa é introduzida
- [ ] Webhook de billing existente permanece funcional (verificado por teste de integração já presente na suíte)

### Casos de borda considerados
- Usuário sem assinatura ativa tenta cancelar
- Assinatura já cancelada, tentativa duplicada
- Cancelamento no mesmo dia da renovação

### Domínios envolvidos

| item | classificação |
|---|---|
| Cancela apenas a própria assinatura | `segurança` |
| Assinatura marcada como cancel_at_period_end | miolo |
| Cobrança futura bloqueada no fim do período | miolo |
| E-mail de confirmação enviado | `integração` |
| Padrão de erro consistente com outros endpoints | miolo |
| Nenhuma dependência nova | `plataforma` |
| Webhook de billing permanece funcional | cross-cutting retido |

Leitura: majoritariamente miolo, com dois aspectos delegáveis (segurança da posse; integração de e-mail) e um cross-cutting (webhook de billing toca posse, consistência de estado e integração). O cross-cutting não fatia — a regra de corte, o registro e o webhook são a mesma decisão.

### Fora de escopo
- Reembolso proporcional (feature separada)
- Cancelamento por admin/suporte (já existe, não mexer)

### Restrições
- Não pode quebrar o webhook de billing existente
- Seguir padrão de resposta de erro já usado nos outros endpoints

### Ambiente / destino
- Endpoint novo no serviço `billing-api` existente, pasta `src/controllers/subscription`
- Usa o mesmo banco de produção já configurado nesse serviço (não é boilerplate novo)

### Nível de risco
[x] Difícil de reverter (mexe em cobrança) → tratado com atenção reforçada de revisão, mesmo mantido como Nível 2
```

---

## Como usar isso na prática

1. Salve este arquivo em algum lugar fixo — `docs/spec-template.md` no repo é uma boa escolha, porque fica versionado junto com o código que ele vai gerar.
2. Antes de qualquer prompt pra IA, copie o nível adequado, preencha, e só depois abra o chat — cole a spec preenchida como parte do prompt ou referencie o arquivo. Se estiver usando a skill `designer`, ela conduz esse preenchimento com você, campo por campo.
3. Depois da Fase Observar, se algo quebrou que a spec não previu, volte aqui e adicione como pergunta padrão pro seu próximo preenchimento — o template também é um documento vivo.

---

*Este template alimenta as Fases Definir e Desenhar do [método SLE](./metodologia-sle.md). Depois de especificado e desenhado, o próximo passo é a skill [`validator`](./validator/SKILL.md), que traduz a spec em testes (Fase Traduzir) antes de qualquer código ser escrito.*
