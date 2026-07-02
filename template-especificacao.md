# Template de Especificação — Fase E do ECHO

> Este template é o mesmo usado pela skill [`especificar`](./skills/especificar/SKILL.md). Serve tanto pra uso manual (copiar e preencher) quanto como referência de como a skill conduz a conversa.

Regra de escala: **o tamanho da spec acompanha o risco da tarefa, não a vontade de ir rápido.** Por isso são 3 níveis. Escolha um antes de começar — a escolha em si já é uma decisão consciente, não um atalho.

Regra de fechamento: **nenhuma spec é considerada pronta com decisão técnica pendurada** — nem no meio do texto, nem como observação depois dela. Se, ao preencher, surgir uma decisão que depende de você (qual datasource, onde salvar, qual porta), resolva na hora e escreva a resposta no campo — nunca deixe como pergunta solta pro final.

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
[Por que isso é necessário agora — 1-2 frases. Se não souber, é sinal de que a Fase E ainda não terminou.]

### Critérios de aceite
- [ ]
- [ ]
- [ ]
(cada um precisa virar teste depois — se não dá pra testar, está vago demais)

### Casos de borda considerados
-
-

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

Tudo do Nível 2, mais:

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
```

---

## Exemplo preenchido (Nível 2, pra calibrar o "tamanho certo")

```markdown
## Spec: Endpoint de cancelamento de assinatura

### Intenção
Usuário autenticado consegue cancelar a própria assinatura via API, com efeito imediato no fim do ciclo pago.

### Contexto
Hoje o cancelamento só é feito manualmente pelo suporte — está gerando fila e reclamação.

### Critérios de aceite
- [ ] Usuário autenticado cancela apenas a própria assinatura
- [ ] Assinatura permanece ativa até o fim do período já pago
- [ ] Cobrança futura é bloqueada
- [ ] Usuário recebe confirmação por e-mail

### Casos de borda considerados
- Usuário sem assinatura ativa tenta cancelar
- Assinatura já cancelada, tentativa duplicada
- Cancelamento no mesmo dia da renovação

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
2. Antes de qualquer prompt pra IA, copie o nível adequado, preencha, e só depois abra o chat — cole a spec preenchida como parte do prompt ou referencie o arquivo. Se estiver usando a skill `especificar`, ela conduz esse preenchimento com você, campo por campo.
3. Depois da Fase O (Observar), se algo quebrou que a spec não previu, volte aqui e adicione como pergunta padrão pro seu próximo preenchimento — o template também é um documento vivo.

---

*Este template alimenta a Fase E do [método ECHO](./metodologia-echo.md). Depois de especificado, o próximo passo é a skill [`planejar`](./skills/planejar/SKILL.md).*
