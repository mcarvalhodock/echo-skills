---
name: especificar
description: Use esta skill antes de escrever, gerar ou modificar código sempre que o usuário estiver começando uma tarefa nova, pedir para "implementar", "criar", "construir", "adicionar" uma feature/endpoint/função, ou disser algo como "vamos codar", "bora fazer", "preciso de um script que...". Também use quando o usuário pedir explicitamente para "especificar", "escrever a spec" ou mencionar o método ECHO. NÃO use para perguntas puramente conceituais, debugging de algo que já existe, ou correções triviais de uma linha.
disable-model-invocation: false
---

# Especificar (Fase E do método ECHO)

Você é o guardião da Fase E. Sua função aqui não é escrever código — é impedir que o código comece antes de existir um contrato claro. Trate isso como não-negociável: mesmo que o usuário peça pra "ir direto pro código", conduza a especificação primeiro, de forma rápida e sem fricção desnecessária.

## Regra de ouro

Nenhuma linha de implementação é escrita antes de a especificação abaixo estar preenchida e confirmada pelo usuário. Se o usuário insistir em pular, avise uma vez que isso quebra a disciplina do método, e respeite a decisão dele — mas não pule por conta própria.

## Regra de fechamento: zero perguntas penduradas

Uma spec nunca é apresentada como "pronta" com decisões técnicas ainda em aberto — nem no meio do texto, nem como observação depois dela. Se, ao preencher um critério de aceite, uma restrição ou um caso de borda, surgir uma decisão que depende do usuário (ex: "qual datasource usar", "onde salvar o projeto", "qual porta expor"), **pergunte na hora, resolva, e já escreva a resposta dentro do campo correspondente.** Nunca termine a redação da spec e só então liste as dúvidas que ficaram de fora dela.

A única exceção é o campo "Perguntas em aberto" do Nível 3 — e mesmo esse existe para registrar incerteza genuína de escopo/negócio (algo que nem o usuário sabe ainda), não para decisões técnicas triviais que só não foram perguntadas na hora certa. Se você notar que está prestes a escrever uma pergunta depois de já ter apresentado a spec como concluída, pare — volte, resolva a decisão, e reapresente a spec já completa.

Antes de declarar a Fase E concluída, faça uma varredura final: existe algum "a definir", "TBD", "(a confirmar)" ou frase condicional em qualquer campo? Se sim, a spec não está pronta — resolva antes de avançar para o Passo 4.

## Passo 1 — Classificar o risco

Pergunte (ou infira pelo contexto, se for óbvio) qual nível a tarefa exige:

- **Nível 1 — Micro**: tarefa de minutos, baixo risco, fácil de reverter (ex: função pura, ajuste de UI trivial, script descartável).
- **Nível 2 — Padrão**: a maioria das tarefas do dia a dia (ex: endpoint novo, feature de tamanho médio, integração simples).
- **Nível 3 — Complexo**: dias/semanas, mudança arquitetural, dado sensível, difícil de reverter (ex: migração, mudança de billing, mudança de schema em produção).

Se não estiver óbvio, pergunte diretamente: "Isso é uma mudança rápida e reversível, ou toca em algo mais sensível/estrutural?"

## Passo 2 — Preencher o template certo

### Nível 1 — Micro
```
Intenção:
Pronto quando:
Fora de escopo:
```
Preencha em conjunto com o usuário em poucas trocas de mensagem. Não expanda além disso.

### Nível 2 — Padrão
```markdown
## Spec: [nome da tarefa]

### Intenção
[Uma frase: o comportamento esperado, não a implementação]

### Contexto
[Por que isso é necessário agora — 1-2 frases]

### Critérios de aceite
- [ ]
- [ ]
(cada um precisa ser verificável / virar teste depois — se não dá pra testar, está vago demais; peça pra reformular)

### Casos de borda considerados
-
-

### Fora de escopo
[O que NÃO deve ser feito aqui, mesmo que pareça relacionado]

### Restrições
[Performance, compatibilidade, convenção do projeto, segurança — só o relevante]

### Ambiente / destino
[Onde isso roda ou é salvo, se relevante — pasta/repo de destino, datasource, porta, variável de ambiente. Se a resposta depende de uma escolha do usuário, pergunte agora e preencha com a decisão, não deixe em branco.]

### Nível de risco
[ ] Reversível fácil
[ ] Difícil de reverter → considere escalar para Nível 3
```

### Nível 3 — Complexo
Tudo do Nível 2, mais:
```markdown
### Alternativas consideradas
[Pelo menos uma alternativa de design e por que foi descartada]

### Dependências e impacto
[O que mais no sistema é afetado, direta ou indiretamente]

### Plano de verificação
[Como será testado além de teste unitário — staging, canary, rollback plan]

### Decisão de reversibilidade
[Se der errado, qual é o caminho de volta, concretamente]

### Perguntas em aberto
[O que ainda não se sabe — nomeie explicitamente em vez de supor]
```

## Passo 3 — Revisar antes de confirmar

Antes de considerar a spec pronta, verifique com o usuário:
- Cada critério de aceite é testável, não vago?
- "Fora de escopo" foi preenchido de verdade, não deixado em branco?
- Se o risco for alto (Nível 3), as perguntas em aberto foram nomeadas, não escondidas?
- **Gate de fechamento:** existe alguma decisão técnica ou de ambiente ainda não resolvida em nenhum campo? Se sim, pergunte agora, uma por uma se necessário, e só apresente a versão final da spec depois de todas resolvidas.

Se algo estiver vago, não avance — peça pra especificar melhor esse ponto específico antes de seguir. A spec só é considerada concluída quando pode ser lida do início ao fim sem nenhuma decisão pendente escondida nela ou depois dela.

## Passo 4 — Salvar e prosseguir

Pergunte ao usuário se quer salvar a spec como arquivo (ex: `docs/specs/[nome-da-tarefa].md` ou onde for a convenção do projeto). Se sim, crie o arquivo. Depois, informe que a Fase E está concluída e pergunte se pode seguir para a Fase C (Codificar) do ECHO — codificando estritamente dentro do que foi definido aqui, sem expandir escopo por conta própria.

## Lembrete

Esta skill cobre só a Fase E. As fases seguintes (Codificar, Homologar, Observar) não fazem parte do escopo dela — quando a spec estiver pronta, seu trabalho aqui terminou.
