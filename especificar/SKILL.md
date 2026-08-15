---
name: especificar
description: Use antes de escrever ou modificar código quando o usuário começa uma demanda nova — "implementar", "criar", "adicionar", "bora fazer", "preciso de um script que...". Também quando ele pedir explicitamente para "especificar" ou "escrever a spec". Produz um plano específico e enxuto — critérios falsificáveis e a ordem de implementação, num arquivo só. Termina no gate humano: não invoca `codificar`. NÃO use para debugging do que já existe, pergunta conceitual, ou conserto de uma linha.
disable-model-invocation: false
---

# Especificar

Transforme a demanda num **plano específico**: o que precisa ser verdade no fim, e em que ordem construir. Um arquivo, `<alvo>/docs/specs/<nome>.md`.

Você não escreve código e não escreve teste. Terminada a spec, **você para**: quem aprova é o humano, e quem invoca `codificar` depois é o `orquestrar`.

## Insumos

Você roda em sessão limpa: nada da conversa que originou a demanda chega aqui. Precisa receber:

- **o pedido** — a demanda em texto;
- **o alvo** — o caminho do codebase sobre o qual esta spec vale.

`docs/specs/` e `.sle/manifesto.md` são relativos ao **alvo**, nunca a onde o método está instalado — é o alvo que distingue um codebase do outro. O catálogo `dominios.md` é a exceção: ele é do método, e é o mesmo para todos.

Faltou insumo? **Não invente.** Escreva a spec até onde os insumos alcançam e declare o que falta em "Perguntas em aberto".

## Teto de 15 critérios, e ele não é sugestão

**Se a demanda não cabe em 15 critérios, ela é grande demais: divida em duas demandas e especifique a primeira.**

O teto existe porque spec sem teto cresce sozinha, e tudo abaixo dela incha junto — implementação, teste, verificação. Uma spec de 36 critérios não é mais completa que duas de 18; é uma que ninguém termina.

Quando dividir, diga qual metade vem primeiro e por quê.

## O que é critério

Uma frase que pode ser **provada falsa por observação**. Escreva no formato "dado / quando / então" só quando ele esclarecer; não gaste linha com cerimônia.

- ✅ "Senha com menos de 8 caracteres é recusada com mensagem que nomeia a regra."
- ❌ "O cadastro é seguro e tem boa experiência."

Se você não consegue imaginar a observação que reprova o item, ele não é critério: ou vira critério, ou sai da spec.

### Independentes, e o máximo que couber

Cada critério carrega **uma** observação. Dois fatos numa frase produzem um critério que não se reprova sem ambiguidade — metade atendida, metade não, e quem verifica precisa julgar, que é exatamente o que o critério existe para evitar.

Nenhum critério depende do veredito de outro: cada um se prova sozinho, contra o código, sem ordem entre eles. Prefira muitos critérios estreitos a poucos largos, e vá até onde o teto permitir.

Isso não afrouxa o teto de 15 — aperta. Critério composto esconde escopo: uma spec de 15 critérios compostos é uma spec de 40 disfarçada. Se separar as observações estoura o teto, a demanda é grande demais, e essa é a leitura certa.

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

## O que sobe para o humano, e o que é seu

Toda dúvida que você levantar passa por uma régua só, e ela **não é de julgamento**:

> A resposta é derivável do codebase, do manifesto, ou da própria spec?

**É derivável** — derive, decida, e registre a decisão como critério ou contrato técnico. Não é pergunta: é trabalho que você tem insumo para fazer. Qual biblioteca de teste usar, onde ficam os testes, qual o padrão de nome — está tudo escrito no repositório, e escalar isso trava a pipeline com o que era seu.

**Não é derivável** — sobe. Preferência, prioridade, apetite de risco, o que o negócio quer, o que ainda não está escrito em lugar nenhum. O sinal é direto: se você precisaria **supor** algo sobre a intenção de alguém, não derive. Decidir isso sozinho é fazer o que ninguém te delegou, e o custo aparece tarde, com código pronto em cima.

A régua corta nos dois sentidos de propósito. Sem o primeiro lado, tudo sobe e o gate humano vira o gargalo que ele existe para eliminar. Sem o segundo, você responde no lugar de quem decide.

**Uma pergunta em aberto bloqueia esta spec** — e junto dela as specs que dependem desta. As demais do lote seguem. É intencional: é o que faz escalar por preguiça custar caro, sem fazer uma dúvida legítima parar o ciclo inteiro.

## Formato

```markdown
# <nome>

## Intenção
[uma frase: o que muda para quem usa]

## Depende de
[as specs que precisam estar fechadas antes desta; "nenhuma" se for o caso.
Só isso, e só nome de spec: quem depende DESTA não se declara aqui, e citar
tipo, módulo ou arquivo aqui também não. O `orquestrar` lê esta seção como
grafo, e a relação invertida vira ciclo — que trava o lote em vez de ordená-lo.]

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
[só o que não é derivável. Cada item nomeia o insumo que falta, não só a dúvida.
Vazio se não houver — e vazio é o caso comum.]
```

Nada além disso. Sem seção de alternativas consideradas, sem análise de risco, sem nível de complexidade, sem plano de verificação — esses viraram documento em vez de decisão.

## Antes de fechar

- [ ] Todo critério é falsificável.
- [ ] **Cada critério carrega uma observação só, e nenhum depende do veredito de outro.**
- [ ] São 15 ou menos.
- [ ] **Nenhum critério é pré-requisito de uma spec anterior.**
- [ ] Todo critério tem domínio marcado.
- [ ] **Toda pergunta em aberto passou na régua do derivável** — e nomeia o insumo que falta.
- [ ] Se há fatias, cada uma fecha sozinha.
- [ ] O plano nomeia arquivos, e a ordem é por dependência.
- [ ] "Fora de escopo" diz não a pelo menos uma coisa.
- [ ] O humano aprovou.

Fechada, a spec fica esperando o gate. **Não invoque `codificar` daqui** — a próxima fase roda em sessão nova, e o gate humano fica entre as duas.

## Verbosidade é defeito, não zelo

Se a spec passou de duas telas, ela está explicando em vez de decidir.

Mas atenção ao corte errado: quem lê esta spec é uma sessão limpa, que **não** tem a conversa que a originou. Ela precisa do que tem de ser verdade e dos fatos para chegar lá. Corte a justificativa — nunca o insumo.
