# roteador-driver

## Intenção
O loop passa a andar sozinho: dado um alvo e um lote de specs aprovadas, o driver invoca cada fase em sessão limpa, aplica a decisão do roteador e só para nos pontos de julgamento real.

## Depende de
`roteador-nucleo` (a decisão), `roteador-lote` (a semântica de lote) e `roteador-driver-invocacao` (processo, guardas e histórico). Esta spec é só o laço.

## Critérios

**O laço**

- [ ] **D1** `[miolo]` — Dado um alvo e os nomes das specs do lote, o driver monta o estado lendo `<alvo>/docs/specs/<nome>.md` de cada uma, via `lote.spec_do_lote`.
- [ ] **D2** `[plataforma]` — A decisão é gravada no registro **antes** da invocação que ela ordena. Interromper o driver e reexecutar não repete uma tentativa já contada.
- [ ] **D3** `[plataforma]` — O número de tentativas vem de `registro.contar_tentativas`, nunca de contador em memória do processo.
- [ ] **D4** `[plataforma]` — Atingido o número máximo de invocações do ciclo, o driver escala com motivo `fusivel`. Nenhuma saída confunde `fusivel` com `teto-de-tentativas`.
- [ ] **D5** `[miolo]` — Falha de invocação (exit code ou artefato ausente, conforme `roteador-driver-invocacao`) resulta em `escalar`. Nunca em avançar para a próxima fase.

**Alvo**

- [ ] **D6** `[integração]` — O alvo é parâmetro obrigatório. Nenhum caminho é resolvido relativo ao diretório onde o método está instalado.
- [ ] **D7** `[integração]` — Dois alvos diferentes na mesma máquina não compartilham registro nem veredito: rodar o driver em A não altera arquivo nenhum em B.
- [ ] **D8** `[miolo]` — O ref base passado a `verificar` é o que foi capturado antes da **primeira** invocação de `codificar` daquela spec, lido do registro. Retentativa não reencurta o diff.

**Saída para o humano**

- [ ] **D9** `[miolo]` — Ao escalar, o driver informa motivo, spec, evidência e os caminhos dos artefatos — e **não** transcreve conteúdo de veredito.
- [ ] **D10** `[miolo]` — Ao encerrar o lote, o driver informa as três listas de `DecisaoDoLote`: fechadas, quarentena, e o que falta a cada uma em quarentena.
- [ ] **D11** `[plataforma]` — Em modo seco, o driver informa a próxima decisão e os insumos que passaria, sem invocar processo, sem commitar e sem escrever no registro.

## Contrato técnico

- CLI: `python tooling/loop/driver.py --alvo <path> --specs a,b,c [--seco] [--fusivel N] [--teto N]`.
- Fusível: default **30** invocações por ciclo. É rede, não controle primário — o que costuma disparar já está limitado pelo teto por spec.
- Os insumos passados a cada fase são os que a skill declara na seção `## Insumos` dela. Insumo que o driver não tem é `escalar`, nunca improviso.
- O instante gravado no registro é carimbado aqui: o núcleo não lê relógio.
- O driver é a única camada que decide **e** toca o mundo; ele compõe `roteador.decidir`, `lote.decidir_lote` e a invocação, sem reimplementar nenhuma regra dos três.

## Fora de escopo

- **`especificar` × N e o gate do lote.** O driver parte de specs **já aprovadas**. Gerar spec a partir de pedido muda a interface de entrada e é outra demanda — esta fecha sozinha sem ela.
- **Portar para outro harness.** A decisão já é pura e portátil; este driver é deliberadamente específico do Claude Code, e é isso que ele existe para provar primeiro.
- **Reprocessar quarentena na mesma execução.** Destravar exige insumo novo, e insumo novo vem do humano.
- **Paralelismo entre specs.** Uma fase por vez: duas rodando no mesmo alvo disputariam o mesmo working tree.

## Plano

1. `tooling/loop/driver.py` — montagem do estado (D1), laço com registro antes da invocação (D2, D3), fusível (D4), tratamento de falha (D5), alvo (D6, D7), ref base (D8).
2. Apresentação e CLI, no mesmo arquivo: escalada (D9), fechamento (D10), modo seco (D11).
3. `tooling/loop/tests/test_driver.py`, com invocador falso e alvo temporário.

Sem fatias: os critérios de `plataforma`, `integração` e `miolo` compartilham o laço, e separá-los produziria reconciliação.

## Perguntas em aberto

Nenhuma.
