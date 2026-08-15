# orquestrar-lote — veredito

Base: `git diff 003eebb -- .` (árvore de trabalho, não commitado). Arquivos que carregam a spec: `orquestrar/SKILL.md` e `metodologia-sle.md`.

## Critérios

- **L1** — atendido
- **L2** — atendido
- **L3** — atendido
- **L4** — atendido
- **L5** — atendido
- **L6** — atendido
- **L7** — atendido
- **L8** — atendido
- **L9** — atendido
- **L10** — atendido
- **L11** — atendido
- **L12** — atendido
- **L13** — atendido
- **L14** — atendido

## Por quê

**L1** — A seção nova "O lote: ler tudo antes de despachar qualquer coisa" abre com a ordem direta: "Recebendo mais de uma spec aprovada, leia todas antes de despachar a primeira", e o checklist "Antes de devolver" repete como item verificável ("Sendo lote, todas as specs foram lidas antes do primeiro despacho").

**L2** — A definição está escrita como definição, não como exemplo: "Divergência é um par de critérios, de specs diferentes, que incidem sobre o mesmo ponto do código." Os três elementos exigidos pelo critério (par de critérios / specs diferentes / mesmo ponto do código) estão todos presentes.

**L3** — O teste está isolado em citação, como pergunta única: "Existe implementação que atenda os dois critérios?" É o teste classificatório que a spec pede, e não um conselho difuso.

**L4** — O ramo "Existe" manda prosseguir e exige o registro: "Prossiga, e registre qual é a implementação que atende os dois", com a justificativa de por que o registro é obrigatório (resolução não anotada é decisão invisível para `codificar`). O checklist final também cobra ("a resolvível teve a implementação registrada").

**L5** — O ramo "Não existe nenhuma" manda parar e subir: "Pare e suba para o humano". A parada também aparece na lista das quatro exceções mais abaixo.

**L6** — O mesmo ramo nomeia o que deve ser dito ao subir: "nomeando **as duas specs e o par de critérios**".

**L7** — O limite está declarado em parágrafo próprio: "A leitura do lote só alcança contradição escrita nas specs, e não substitui o veredito de cada demanda", seguido de "Ler o lote não é certificar que ele é coerente" e da atribuição explícita da rede residual a `verificar`, uma demanda por vez.

**L8** — A seção "O que sobe, e o que segue" declara a parada e dá o teste separador, na forma da régua de `especificar` aplicada à condução: se prosseguir exigiria *supor* intenção — preferência, prioridade, apetite de risco —, pare; se a resposta é derivável do codebase, do manifesto ou das specs, é corrigível. O teste separa os dois casos, que é o que o critério exige.

**L9** — Está escrito em negrito na mesma seção: "O que é corrigível prossegue sem parar, com a recomendação registrada", com a razão anexa (parar para pedir permissão sobre o derivável devolve ao humano o trabalho que o orquestrador absorve).

**L10** — A tabela problema→fase existe e cobre quatro tipos: código não faz o que o critério pede → `codificar`; critério atendido, falta medir → `verificar`; ciclo acabou e falta a suíte completa → `homologar`; critério errado ou não mensurável → nenhuma, sobe. A frase seguinte fixa a regra que a tabela encarna: "O tipo do problema decide o contexto, não a ordem do ciclo."

**L11** — A seção "O teto, e as paradas por exceção" fixa "Duas tentativas por critério `não atendido`" e detalha a contagem — reprovou, volta uma vez; reprovou de novo, pare e suba —, o que dá exatamente duas tentativas e a segunda reprovação como parada. A justificativa do número e o enquadramento da segunda como "suspeita de spec ambígua" estão presentes. A tabela de roteamento no topo foi ajustada para "volta para `codificar`, até o teto", e o checklist ganhou "Nenhum critério voltou para `codificar` mais de duas vezes".

**L12** — As três exceções de `metodologia-sle.md:114` estão reproduzidas com os mesmos nomes: `não verificável` (dito "defeito de spec"), teto de tentativas estourado, insumo que falta. A quarta da lista é a divergência, que não é invenção: é a exceção que **L14** manda acrescentar à lista canônica, e ela aparece na skill e na metodologia com a mesma redação de fundo. A proibição está escrita: "não se inventa uma quinta" e "Inventar exceção fora dessas quatro é o que transforma 'para quando precisa' em 'para sempre que tem dúvida'". A seção anterior, que antes listava duas exceções soltas e incompletas, foi trocada por um ponteiro para essa lista única — não há duas listas concorrentes.

**L13** — A regra da quarentena está reproduzida em negrito: "Spec bloqueada por insumo entra em quarentena junto com as que dependem dela, e o resto do lote segue", com o princípio ("problema local não vira parada global") e uma consequência a mais, coerente com o método: specs em quarentena não entram na homologação, porque não fecharam.

**L14** — A linha de exceções de `metodologia-sle.md` foi reescrita para incluir a divergência junto das outras três, com a definição em linha: "ou **divergência entre specs** — duas que se contradizem a ponto de nenhuma implementação atender aos dois critérios". A quarentena permanece na mesma linha, intacta.

## Observação de leitura

A seção **Critérios** da spec vai de **L1** a **L14**, mas o **Contrato técnico** e o **Plano** falam em **L15** ("**L15** acrescenta a divergência à lista canônica", "o único de `plataforma` é uma linha", "Quatorze dos quinze critérios"). O **L15** citado no texto corresponde ao **L14** listado — o critério de `plataforma` sobre `metodologia-sle.md`. A numeração foi lida como um deslocamento de rótulo, não como um décimo quinto critério ausente; não há critério sem correspondência no diff.
