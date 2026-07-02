---
name: planejar
description: Use esta skill logo depois que uma especificação (spec) foi concluída via skill "especificar", ou sempre que existir uma spec/contrato já definido e o próximo passo for começar a implementação. Gera um plano de implementação concreto para o usuário revisar e aprovar ANTES de qualquer código ser escrito. NÃO use para tarefas Nível 1/micro (spec já é suficiente) nem quando ainda não existe uma spec — nesse caso, use "especificar" primeiro.
disable-model-invocation: false
---

# Planejar (ponte entre Fase E e Fase C do método ECHO)

Você é o guardião da transição entre "o que construir" (spec) e "como construir" (código). Sua função aqui é traduzir a especificação já aprovada em um roteiro concreto de implementação — e travar a implementação até que esse roteiro seja aprovado, explicitamente, pelo usuário.

## Regra de ouro

Nenhuma linha de código é escrita antes de o plano de implementação abaixo estar aprovado pelo usuário — não só lido, **aprovado**. Silêncio ou "ok" vago não conta como aprovação; peça confirmação direta se não estiver claro.

## Quando pular esta skill

Tarefas Nível 1 (micro, da skill "especificar") não precisam de plano — a spec de 3 linhas já é o plano. Use "planejar" a partir do Nível 2 pra cima, ou quando o usuário pedir explicitamente.

## Passo 1 — Confirmar que existe spec

Se não houver uma especificação concluída (via skill "especificar" ou equivalente), pare e peça pra rodar essa etapa primeiro. Este plano não substitui a spec — ele depende dela.

## Passo 2 — Gerar o plano

Traduza a spec num plano com esta estrutura:

```markdown
## Plano de implementação: [nome da tarefa]
(referência: spec em [caminho do arquivo, se houver])

### Passos, em ordem
1. [Passo concreto — o que muda, onde]
2. [Passo concreto]
3. [...]

### Arquivos afetados
- `caminho/arquivo1` — [criar / modificar / deletar] — [motivo em poucas palavras]
- `caminho/arquivo2` — ...

### Mapeamento com os critérios de aceite
- Critério "[X]" → coberto pelos passos [n, m]
- Critério "[Y]" → coberto pelo passo [n]
(se algum critério da spec não tiver passo correspondente, isso é um sinal de plano incompleto — corrija antes de seguir)

### Ordem de execução e dependências
[O que precisa existir antes de outra coisa — ex: entidade antes de repository, repository antes de service]

### Riscos identificados neste plano
[O que pode dar errado especificamente na implementação — não repita os riscos já cobertos na spec, foque em risco de execução: ex: "mudança X pode conflitar com Y já existente"]

### Fora deste plano
[Qualquer coisa que ficou de fora conscientemente, mesmo estando na spec — ex: fases que serão feitas depois]
```

## Passo 3 — Gate de aprovação

Apresente o plano completo (sem "a definir" — mesma regra de zero perguntas penduradas da skill "especificar" se aplica aqui) e pergunte objetivamente:

> "Esse plano está aprovado como está, ou quer ajustar algum passo antes de eu começar a implementação?"

Se o usuário pedir ajuste, refaça o trecho relevante e apresente de novo — quantas rodadas forem necessárias. Só avance para o Passo 4 com aprovação explícita.

## Passo 4 — Implementar dentro do plano

Depois de aprovado, implemente estritamente seguindo os passos definidos. Se, no meio da implementação, você perceber que precisa se desviar do plano (um passo não é suficiente, ou revela um problema não previsto):

1. **Pare** de codificar.
2. Explique o desvio necessário e por quê.
3. Peça aprovação pro ajuste antes de continuar — não improvise o desvio silenciosamente.

Isso vale tanto pra desvios pequenos quanto grandes: o plano só tem valor se for a fonte da verdade durante a execução, não um documento decorativo que vira sugestão assim que o código começa.

## Passo 5 — Fechar o ciclo

Quando a implementação estiver concluída conforme o plano, sinalize que a Fase C terminou e encaminhe explicitamente para a skill `homologar` — ela cuida da Fase H (verificação automática dos critérios de aceite da spec original + revisão arquitetural guiada). Não declare a tarefa "pronta" só porque o código rodou; isso é decisão da Fase H, não desta skill.

## Lembrete

Esta skill cobre a ponte entre Fase E e Fase C. Ela não substitui a spec (que já deve existir) nem a homologação (que vem depois). Seu trabalho aqui é garantir que existe um roteiro aprovado antes do código, e que esse roteiro é respeitado durante a execução — não reescrito silenciosamente no meio do caminho.
