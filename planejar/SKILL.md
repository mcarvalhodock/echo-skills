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

## Passo 1.1 — Avaliar fatiabilidade

A spec marcou quais critérios pertencem a quais domínios (ver `dominios.md`). Aqui você decide se essa marcação vira **delegação real** a especialistas — humanos ou subagentes — ou se fica só como endereçamento para consulta.

**O nível de risco não entra nesta decisão.** N1/N2/N3 medem reversibilidade e raio de impacto; fatiabilidade mede quanta perspectiva distinta a demanda exige. Um N3 mono-domínio profundo não se fatia; um N2 que toca quatro domínios rasos se fatia bem. Se você se pegar usando o nível como argumento, parou de avaliar.

Três condições. **Falta uma, não fatia:**

1. **Pluralidade** — mais de um domínio genuinamente envolvido, não decorativo. Spec majoritariamente `miolo` reprova aqui.
2. **Independência** — as fatias não precisam negociar entre si. Itens marcados como *cross-cutting retido* já são, por definição, não delegáveis. Se a fatia A precisa de uma decisão da fatia B para começar, reprova.
3. **Massa** — cada fatia tem trabalho suficiente para justificar um contexto próprio. Delegar dois critérios triviais custa mais em coordenação do que executar.

Declare o resultado **por escrito no plano**, com justificativa citando as três condições — inclusive quando não fatia. "Não fatiável" com motivo é informação; sem motivo é omissão.

- **Não fatiável** → siga para o Passo 2 normalmente. O plano sai no formato de sempre, sem nenhuma menção a subagente. Este é o caso comum; não force o outro.
- **Fatiável** → siga para o Passo 2 e, além do plano, aplique o **Protocolo de fatiamento** descrito no fim desta skill.

## Passo 2 — Gerar o plano

Traduza a spec num plano com esta estrutura:

```markdown
## Plano de implementação: [nome da tarefa]
(referência: spec em [caminho do arquivo, se houver])

### Fatiabilidade
[Fatiável ou não, com justificativa citando pluralidade, independência e massa. Se fatiável, liste as fatias propostas por domínio — sem nomear executor concreto.]

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

## Protocolo de fatiamento

Só se aplica quando o Passo 1.1 declarou a demanda fatiável. Se não declarou, ignore esta seção inteira.

### 1. Propor e aprovar

Apresente as fatias propostas — uma por domínio, cada uma com os critérios de aceite que carrega — e obtenha aprovação explícita **antes de qualquer dispatch**. A spec nomeia domínio, nunca executor: quem vai executar cada fatia é decisão deste momento, não da Fase E.

### 2. Projetar a sub-spec

Cada fatia vira um arquivo **fora do repositório de trabalho**, em `~/.echo/fatias/<repositório>/<spec>/`. Se `HOME` não for gravável (CI, container), use o diretório temporário do sistema. **Nunca escreva sub-spec dentro do workspace, e nunca edite o `.gitignore` do projeto** — sub-spec é artefato de execução, não pertence ao repositório do cliente, e sanitização que depende de um arquivo de configuração estar certo é sanitização probabilística. Fora do workspace, não há o que ignorar.

Ela é **gerada**, não escrita, e carrega:

- a **intenção** da spec-mãe, íntegra
- os **critérios de aceite e casos de borda** daquele domínio
- **restrições, fora de escopo e ambiente — integrais, não fatiados**

O terceiro item é o que costuma ser esquecido e é o que mais custa. Um especialista de segurança que recebe só os critérios de segurança, sem o "fora de escopo", vai propor coisa fora do escopo — com toda a razão, porque ninguém contou pra ele.

### 3. Sub-spec é read-only para quem executa

Se o especialista descobrir algo que **muda o contrato**, isso volta para a spec-mãe e a fatia é reemitida. Nunca é corrigido dentro da sub-spec: a mãe deixaria de ser verdade e o método perderia a única coisa que ele existe para proteger, que é ter um contrato confiável.

### 4. Formato de retorno

Cada fatia devolve **dois campos**:

1. **Resultado** — o que foi feito, contra quais critérios
2. **O que a mãe não previu** — descobertas, tensões, suposições que precisou fazer

O segundo campo não é opcional. É Fase O acontecendo dentro da Fase C, e é o que faz o fatiamento render aprendizado em vez de só paralelismo.

### 5. Remontar por reconciliação

A remontagem é **reconciliação contra a spec-mãe**, nunca união dos outputs. "Pronto" do conjunto significa **critérios da mãe verificados** — não "todas as fatias concluídas". Fatia entregue com critério da mãe descoberto é conjunto incompleto.

Por isso a Fase H não muda: `homologar` continua operando só sobre a spec-mãe e não precisa saber que houve fatiamento.

## Lembrete

Esta skill cobre a ponte entre Fase E e Fase C. Ela não substitui a spec (que já deve existir) nem a homologação (que vem depois). Seu trabalho aqui é garantir que existe um roteiro aprovado antes do código, e que esse roteiro é respeitado durante a execução — não reescrito silenciosamente no meio do caminho.
