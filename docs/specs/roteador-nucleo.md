# roteador-nucleo

## Intenção
O humano deixa de ser o barramento de mensagens entre as fases do SLE: uma função determinística decide a próxima transição a partir do estado observável, e só devolve o controle nos pontos de julgamento real.

## Depende de
Nenhuma.

## Critérios

**Tabela de transições**

- [ ] **C1** `[miolo]` — Estado com `codificar` concluída resulta em `invocar: verificar`, sem escalar.
- [ ] **C2** `[miolo]` — Veredito com todos os critérios `atendido` resulta em `invocar: homologar`. (Com lote, `roteador-lote` intercepta antes: só o fim do lote chega aqui.)
- [ ] **C3** `[miolo]` — Veredito com pelo menos um `não atendido`, nenhum `não verificável`, e tentativas < teto resulta em `invocar: codificar` com a tentativa incrementada.
- [ ] **C4** `[miolo]` — Tentativas == teto com `não atendido` remanescente resulta em `escalar`, e a decisão carrega o caminho dos N vereditos produzidos, em ordem.
- [ ] **C5** `[miolo]` — Pelo menos um `não verificável` resulta em `escalar` com motivo `defeito-de-spec`, **mesmo que existam `não atendido` no mesmo veredito e tentativas < teto**. Precedência é do `não verificável`.
- [ ] **C6** `[miolo]` — Estado com `especificar` concluída resulta em `escalar` com motivo `gate-spec-aprovada`. Nenhuma entrada produz `invocar: codificar` a partir de `especificar`.
- [ ] **C7** `[miolo]` — Estado com `homologar` concluída resulta em `escalar` com motivo `gate-checklist`.

**Leitura do veredito**

- [ ] **C8** `[miolo]` — Dada uma linha no molde de `verificar` — `- **<ID>** — <classificação>`, com a classificação abrindo o texto após o travessão — o parser devolve `atendido`, `não atendido` ou `não verificável` para aquele identificador. Ênfase em markdown, acento e caixa não alteram o resultado.
- [ ] **C9** `[miolo]` — Linha que não abre no molde é ignorada, **mesmo citando identificadores de critério**. Uma justificativa que menciona `C2` não classifica `C2`.
- [ ] **C10** `[miolo]` — Classificação que o parser não reconhece resulta em `não verificável` para aquele identificador.
- [ ] **C11** `[miolo]` — Nenhuma entrada ambígua é lida como `atendido`. `parcialmente atendido`, `atendido em parte` e `quase atendido` resultam em `não verificável`.
- [ ] **C12** `[miolo]` — Veredito ausente, vazio, ou sem nenhuma linha no molde resulta em `escalar`. Nunca em `invocar`.

**Registro**

- [ ] **C13** `[plataforma]` — Cada decisão acrescenta exatamente uma linha ao registro, com campos fixos (instante, alvo, spec, transição, motivo, evidência, tentativa) e nenhum campo de texto livre. Linhas anteriores não são reescritas.
- [ ] **C14** `[plataforma]` — Dado um registro e o nome de uma spec, é possível recuperar quantas tentativas de `codificar` já ocorreram para ela — é essa leitura que alimenta o teto de C3 e C4.

**Fronteira de porte**

- [ ] **C15** `[integração]` — A decisão é pura: mesma entrada produz mesma saída, e nenhum módulo da cadeia (`roteador.py` e `veredito.py`) toca disco, relógio, rede ou API de harness. Verificável executando a decisão com o sistema de arquivos **e o relógio** instrumentados para falhar.

## Contrato técnico

- Python, pytest, marcador `spec:<ID>` em comentário nos testes — convenção de `tooling/ci/scripts/criterion_coverage.py`.
- Teto de tentativas: parâmetro explícito da decisão, default **3**.
- **O molde do veredito é contrato, não heurística.** `verificar` emite uma linha por critério abrindo com `- **<ID>** — <classificação>`; o parser lê a classificação no início do texto após o travessão, nunca por varredura da linha inteira. Foi a varredura que produziu seis falsos `não verificável` no primeiro veredito real.
- **Desempate:** identificador repetido com classificações diferentes fica com a pior (`não verificável` > `não atendido` > `atendido`). Com o molde fixado o caso é raro, mas ambiguidade nunca resolve para `atendido`.
- **O alvo é parâmetro.** Todo caminho que a decisão devolve ou que o registro escreve é relativo ao alvo, nunca ao diretório onde o método está instalado. O registro fica em `<alvo>/.sle/loop.jsonl`.
- Registro em JSONL, uma decisão por linha. Formato de máquina por escolha: é o que impede o registro de virar prosa sobre o trabalho.
- A decisão é um valor de dado (ação, motivo, evidência, tentativa), não uma string formatada. Quem apresenta ao humano é o driver.
- O instante de C13 entra por parâmetro, não por leitura de relógio dentro da decisão — é o que preserva C15.

## Fora de escopo

- **Semântica de lote** (percorrer N specs, quarentena, propagação por dependência) — é a `roteador-lote`. Esta spec decide uma transição por vez.
- **O driver nativo** (skill e hook do Claude Code) — esta entrega a decisão, não quem a executa.
- **Descobrir o estado** (qual fase terminou, qual o ref base) — o chamador informa. Descoberta é acoplamento a harness, e é o que C15 mantém do lado de fora.
- **Qualquer leitura do código ou do diff** — o roteador é agnóstico ao conteúdo por desenho; julgar implementação é de `verificar`.
- **Interface de linha de comando** — pertence ao driver; a pureza de C15 é o que garante a portabilidade aqui, não uma CLI.

## Plano

Sem fatias: os critérios de `plataforma` e `integração` não fecham sozinhos sem o núcleo `miolo`, e fatiar produziria reconciliação em vez de entrega.

1. `tooling/loop/veredito.py` — parser do molde (C8–C12).
2. `tooling/loop/roteador.py` — a decisão pura e a tabela de transições (C1–C7, C15).
3. `tooling/loop/registro.py` — escrita append-only e leitura de tentativas (C13, C14).
4. `tooling/loop/tests/` — `test_veredito.py`, `test_roteador.py`, `test_registro.py`, com `conftest.py` pondo `tooling/loop` no path.

A ordem é por dependência real: a decisão consome a classificação do parser, e o teto consome a leitura do registro.

## Perguntas em aberto

Nenhuma.
