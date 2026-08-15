# loop-ciclo

## Intenção
O teto de tentativas passa a valer por ciclo: uma spec que esgotou as tentativas semanas atrás não nasce esgotada quando você a emenda e roda de novo.

## Depende de
`roteador-driver` — é o laço que grava o registro e conta as tentativas.

## Critérios

**O registro passa a contar o fim**

- [ ] **R1** `[plataforma]` — Decisão de `escalar` é gravada no registro, com a mesma linha de campos fixos das invocações. Hoje só invocação é gravada, e o registro não sabe dizer por que o loop parou.
- [ ] **R2** `[plataforma]` — O encerramento do lote (a decisão de `invocar: homologar`, que o driver não executa) também é gravado.

**Ciclo novo × retomada**

- [ ] **R3** `[plataforma]` — Registro cuja última linha é terminal faz a execução seguinte arquivar o arquivo e começar um novo.
- [ ] **R4** `[plataforma]` — Registro cuja última linha **não** é terminal faz a execução seguinte continuar no mesmo arquivo. Interromper com `Ctrl+C` e rodar de novo não perde a contagem.
- [ ] **R5** `[plataforma]` — O arquivo arquivado preserva o conteúdo byte a byte e recebe nome que não colide com arquivamentos anteriores.
- [ ] **R6** `[plataforma]` — Registro inexistente é ciclo novo, sem arquivar nada e sem erro.

**A contagem**

- [ ] **R7** `[miolo]` — A contagem de tentativas considera só o ciclo corrente. Spec que esgotou o teto num ciclo anterior começa o novo em zero.
- [ ] **R8** `[miolo]` — Dentro do mesmo ciclo, a contagem continua acumulando entre execuções interrompidas.

## Contrato técnico

- **Terminal é `escalar` ou `invocar:homologar`.** Ambos significam que o laço não tem mais o que fazer sozinho; qualquer outra linha significa que ele foi cortado no meio.
- **A escalada por guarda do alvo não é gravada.** A guarda existe para não tocar num alvo que não está pronto, e criar `.sle/loop.jsonl` ali contradiria a própria guarda — além de sujar o working tree que ela acabou de reprovar. O `R1` vale para as decisões de dentro do ciclo; a guarda aborta antes de ele começar.
- **A detecção é pela última linha, não por flag.** Foi a decisão tomada no lugar de `--novo-ciclo`: flag se esquece justamente na vez em que importa, e o caso comum passa a exigir que você lembre de algo. Custo aceito: se você escalar, consertar o código à mão sem tocar a spec e rodar de novo, ganha contagem zerada. Isso é o comportamento certo — o teto anterior julgou código que não existe mais.
- Arquivamento: `<alvo>/.sle/loop-<n>.jsonl`, com `<n>` o menor inteiro livre. Nome derivado do que já existe no diretório, não de relógio — dois ciclos no mesmo segundo colidiriam.
- O esquema do registro **não muda**: os sete campos do `C13` da `roteador-nucleo` continuam os mesmos, e nenhum campo novo entra. É por isso que a solução é arquivar em vez de marcar ciclo na linha.
- `registro.contar_tentativas` continua contando o arquivo que recebe; quem sabe qual arquivo é o corrente é o driver.

## Fora de escopo

- **Purgar ou comprimir arquivos antigos** — eles são o histórico de auditoria do loop; apagar é decisão sua, não do mecanismo.
- **Contar tentativas entre alvos** — cada alvo tem o seu registro, e isso já vale.
- **Retomar quarentena** — continua exigindo insumo novo, que vem de você.
- **Otimizar a releitura do registro** — medido: 188 ms num ciclo de 12 specs, contra ~36 min de invocações. Otimizar isso não compra nada.

## Plano

1. `tooling/loop/registro.py` — gravação de decisão terminal, detecção de linha terminal, arquivamento e escolha do próximo nome livre (R1–R6).
2. `tooling/loop/driver.py` — chamar o arquivamento na abertura e registrar a decisão final antes de sair (R7, R8).
3. `tooling/loop/tests/test_registro.py` e `test_driver.py`.

## Perguntas em aberto

Nenhuma.
