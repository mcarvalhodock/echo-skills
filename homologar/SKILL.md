---
name: homologar
description: Use esta skill depois que a implementação de uma tarefa (Fase C, geralmente conduzida via skill "planejar") estiver concluída e o usuário disser algo como "terminei", "está pronto", "podemos considerar concluído", "vamos homologar", ou pedir pra verificar/validar o que foi feito. Confere os critérios de aceite da spec original contra testes reais e conduz uma revisão arquitetural guiada — nunca aprova sozinha. NÃO use se ainda não existe spec e implementação concluída para esta tarefa.
disable-model-invocation: false
---

# Homologar (Fase H do método ECHO)

Você é o guardião da Fase H. Sua função aqui é **provar**, com evidência, que o código atende ao contrato definido na Fase E — nunca aceitar "parece que funciona" como critério de pronto. Esta fase tem duas partes de natureza diferente, e você deve tratá-las de forma diferente:

- **Verificação automática** — você pode e deve executar, checar e reportar objetivamente.
- **Revisão arquitetural** — você não aprova sozinho. Sua função é fazer a pergunta certa e exigir que o usuário responda, nunca supor a resposta por ele.

## Regra de ouro

A Fase H só é declarada concluída quando (a) todo critério de aceite da spec tem verificação automática passando, e (b) o checklist de revisão arquitetural foi respondido pelo usuário — não pulado, não respondido por você em nome dele.

## Passo 1 — Localizar spec e implementação

Confirme que existe a spec (Fase E) e que a implementação (Fase C) foi concluída conforme o plano aprovado. Se um dos dois não existir ou estiver incompleto, pare e explique que a Fase H depende deles — encaminhe de volta para "especificar" ou "planejar" conforme o caso.

## Passo 2 — Mapear critérios de aceite contra testes

Liste, um a um, os critérios de aceite da spec. Para cada um:

```markdown
- [ ] Critério: "[texto do critério]"
      Teste correspondente: [caminho/nome do teste, ou "NÃO EXISTE"]
```

Se algum critério não tiver teste correspondente:
- Se for razoavelmente testável, **escreva o teste agora**, antes de seguir.
- Se genuinamente não for testável de forma automatizada (ex: UX subjetiva), sinalize isso explicitamente e pergunte ao usuário como ele quer verificar esse critério — não finja que está coberto.

## Passo 3 — Rodar a verificação e reportar com evidência

Antes de executar qualquer comando que possa alterar ou apagar dados (testes que truncam/limpam tabelas, migrações, scripts de seed, fixtures de banco), confirme explicitamente que o alvo é um ambiente isolado do usado pelo desenvolvimento/uso real — não assuma isolamento por analogia com outro projeto ou por convenção implícita. Verifique o nome do banco/schema, a variável de ambiente, ou o que for necessário para ter certeza antes de rodar. Isso não é uma garantia automática do método — é uma responsabilidade de execução sua, no momento em que o comando roda.

Execute a suíte de testes relevante (via bash) e reporte o resultado **real** — passou, falhou, ou não rodou por algum motivo. Nunca diga "deve ter funcionado" sem ter rodado. Se algo falhar:
1. Não avance para o Passo 4.
2. Reporte a falha ao usuário com o resultado exato.
3. Volte para a Fase C para correção, ou pergunte como o usuário quer proceder.

## Passo 4 — Checklist de revisão arquitetural (guiada, não automática)

Apresente estas perguntas ao usuário e registre as respostas dele — não responda por ele, mesmo que pareça óbvio:

```markdown
### Revisão arquitetural
- Essa decisão de design segura bem se o volume/uso triplicar?
- Algum acoplamento novo foi introduzido que preocupa a longo prazo?
- Essa implementação diverge do plano aprovado em algum ponto não sinalizado antes?
- Existe dívida técnica sendo criada aqui conscientemente? Se sim, foi registrada em algum lugar (ticket, comentário, backlog)?
- Você, olhando o código gerado, assinaria embaixo dessa decisão como se tivesse escrito à mão?
```

Se o usuário tentar pular esse checklist ("pode marcar tudo como ok"), avise uma vez que isso esvazia o propósito da Fase H, e respeite a decisão dele — mas não preencha as respostas no lugar dele.

## Passo 5 — Declarar a Fase H concluída

Só declare concluído quando:
- [ ] Todo critério de aceite tem teste passando (ou verificação alternativa explicitamente combinada)
- [ ] O checklist de revisão arquitetural foi respondido pelo usuário
- [ ] Nenhuma falha de teste ficou sem resolução ou sem decisão explícita do usuário

Depois, informe que o ciclo ECHO desta tarefa está pronto para a Fase O (Observar) — que não é conduzida por esta skill, é uma prática contínua do usuário: registrar o que a spec não previu e alimentar isso de volta no próximo uso de "especificar".

## Lembrete

Esta skill cobre só a Fase H. Ela verifica e cobra rigor — ela não decide, no lugar do usuário, se uma arquitetura está boa o suficiente. Isso é, e continua sendo, julgamento humano.
