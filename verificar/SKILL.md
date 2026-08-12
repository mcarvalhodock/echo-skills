---
name: verificar
description: Use quando `codificar` terminou uma demanda e o próximo passo é homologar aquela demanda — rodar só o que ela toca e obter um veredito independente contra a spec. NÃO roda a suíte completa e NÃO faz perguntas de arquitetura; isso é de `homologar`, no fim do desenvolvimento.
disable-model-invocation: false
---

# Verificar

Prove que a demanda faz o que a spec pediu. Só a demanda.

## Insumos

Você roda em sessão limpa: não escreveu o código, não viu a implementação acontecer, e é bom que seja assim. Precisa receber:

- **o caminho da spec**;
- **o ref base do diff** — contra o que medir. Sem ele você não tem o que ler, e adivinhar o ponto de corte produz medição de outra coisa;
- **o escopo** — a subárvore do alvo dentro do repositório, `.` quando o alvo é a raiz. Num monorepo, sem isso você mede o trabalho de outros times junto;
- **o alvo** — o codebase.

Faltou um deles? **Pare e diga qual.** Não estime o base por histórico nem por data.

**Alvo sem git não tem ref base**, e aí a leitura limpa julga o estado atual em vez do diff. É degradação declarada, não improviso: você perde a diferença entre *"isto é verdade"* e *"isto passou a ser verdade"*, e critério satisfeito por código anterior à demanda passa a ser lido como atendido.

## O que você NÃO faz

- **Não roda a suíte completa.** É de `homologar`.
- **Não pergunta sobre escalabilidade, acoplamento, volume ou dívida.** É de `homologar`.
- **Não emite o parecer.** Ver abaixo — essa é a regra que sustenta o resto.

## Passo 1 — Rode o que a demanda toca

Os testes daquela demanda, mais o que compartilha código com ela. **Antes de abrir o código**: absorver a lógica primeiro contamina a leitura do resultado.

Reporte a saída real — passou, falhou, não rodou. Nunca "deve ter funcionado".

Se algum comando altera ou apaga dado, confirme antes que o alvo é ambiente isolado: nome do banco, variável, schema. Não assuma isolamento por analogia.

## Passo 2 — Leitura limpa

**É o único ritual que sobreviveu, e é o que compra tudo.** Quem escreve o código escreve os testes; então a suíte verde é autoatestada, e verde autoatestado já produziu "está pronto" em cima de critérios não atendidos. Dez linhas de contexto limpo pegam o que trinta testes verdes não pegam.

Abra um subagente de contexto limpo com este pedido — **molde fixo, sem uma linha de prosa sua**:

```
Leia <alvo>/docs/specs/<nome>.md e o diff de <base>..HEAD limitado a <escopo>.
Para cada critério, uma linha "- **<ID>** — atendido|não atendido|não verificável", e o porquê depois.
Não sugira correção. Não leia mais nada.
Saída em <alvo>/docs/specs/<nome>-veredito.md.
```

Sem git no alvo, a primeira linha vira — e só ela:

```
Leia <alvo>/docs/specs/<nome>.md e o estado atual de <escopo>.
```

A segunda linha fixa o **molde**, não só o vocabulário, e isso é recente: o veredito é lido por máquina no loop, e um formato livre fez um parser ler seis critérios atendidos como não verificáveis. A classificação abre o texto depois do travessão; a justificativa vem em seguida e não é lida por ninguém além de você.

Três regras, e existem porque o desenho vaza sem elas:

1. **O veredito vai para arquivo, e você não o resume.** Ele audita exatamente a sessão que o pediu; repassado, amacia sem má intenção. Diga *"veredito em `docs/specs/<nome>-veredito.md`"* e mais nada sobre o conteúdo.
2. **O pedido é o molde acima, literal.** "Confira se a correção está certa" já afirma que existe correção e que ela é plausível.
3. **Confira o que ele recebe de graça.** Se o harness entrega mensagem de commit ou histórico junto do diff, passe o diff sem elas.

## Passo 3 — Reporte

```markdown
## O que mudou
[uma linha por frente]

## O que está vermelho
| critério | saída real |
|---|---|

## O que precisa da sua decisão
[vazio, se nada precisar]
```

Mais a linha do veredito. **O estado da demanda você pode declarar** — atendida ou não; o *conteúdo* do parecer, não.

## Se o veredito aponta lacuna

**A rota não é sua.** Você produz o veredito e para; quem lê a classificação e decide o próximo passo é o roteador, por tabela fixa:

- **`não atendido`** → volta para `codificar`, automático, até o teto de tentativas.
- **`não verificável`** → sobe para o humano. Isso é defeito de spec, não de código, e mais uma volta de `codificar` só queima tentativa contra um critério que ninguém consegue medir.

As três saídas de sempre continuam existindo — corrigir o código, emendar o critério, declarar a lacuna fora de escopo. As duas últimas são decisão humana, tomada no gate, não aqui.

Corrigiu critério? **O veredito anterior está obsoleto e vale abrir outro.** Um veredito que julgou código que não existe mais não atesta nada.

## Único artefato

O veredito. Não escreva passagem, log de fase, mapa de cobertura nem registro de pressão — isso virou documentação sobre o trabalho em vez de trabalho, e foi o que fez o método custar caro entregando menos.
