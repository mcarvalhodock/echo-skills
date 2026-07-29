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

### Domínios envolvidos
| item | classificação |
|---|---|
| [cada critério de aceite e cada caso de borda acima] | `dominio` / cross-cutting retido / miolo |

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
Tudo do Nível 2 — incluindo **Domínios envolvidos** — mais:
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

## Passo 2.1 — Classificar por domínio (só Nível 2 e 3)

Nível 1 não tem esta etapa — a válvula de escape do método não engorda.

**Leia o catálogo antes de conduzir.** O vocabulário canônico está em `dominios.md` na raiz do repositório do método. Nunca reproduza a lista de memória e nunca a copie para dentro de uma spec: fonte duplicada é defeito, e é ela que quebra a evolução do catálogo.

**Verifique a ativação local.** Se o repositório de trabalho tiver `.echo/manifesto.md`, ofereça **apenas os domínios ativos** declarados nele, e trate como obrigatórios os que ele marcar assim. Se não existir manifesto, avise **uma vez** — "este repositório não tem `.echo/manifesto.md`; usando o catálogo canônico inteiro" — e siga normalmente. Ausência de manifesto degrada, não bloqueia; não peça para criar um no meio da spec.

**Classifique cada critério de aceite e cada caso de borda** em uma de três opções:

- **domínio(s)** — pertence a uma ou mais disciplinas do catálogo; é candidato a delegação
- **cross-cutting retido** — toca vários domínios de forma inseparável, então **não se delega**; fica com o orquestrador
- **miolo** — regra de negócio, comportamento central; fica com o dono da demanda

`miolo` é classificação válida e frequente. Uma spec inteiramente miolo é resultado legítimo — significa que a demanda não tem aspecto delegável, só corpo. Não invente domínio para preencher a tabela.

Um critério pode pertencer a mais de um domínio. Mas se ele marca vários e eles são inseparáveis, isso não é multi-domínio: é cross-cutting retido. E se marca vários que *são* separáveis, verifique se não são dois critérios diferentes escritos como um só.

**Domínio sem item apontando pra ele** é sinal de decomposição vaga — peça refino antes de fechar.

### Recusa de domínio fora do catálogo

Se o usuário propuser um nome que não está no catálogo (ou não está ativo no manifesto), **recuse e ofereça a lista canônica**. Não aceite "outros", "diversos" nem nomes inventados — é a recusa que preserva a precisão da spec.

Mas a recusa **grava**. Acrescente uma linha em `.echo/pressao-catalogo.md` do repositório de trabalho com: data, spec em curso, nome tentado exatamente como foi proposto, o que se queria expressar em uma frase, e o domínio oferecido em substituição. Se o arquivo não existir, crie com o cabeçalho descrito em `dominios.md`.

Esse log é o único instrumento de evolução do catálogo. Anotação informal que morre no fim da conversa não serve — a pressão sobre o vocabulário é o dado mais valioso que o método produz.

## Passo 3 — Revisar antes de confirmar

Antes de considerar a spec pronta, verifique com o usuário:
- Cada critério de aceite é testável, não vago?
- "Fora de escopo" foi preenchido de verdade, não deixado em branco?
- Se o risco for alto (Nível 3), as perguntas em aberto foram nomeadas, não escondidas?
- **Gate de domínio (N2/N3):** todo critério de aceite e todo caso de borda tem classificação? Um item sem classificação é uma pergunta pendurada como qualquer outra — resolva antes de fechar, não depois.
- **Gate de fechamento:** existe alguma decisão técnica ou de ambiente ainda não resolvida em nenhum campo? Se sim, pergunte agora, uma por uma se necessário, e só apresente a versão final da spec depois de todas resolvidas.

Se algo estiver vago, não avance — peça pra especificar melhor esse ponto específico antes de seguir. A spec só é considerada concluída quando pode ser lida do início ao fim sem nenhuma decisão pendente escondida nela ou depois dela.

## Passo 4 — Salvar e prosseguir

Pergunte ao usuário se quer salvar a spec como arquivo (ex: `docs/specs/[nome-da-tarefa].md` ou onde for a convenção do projeto). Se sim, crie o arquivo. Depois, informe que a Fase E está concluída.

- Se a tarefa for **Nível 1 (micro)**, pode seguir direto para a Fase C (Codificar), dentro do que foi definido aqui.
- Se for **Nível 2 ou 3**, não implemente ainda — encaminhe para a skill `planejar`, que vai transformar esta spec num plano de implementação a ser aprovado antes de qualquer código.

## Lembrete

Esta skill cobre só a Fase E. As fases seguintes (Codificar, Homologar, Observar) não fazem parte do escopo dela — quando a spec estiver pronta, seu trabalho aqui terminou.
