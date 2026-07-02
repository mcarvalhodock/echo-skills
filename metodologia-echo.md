# Método ECHO
### Uma disciplina pessoal para unir rigor de engenharia e velocidade de IA

> Prompt não é trabalho. Prompt é intenção. O trabalho é o que acontece entre a intenção e o sistema que sobrevive em produção.

> **Status: em teste.** Este documento descreve o desenho do método. Ele ainda está sendo validado em tarefas reais antes de ser considerado estável — trate como hipótese bem fundamentada, não como regra pronta.

---

## Por que "ECHO"

Quatro fases, em loop — nunca linear, nunca pulado:

**E**specificar → **C**odificar → **H**omologar → **O**bservar → volta pra Especificar

O nome não é acidental: cada incremento que você entrega ecoa nas próximas decisões. Se você pula uma fase, o eco vem distorcido — mais tarde, mais caro, e geralmente na forma de bug de produção ou refatoração forçada.

Isso não é uma metodologia nova do zero. É a síntese prática de três coisas que já existem separadas — **Spec-Driven Development**, **TDD/BDD** e **engenharia de harness/verificação determinística** — organizadas num ciclo que uma pessoa consegue rodar sozinha, sem cerimônia de time, e que funciona com qualquer ferramenta de IA (Claude Code, Cursor, Copilot, o que vier depois).

---

## Regra de ouro

**Nenhum código é gerado por IA antes de existir uma especificação, por menor que seja, que sobreviva sem você por perto. Nenhuma implementação começa antes de existir um plano aprovado. Nenhuma tarefa é declarada pronta sem verificação real e revisão humana da decisão de arquitetura.**

Isso não significa burocracia. Para uma tarefa de 20 minutos, a especificação pode ser 5 linhas e o plano pode nem ser necessário. Para uma feature de uma semana, pode ser um documento inteiro. O tamanho escala com o risco — não com a vontade de ir rápido.

Se você não consegue escrever a especificação, é sinal de que **você mesmo** ainda não entende o problema — e nesse caso, nenhuma IA vai entender por você. Esse é o momento exato em que o atalho aparece: a vontade de pular direto pro prompt pra não encarar essa lacuna.

---

## Fase 1 — Especificar (E)

**Objetivo:** transformar intenção vaga em contrato verificável.

Antes de abrir qualquer chat com IA, escreva:

- **O que**, em uma frase — o comportamento esperado, não a implementação.
- **Critérios de aceite** — como eu sei, objetivamente, que terminou? (cada um precisa virar teste depois)
- **Casos de borda** que você já consegue prever
- **O que fica de fora** — escopo negativo é tão importante quanto o positivo
- **Restrições não-funcionais** relevantes — performance, compatibilidade, segurança, convenção do projeto
- **Ambiente/destino** — onde isso roda ou é salvo, se relevante (é comum essa decisão ficar pendurada se não for perguntada aqui)

O tamanho escala em 3 níveis — micro, padrão, complexo — conforme o risco da tarefa. Template completo em [`template-especificacao.md`](./template-especificacao.md).

**Sinal de alerta:** se você está escrevendo o prompt pra IA e a especificação ao mesmo tempo, misturando os dois — pare. São coisas diferentes. A especificação é sua, pertence a você e ao projeto. O prompt é só a forma de comunicar parte dela pra uma ferramenta específica, e vai mudar quando a ferramenta mudar.

**Regra de fechamento:** uma spec nunca é declarada pronta com decisão técnica pendurada — nem no meio dela, nem como pergunta solta depois. Se surgir uma decisão durante o preenchimento, resolve ali, na hora.

---

## Fase 2 — Codificar (C)

**Objetivo:** usar a IA como acelerador dentro do contrato definido na Fase 1 — nunca como substituta dele. Com um passo intermediário que vale a pena isolar: **planejar antes de codificar.**

Pra tarefas de risco médio/alto, a spec sozinha não é suficiente — ela diz o quê, não diz como. Antes do código:

- Gere um plano de implementação: passos em ordem, arquivos afetados, mapeamento explícito de cada passo com o critério de aceite que ele cobre.
- Aprove o plano de verdade antes de qualquer linha ser escrita — não é aprovação automática, é revisão real.
- Código é escrito estritamente dentro do plano aprovado. Se algo exigir desviar no meio do caminho, isso é sinalizado e reaprovado — nunca improvisado silenciosamente.

Regras que não podem depender do julgamento do modelo (segurança, padrões não-negociáveis, comandos destrutivos) viram **harness determinístico** — hooks, linters, CI, validação automática — não instrução em prompt. Prompt pede; harness garante.

**Sinal de alerta:** você está re-prompting a mesma tarefa pela terceira vez tentando "acertar por sorte". Isso quase sempre significa que a Fase 1 (ou o plano) estava incompleto — volte pra trás, não insista no prompt.

---

## Fase 3 — Homologar (H)

**Objetivo:** provar, com evidência, que o código atende ao contrato — não "parece que funciona".

Dois níveis, sempre os dois, e de natureza diferente:

1. **Verificação automática:** os critérios de aceite da Fase 1 viram testes reais. Se um critério não pode virar teste, isso é sinal de que ele estava vago demais lá atrás. Rode a suíte e reporte o resultado real — nunca "deve ter funcionado" sem ter rodado.
2. **Revisão humana com foco em arquitetura, não sintaxe:** a pergunta não é "o código está bonito", é "essa decisão de design segura daqui a 6 meses, com outro código em volta que ainda não existe". Isso é trabalho que só você consegue fazer — é o "músculo" que você quer manter treinado. Nenhuma ferramenta de IA deveria responder isso no seu lugar, mesmo que pareça óbvio.

**Sinal de alerta:** "rodou e não deu erro" sendo tratado como critério de pronto. Ausência de erro não é presença de correção. E: revisão arquitetural sendo marcada como "ok" sem ser respondida de verdade — isso esvazia a fase inteira.

---

## Fase 4 — Observar (O)

**Objetivo:** fechar o loop — aprender com o que aconteceu depois que o código foi pra produção/uso real, e alimentar isso de volta na próxima especificação.

- O que quebrou que a especificação não previu? Isso vira um novo critério de aceite ou caso de borda no template, pra próxima vez.
- Você está medindo saúde do sistema (dívida técnica, tempo de manutenção, retrabalho) ou só velocidade de entrega? Se só velocidade, ajuste a métrica antes de ajustar o processo.
- Pergunta de calibração pessoal, semanal: *quantas vezes essa semana eu especifiquei antes de prompt, de verdade — e quantas vezes eu pulei direto pro atalho?*

Esta é a fase mais frágil do método hoje: ainda não tem skill própria, é prática manual de retrospectiva. Sem ela rodando de verdade, o ciclo não fecha — vira um funil linear com nome de ciclo.

---

## Por que isso é replicável em qualquer plataforma

O método não depende de nenhuma feature específica de nenhuma ferramenta. Cada fase mapeia pra qualquer ambiente:

| Fase | Implementação neste repo (Claude Code) | Qualquer outra ferramenta de IA |
|---|---|---|
| Especificar | skill [`especificar`](./skills/especificar/SKILL.md) | Arquivo de spec versionado no repo, preenchido manualmente |
| Codificar (com plano) | skill [`planejar`](./skills/planejar/SKILL.md) | Documento de plano + aprovação manual antes do prompt de código |
| Homologar | skill [`homologar`](./skills/homologar/SKILL.md) | Testes automatizados + checklist de revisão humana |
| Observar | ainda não existe skill — prática manual | Retro pessoal + atualização do template de spec |

A ferramenta muda. O contrato entre intenção, execução e verificação, não.

---

## Checklist rápido (cole no seu fluxo de trabalho)

- [ ] Escrevi a especificação antes de abrir o prompt?
- [ ] Os critérios de aceite são verificáveis, não vagos?
- [ ] Alguma decisão técnica ficou pendurada em vez de resolvida na hora?
- [ ] Pra tarefa de risco médio/alto, existe um plano aprovado antes do código?
- [ ] O que é regra inegociável virou harness, não só instrução?
- [ ] Testei o resultado contra os critérios, não só "rodei e vi que funcionou"?
- [ ] Revisei a decisão de arquitetura de verdade, não só marquei como ok?
- [ ] Registrei o que aprendi pra próxima especificação?

---

*Documento vivo — revisado depois de aplicar em tarefas reais. Ajuste o que não encaixar na prática; o método serve ao trabalho, não o contrário.*
