---
name: especificar
description: Use antes de escrever ou modificar código quando o usuário começa uma demanda nova — "implementar", "criar", "adicionar", "bora fazer", "preciso de um script que...". Também quando ele pedir explicitamente para "especificar" ou "escrever a spec". Produz um plano específico e enxuto — critérios falsificáveis e a ordem de implementação, num arquivo só. Encaminha para `codificar`. NÃO use para debugging do que já existe, pergunta conceitual, ou conserto de uma linha.
disable-model-invocation: false
---

# Especificar

Transforme a demanda num **plano específico**: o que precisa ser verdade no fim, e em que ordem construir. Um arquivo, `docs/specs/<nome>.md`.

Você não escreve código e não escreve teste. Quando o plano estiver aprovado pelo humano, siga para `codificar`.

## Teto de 15 critérios, e ele não é sugestão

**Se a demanda não cabe em 15 critérios, ela é grande demais: divida em duas demandas e especifique a primeira.**

O teto existe porque spec sem teto cresce sozinha, e tudo abaixo dela incha junto — implementação, teste, verificação. Uma spec de 36 critérios não é mais completa que duas de 18; é uma que ninguém termina.

Quando dividir, diga qual metade vem primeiro e por quê.

## O que é critério

Uma frase que pode ser **provada falsa por observação**. Escreva no formato "dado / quando / então" só quando ele esclarecer; não gaste linha com cerimônia.

- ✅ "Senha com menos de 8 caracteres é recusada com mensagem que nomeia a regra."
- ❌ "O cadastro é seguro e tem boa experiência."

Se você não consegue imaginar a observação que reprova o item, ele não é critério: ou vira critério, ou sai da spec.

## Uma spec pode depender de outra. Um critério, não.

**Nenhum critério desta spec pode ser pré-requisito de uma spec que vem antes dela.**

Dependência entre specs é normal e se declara: a 07 depende da 06, e a 06 fecha primeiro. O que não pode existir é a 01 precisar que um critério da 06 seja verdade para fechar — aí a spec que é dependência só fecha depois de quem depende dela, e nenhuma das duas fecha nunca.

Para cada critério, pergunte: **"alguma spec anterior precisa que isto seja verdade?"** Se sim, ele está na spec errada. Duas saídas, e a escolha é do humano:

- o critério pertence àquela spec anterior — mova;
- a ordem está errada — inverta as duas specs.

O sintoma, quando isso passa: toda entrega fica "parcial", e o relatório de execução nunca mostra uma spec inteira verde. Já custou dias antes de alguém perceber que a causa não era falta de trabalho.

## Domínios

Marque cada critério com o domínio que ele exercita — o catálogo canônico está em [`dominios.md`](../dominios.md).

O domínio não é etiqueta: ele **baliza o desenvolvimento**. Diz que ferramental o critério puxa, que tipo de erro ele admite, e quanto custa errar. Um critério de `segurança` não aceita a mesma verificação que um de `experiência`.

**Se os domínios se separam limpo, a spec é fatiável.** Uma fatia é entregável separadamente quando:

1. os critérios dela são de um domínio (ou de um conjunto declarado);
2. **ela fecha sozinha** — nenhum critério dela depende de critério de outra fatia.

A condição 2 é a mesma regra da seção anterior, aplicada dentro da spec. Fatia que não fecha sozinha não é fatia: é a mesma spec com o trabalho espalhado, e o custo aparece só na hora de homologar.

Se não separa limpo, **não force**. Spec pequena inteira vale mais que spec fatiada que precisa de reconciliação.

## Formato

```markdown
# <nome>

## Intenção
[uma frase: o que muda para quem usa]

## Depende de
[as specs que precisam estar fechadas antes desta; "nenhuma" se for o caso]

## Critérios
- [ ] **C1** `[domínio]` — ...
- [ ] **C2** `[domínio, domínio]` — ...

## Contrato técnico
[só o que restringe a implementação e não é óbvio: algoritmo obrigatório, formato de
token, limite de latência, tabela que não pode existir. Se não houver, escreva "nada
além do padrão do repositório".]

## Fora de escopo
[o que alguém razoavelmente esperaria e não vem — com o motivo em meia linha]

## Plano
1. ...
2. ...
[a ordem de construção, por dependência real. Cada passo nomeia os arquivos ou módulos
que ele toca. Sem estimativa, sem "fase", sem diagrama.

Se a spec for fatiável, diga aqui quais são as fatias e em que ordem — cada uma com os
critérios que fecha.]

## Perguntas em aberto
[o que depende de decisão do humano; vazio se não houver]
```

Nada além disso. Sem seção de alternativas consideradas, sem análise de risco, sem nível de complexidade, sem plano de verificação — esses viraram documento em vez de decisão.

## Antes de fechar

- [ ] Todo critério é falsificável.
- [ ] São 15 ou menos.
- [ ] **Nenhum critério é pré-requisito de uma spec anterior.**
- [ ] Todo critério tem domínio marcado.
- [ ] Se há fatias, cada uma fecha sozinha.
- [ ] O plano nomeia arquivos, e a ordem é por dependência.
- [ ] "Fora de escopo" diz não a pelo menos uma coisa.
- [ ] O humano aprovou.

Aprovado, invoque `codificar`.

## Verbosidade é defeito, não zelo

Se a spec passou de duas telas, ela está explicando em vez de decidir. Corte a explicação: quem lê já tem o contexto da conversa. O que não pode faltar é o que precisa ser **verdade**, não por que você acha que precisa.
