# sle-painel

## Intenção
Você pergunta como estão os projetos e recebe uma fila: o que cada repositório espera de você, agora, derivado do que está no disco dele.

## Depende de
`sle-casa` — sem cadastro não existe "todos os repositórios".

## Critérios

**A fila**

- [ ] **V1** `[miolo]` — `sle painel` devolve uma linha por repositório cadastrado, dizendo o que ele espera de você.
- [ ] **V2** `[miolo]` — `sle painel --alvo <apelido ou caminho>` mostra só aquele repositório.
- [ ] **V3** `[integração]` — O painel sai com **0** mesmo havendo repositórios travados: ele relata, não julga.

**Os estados, e eles não se confundem**

- [ ] **V4** `[miolo]` — Registro ausente aparece como **não começou** — distinto de ocioso e de pronto.
- [ ] **V5** `[miolo]` — Última decisão `escalar` com motivo `gate-spec-aprovada` aparece como **aguarda aprovação do lote**.
- [ ] **V6** `[miolo]` — Última decisão `escalar` com motivo `gate-checklist` aparece como **aguarda checklist**.
- [ ] **V7** `[miolo]` — Última decisão `escalar` com qualquer outro motivo aparece como **travado**, e a linha nomeia o motivo.
- [ ] **V8** `[miolo]` — Última decisão não terminal aparece como **em andamento**, e a linha nomeia a fase e a spec em que parou.

**Não estragar nada para responder**

- [ ] **V9** `[miolo]` — O estado é derivado dos artefatos do alvo. O painel não lê nem escreve armazenamento próprio de estado.
- [ ] **V10** `[plataforma]` — O painel não invoca agente nenhum e não escreve nada em alvo nenhum: nem registro, nem commit, nem arquivo.
- [ ] **V11** `[plataforma]` — Repositório cadastrado cujo caminho sumiu aparece como inacessível e **não impede** os outros de aparecerem.
- [ ] **V12** `[plataforma]` — O painel roda com um ciclo em andamento noutro terminal sem interferir nele e sem esperar por ele.

## Contrato técnico

- **A leitura é a última linha de `<alvo>/.sle/loop.jsonl`**, que já distingue terminal de interrompido — foi o `loop-ciclo` que colocou isso lá, e é o que evita inventar um segundo modelo de estado.
- **Nada de cache.** Reler a cada chamada é barato perto de divergir do alvo, e divergir é como uma ferramenta passa a mentir com confiança — agora sobre N projetos ao mesmo tempo.
- Um alvo sem `.sle/loop.jsonl` mas com specs em `docs/specs/` continua sendo "não começou": specs escritas à mão não são ciclo iniciado.
- O `V12` sai de graça do desenho somente-leitura, e é o que permite deixar um painel aberto enquanto o loop trabalha.

## Fora de escopo

- **Dizer que um repositório está "pronto".** Ninguém verificou os critérios ao final do ciclo ainda; enquanto essa fase não existir, "aguarda checklist" é o mais longe que dá para ir com honestidade.
- **Avançar qualquer projeto.** O painel lê. Supervisor que também executa é outra demanda.
- **Histórico.** Todas as perguntas aqui são sobre o presente.
- **Ordenar a fila por prioridade.** Prioridade entre projetos é julgamento seu, e inventar um critério de ordenação seria decidir no seu lugar.

## Plano

1. `tooling/loop/painel.py` — derivação do estado de um alvo e a linha correspondente (V4–V9, V11).
2. `tooling/loop/driver.py` — o subcomando `painel`, com e sem `--alvo` (V1, V2, V3, V10, V12).
3. `tooling/loop/tests/test_painel.py`, com alvos temporários em cada um dos estados.

Sem fatias: os estados não fecham sem a derivação, e a derivação sozinha não é painel.

## Perguntas em aberto

Nenhuma.
