---
name: codificar
description: >-
  Use quando existe uma spec aprovada por `especificar` e o próximo passo
  é implementá-la. Escreve o código de produção e os testes unitários
  daquela demanda, seguindo o Clean Code e a arquitetura do repositório.
  Entrega e para: não invoca `verificar`. NÃO use sem spec aprovada, nem
  para conserto de uma linha que não passou por spec.
---

# Codificar

Implemente **tudo** que a spec pede, e nada além. Escreva os testes unitários **daquela demanda**.

## Insumos

Você roda em sessão limpa: não viu a spec ser escrita, não viu a conversa, não sabe o que foi discutido e descartado. Precisa receber:

- **o caminho da spec aprovada**;
- **o alvo** — o codebase onde o código vai morar.

A spec é o contrato inteiro. Se ela não basta para implementar, isso não é falha sua e você não preenche a lacuna por conta: **pare e diga qual insumo falta.**

Caminhos são relativos ao alvo. O padrão de código sai de `<alvo>/.sle/manifesto.md`.

## O que você entrega

1. O código de produção que satisfaz os critérios, na ordem do plano.
2. Os testes daquela demanda, cada um citando o critério que cobre (`C1`, `C2`, …).

Ordem entre os dois: a que fizer o código ficar melhor. Teste antes ajuda quando o comportamento é claro e o desenho não; código antes ajuda quando é o contrário. O que não é negociável é que **nenhum critério fique sem teste** ao fim.

## O que você roda

**Só os testes desta demanda.** Em watch, o tempo todo.

**A suíte completa não é sua.** Ela pertence a `homologar`, no fim do desenvolvimento. Rodá-la "para garantir" no meio da implementação é ansiedade operando como método: gasta tempo e não compra o que os seus testes não comprem mais barato.

Se você tocou código compartilhado e desconfia de quebra fora da demanda, **diga isso na entrega** em vez de rodar tudo. Quem mede é `verificar`.

## Clean Code e arquitetura

O padrão é o do manifesto do repositório, não o que você prefere. Sem manifesto, boas práticas gerais — sem inventar rigidez que ninguém pediu.

Duas regras que valem sempre:

- **Nunca deixe o código pior do que estava.** O que sai daqui é produção.
- **Nome que declara intenção.** Se o comentário existe para explicar o que o nome deveria dizer, corrija o nome.

Comentário é para o **porquê** — a decisão, o custo que ela evita, a armadilha que ela fecha. Nunca para o quê.

## Escopo estrito

Não implemente o que a spec não pediu. *"Já que estou aqui, aproveito"* é violação de escopo — vira uma linha na entrega, não código agora.

Se algo que a spec pediu se mostrar impossível ou errado, **pare e diga**. Não improvise contra um critério que você sabe estar quebrado.

## Entrega

Três blocos, e nada além:

```markdown
## O que mudou
[uma linha por frente, com os caminhos]

## O que está vermelho
[vazio, se os testes da demanda passam]

## O que precisa da sua decisão
[vazio, se nada precisar]
```

Não escreva documento de passagem, não escreva log de fase, não descreva como o código resolve o problema por dentro. O diff já conta o que mudou; quem verifica mede contra a spec, e a sua explicação só contaminaria essa medida.

Entregue e pare. **Não invoque `verificar` daqui** — ela roda em sessão nova, e é o `orquestrar` que a chama. Uma fase que emenda na seguinte dentro da mesma sessão carrega o próprio raciocínio junto, que é exatamente o que a sessão limpa existe para cortar.
