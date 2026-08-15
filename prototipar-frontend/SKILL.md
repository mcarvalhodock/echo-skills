---
name: prototipar-frontend
description: Use quando a demanda é de interface e o caminho ainda não está decidido — "não sei como isso deveria ficar", "queria ver antes de fechar", "tenta uma tela pra isso". Lê a codebase, produz tela navegável para você reagir, e entrega como resíduo o que sobreviveu à reação — o insumo que `especificar` consome. NÃO use quando o caminho já está decidido e só falta construir: aí a demanda vai direto para `especificar`.
disable-model-invocation: false
---

# Prototipar frontend

Você produz **uma tela para o humano reagir**, e o resíduo dessa reação. Não produz spec, não produz produção.

A pergunta que esta skill responde não é *"como construir isto?"* — é *"é isto mesmo?"*. Quando a segunda ainda não tem resposta, especificar primeiro é escrever contrato sobre hipótese não testada: quinze critérios impecáveis sobre a tela errada.

## Você está fora do ciclo

O ciclo é `especificar` → `codificar` → `verificar` → `homologar`. **Esta skill não é fase dele.** Ela roda **antes** do `especificar`, e o que ela entrega é insumo, não etapa.

A diferença tem consequência prática: nada aqui é medido contra critério, porque não há critério ainda — é o que você está descobrindo. O rigor do ciclo começa depois, sobre o que sobreviveu.

## Insumos

Você roda em sessão limpa. Precisa receber:

- **a demanda** — o que se quer, mesmo mal formulado. Vaga é o caso normal aqui;
- **o alvo** — o caminho do codebase.

## Ancoragem: leia antes de propor

**Não desenhe nada antes de ler o alvo.** Protótipo que nasce em branco é bonito e inútil: ele não herda nada, então tudo nele é decisão nova, e você acaba discutindo tipografia quando queria discutir fluxo.

Abra o que já existe — componentes, telas vizinhas, tokens de estilo, o padrão de estado e de chamada — e escreva a **ancoragem** antes da primeira tela:

```markdown
## Ancoragem
Parte de: [arquivos ou componentes existentes, pelo caminho]
Herda: [ao menos um padrão que o protótipo repete de propósito]
Contradiz: [ao menos uma coisa que ele quebra, e por quê — ou "nada"]
```

As três linhas são obrigatórias, e **"Contradiz" é a que trabalha**. Protótipo que não contradiz nada geralmente não propôs nada: reorganizou o que já havia. Se for esse o caso, escreva "nada" e siga — mas escreva, porque é sinal.

Nomeie caminhos. "Segue o padrão do projeto" não é ancoragem; é elogio.

## O artefato é tela, não texto

**Descrição em prosa é recusada aqui.** Se o produto desta skill pudesse ser lido, o `especificar` já bastava — ele lê melhor que você. O que ele não faz é te dar algo para olhar e odiar em três segundos, que é o serviço.

A tela é **navegável**: o que parece clicável, clica; o que leva a outro lugar, leva. Dado falso é bem-vindo, tela morta não.

E ela mostra os estados, não só o feliz:

- **vazio** — primeira vez, nada cadastrado;
- **carregando** — o que ocupa o espaço enquanto não chega;
- **erro** — o que a pessoa lê quando falha, e o que ela consegue fazer depois;
- **cheio** — volume real, não três linhas de exemplo;
- **o estado que a demanda inventa** — se ela cria um jeito novo de a coisa estar, esse também.

Os quatro primeiros são onde a interface real desmonta, e são exatamente os que uma maquete costuma pular. Pular aqui devolve para o `especificar` uma hipótese que ninguém testou.

## Três rodadas, e a terceira é a última

O teto é **três rodadas de reação**. Uma rodada é: você mostra, o humano reage, você ajusta.

Três é o que comporta *propõe → corrige → confirma*. Na quarta, **pare e entregue o resíduo com o que tiver**, mesmo insatisfeito. Protótipo que não converge em três rodadas não está sendo refinado: está sendo negociado sem contrato, e contrato é o que o `especificar` faz depois — melhor que aqui.

O teto é de esforço, não de qualidade. Não peça permissão para estourá-lo; entregue.

## Descartar é o resultado bom

**Jogar o protótipo fora é sucesso, não desperdício.** Se a tela fez o humano dizer "não é isso", ela pagou o próprio custo — descobriu em uma rodada o que a spec descobriria depois do código pronto, com teste em cima.

Trate o código como descartável desde a primeira linha. Nada aqui precisa aguentar produção, e escrever como se precisasse é o que torna o descarte caro — e, quando o descarte fica caro, você defende a tela errada porque ela deu trabalho.

## O resíduo

O fim desta skill é **um arquivo**, em `<alvo>/docs/prototipos/<nome>-residuo.md`.

Arquivo, não conversa: `especificar` roda em sessão limpa e nada do que aconteceu aqui chega lá. **O resíduo é o insumo "o pedido"** que ele exige — quem o ler precisa conseguir escrever a spec sem ter visto a tela.

```markdown
# <nome> — resíduo

## Ancoragem
[as três linhas, como ficaram no fim]

## O que sobreviveu
[o que o humano confirmou. Uma linha por decisão, em fatos:
"a busca é incremental, sem botão", não "a busca ficou boa"]

## O que foi descartado
[o que foi mostrado e recusado — nomeado, com o motivo em meia linha.
Isto não é histórico: é o que impede a spec de repropor o que já morreu]

## O que continua aberto
[o que três rodadas não resolveram, se sobrou algo]
```

**"O que foi descartado" não é opcional.** Sem ele, o resíduo diz o que fazer mas não o que já foi tentado, e a demanda volta na spec pela porta dos fundos — com aparência de ideia nova.

## O que você não faz

- **Não escreve teste.** Teste de protótipo prende o que era para ser descartável.
- **Não commita como produção.** O que sai daqui não entra na árvore de produção do alvo — só o resíduo é versionável.
- **Não invoca `codificar`.** O caminho é `especificar` primeiro, com o resíduo na mão, e quem decide isso é o humano.

## Frontend é disciplina, não domínio

**Não marque critério, não use `dominios.md` como etiqueta, e não acrescente `frontend` a ele.** O catálogo endereça *especialista* (`dominios.md`); esta skill endereça *prática*. São eixos diferentes, e misturá-los faz `frontend` competir com `experiência` pelo mesmo critério — que devolve ao roteamento a inferência que o catálogo existe para eliminar.

A relação certa é de consumo: o domínio `experiência` te diz o que a interface precisa sustentar naquele repositório — acessibilidade, fluxo, conteúdo — e você usa isso para saber que estados a tela tem de mostrar. Quem marca domínio é o `especificar`, depois, sobre o resíduo.

## Antes de entregar

- [ ] A ancoragem nomeia caminhos reais, e a linha "Contradiz" está preenchida (ou diz "nada").
- [ ] A tela navega, e mostra vazio, carregando, erro e cheio.
- [ ] Foram três rodadas ou menos.
- [ ] O resíduo existe como arquivo, e nomeia o que foi descartado.
- [ ] Quem ler só o resíduo consegue escrever a spec.
- [ ] Nada foi commitado como produção.

Entregue o resíduo e **pare**. A próxima fase é `especificar`, em sessão nova, e quem a invoca é o humano.
