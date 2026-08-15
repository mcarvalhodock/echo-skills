# velha — resíduo

## Ancoragem

Parte de: `tooling/loop/painel.py` (`Estado(rotulo, detalhe)`, `linha_de`), `scripts/install.sh:50-63` (`write_step`: `[ok]` `[skip]` `[warn]` `[error]`)
Herda: todo estado se declara como rótulo em minúscula **mais** o motivo, nunca só cor ou ícone — é o contrato de `painel.py:33` e do `write_step`
Contradiz: no alvo nada é clicável; a interface inteira é saída de terminal que se lê. Um tabuleiro em que se clica quebra isso de propósito — é a primeira superfície do repositório que aceita entrada

## Como a tela subiu

Degrau 2 — preview em docker (`prototipar-frontend/preview/compose.yml`), porta padrão `8173`. O degrau 1 não existe neste alvo: `echo-skills` não tem frontend nem comando para rodar um, e o manifesto declara `experiência` inativo.

Capturada e conferida antes de ser mostrada, via automação de browser. A conferência reprovou duas coisas, consertadas antes da rodada 1.

## O que sobreviveu

- Todo estado do jogo se anuncia como `[jogo] <rótulo> — <motivo>`, com o motivo obrigatório: `não começou — sem jogada`, `pensando — vez de O`, `deu velha — tabuleiro cheio, sem três em linha`.
- Clique em casa ocupada é recusado com motivo que nomeia a casa e o dono (`recusado — casa 5 ocupada por X`), não ignorado em silêncio.
- O tabuleiro aceita clique. A contradição com o alvo foi mostrada explicitamente e não foi recusada.
- Seis estados navegáveis: vazio, em jogo, pensando, recusado, cheio, vitória.
- O adversário responde com atraso visível, e a entrada trava enquanto isso — "carregando" num jogo é o oponente pensando.
- Sem passo de build: um `index.html` que carrega o próprio CSS e o próprio JS.

## O que foi descartado

- **`vez de X` persistindo depois do fim** — dois rótulos se contradiziam na mesma tela; virou `—` quando o jogo encerra. Morreu na conferência, antes de chegar ao humano.
- **Placar incrementando a cada atalho de estado** — pular entre cenas somava vitória que ninguém ganhou. Cada cena passou a fixar o placar. Mesma conferência.
- **Nada foi recusado pelo humano na rodada 1.** A reação foi confirmação, e a rodada fechou sem correção — registrado porque um resíduo sem recusa humana é sinal, não silêncio.

## O que continua aberto

- Se a recusa falante é cerimônia demais para um jogo da velha, ou se é justamente o que torna o vocabulário do repo aplicável a uma interface.
- Os atalhos de estado são andaime de protótipo, não proposta. Se alguma forma deles deve sobreviver ao produto, ninguém decidiu.
- Se a contradição vale: aceitar entrada clicável abre a primeira superfície interativa do repositório, e a consequência disso para o método não foi discutida — sobreviveu por não ter sido recusada, não por ter sido examinada.
