# ECHO

Uma disciplina pessoal pra unir rigor de engenharia e velocidade de IA em coding assistido — especificar antes de codificar, planejar antes de implementar, verificar antes de declarar pronto.

> **Status: em teste.** Isso não é um framework maduro nem um dogma — é um experimento pessoal que estou rodando em tarefas reais antes de considerar "certo". Se você achou este repo, sinta-se à vontade pra usar, forkar ou roubar pedaços, mas saiba que ainda estou validando se funciona sob pressão de verdade.

---

## Por que isso existe

Prompt sozinho diz intenção, não faz o trabalho. É fácil pedir pra IA gerar código rápido e confundir "compilou" com "está certo" — o equivalente, em engenharia, de achar que existe atalho pra disciplina de longo prazo. ECHO é a tentativa de trazer de volta o rigor de sempre (especificação clara, verificação real, revisão de decisão de arquitetura) pro fluxo de trabalho com agentes de IA, sem virar burocracia que ninguém segue na prática.

## O ciclo

Quatro fases, em loop — nunca linear, nunca pulado:

| Fase | O quê | Natureza |
|---|---|---|
| **E**specificar | Intenção vira contrato verificável antes de qualquer prompt de código | Você define |
| **C**odificar | Plano de implementação aprovado antes do código, IA executa dentro do escopo | IA acelera, você aprova |
| **H**omologar | Critérios de aceite viram teste real + revisão arquitetural humana | Verificação + julgamento |
| **O**bservar | O que quebrou que a spec não previu vira input pra próxima especificação | Fecha o loop |

Regra de ouro, resumida: **nenhuma linha de código antes de existir contrato; nenhuma implementação antes de existir plano aprovado; nenhuma tarefa "pronta" sem verificação real e revisão humana.**

O guia completo, com o raciocínio por trás de cada fase, está em [`metodologia-echo.md`](./metodologia-echo.md).

## O que tem neste repo

```
.
├── README.md
├── metodologia-echo.md          # o método, explicado
├── template-especificacao.md    # template de spec em 3 níveis (micro/padrão/complexo)
├── propostas/
│   └── expansao-para-times.md   # hipótese não validada, não é mudança nas skills
├── especificar/SKILL.md         # Fase E — gera e trava a especificação
├── planejar/SKILL.md            # Fase C — traduz spec em plano aprovável
└── homologar/SKILL.md           # Fase H — verifica critérios + cobra revisão arquitetural
```

As três skills são feitas pra Claude Code (ou qualquer harness compatível com o formato `SKILL.md`), mas o método em si não depende de nenhuma ferramenta específica — dá pra aplicar manualmente com qualquer assistente de IA, só copiando os templates.

## Instalação das skills

**Claude Code:**
```bash
cp -r especificar planejar homologar ~/.claude/skills/
```
Ou copie para `.claude/skills/` na raiz de um projeto específico, se quiser escopo local em vez de global.

**Claude.ai:** zipe cada pasta de skill e faça upload em Settings → Features → Skills (planos Pro/Max/Team/Enterprise com code execution habilitado).

Depois de instaladas, elas se encadeiam sozinhas: `especificar` encaminha pra `planejar`, que encaminha pra `homologar` ao fim da implementação.

## Como usar, no dia a dia

1. Peça a tarefa normalmente — a skill `especificar` entra automaticamente (ou chame `/especificar`).
2. Ela classifica o risco (micro/padrão/complexo) e preenche a spec com você, sem deixar nenhuma decisão pendurada pra depois.
3. Pra tarefas Nível 2+, ela encaminha pra `planejar`, que gera um roteiro de implementação — você aprova ou ajusta antes de qualquer código.
4. Código é escrito estritamente dentro do plano aprovado. Desvio no meio do caminho exige nova aprovação, não improviso silencioso.
5. Ao final, `homologar` confere cada critério de aceite contra teste real e conduz um checklist de revisão arquitetural — que você responde, ela não responde por você.
6. Fase O é sua: o que quebrou que a spec não previu vira ajuste no próximo `especificar`.

## O que ainda falta (honestamente)

- **Fase O ainda não tem skill própria** — é prática manual de retrospectiva por enquanto.
- **Enforcement ainda é probabilístico, não determinístico.** As três skills são prompt bem estruturado, não hook. Nada aqui *bloqueia* de verdade se o modelo (ou eu) decidir ignorar — um hook `PreToolUse` que trava a primeira edição de código sem spec salva é o próximo passo natural pra fechar essa lacuna.
- **Zero validação em escala.** Isso foi desenhado, não testado sob pressão real de prazo ainda. Uso pessoal primeiro, difusão pro time só depois de eu conseguir defender cada parte com exemplo real, não com teoria. Raciocínio inicial (ainda hipotético, não implementado) sobre o que mudaria pra 10+ pessoas está registrado em [`propostas/expansao-para-times.md`](./propostas/expansao-para-times.md).

## Licença

Use como quiser. Isso é registro pessoal de processo, não produto — sem garantia, sem suporte formal, ajuste pro seu contexto.
