# loop-cli

## Intenção
O loop vira uma ferramenta com nome e subcomandos, e o segmento 2 passa a ir até o fim: roda `homologar` sozinho e para só no checklist.

## Depende de
`loop-especificar` e `loop-pedido-interativo` — os dois segmentos que os subcomandos expõem.

## Critérios

**A ferramenta**

- [ ] **S1** `[integração]` — `sle pedir --alvo <caminho>` roda o segmento 1, interativo, com o mesmo comportamento de hoje.
- [ ] **S2** `[integração]` — `sle rodar --alvo <caminho> --specs a,b` roda o segmento 2, headless.
- [ ] **S3** `[integração]` — Sem subcomando, ou com subcomando desconhecido, a ferramenta mostra a ajuda e sai com código não-zero.
- [ ] **S4** `[integração]` — `--seco` vale nos dois subcomandos, com o mesmo significado: nada é invocado, registrado ou commitado.
- [ ] **S5** `[plataforma]` — Existe um invólucro executável — `scripts/sle` e `scripts/sle.ps1` — que roda sem o usuário digitar `python` nem o caminho do driver.

**Sair dizendo o que aconteceu**

- [ ] **S6** `[integração]` — Parada em gate planejado (`gate-spec-aprovada`, `gate-checklist`) sai com código **0**.
- [ ] **S7** `[integração]` — Parada por exceção (`defeito-de-spec`, `teto-de-tentativas`, `fusivel`, `falha-de-invocacao`, `guarda-do-alvo`, `lote-vazio`, `dependencia-circular`) sai com código **não-zero**.

**Até o fim**

- [ ] **S8** `[miolo]` — Lote esgotado com pelo menos uma spec fechada resulta em **invocar** `homologar`, headless. O loop não para mais antes dela.
- [ ] **S9** `[integração]` — O prompt de `homologar` carrega os insumos que a skill declara: as specs do ciclo, os caminhos dos vereditos, o ref base do ciclo e o alvo.
- [ ] **S10** `[miolo]` — O ref base do ciclo é o da **primeira** spec que rodou neste ciclo, lido do registro — não o da última.
- [ ] **S11** `[miolo]` — Concluída `homologar`, a saída dela é repassada **na íntegra e sem resumo**, e o loop escala com `gate-checklist`.
- [ ] **S12** `[plataforma]` — Falha de invocação de `homologar` resulta em `escalar`, como qualquer outra fase. Nunca em ciclo declarado fechado.

## Contrato técnico

- Nome: `sle`. Invólucros em `scripts/sle` (sh) e `scripts/sle.ps1`, chamando o driver por caminho relativo ao clone. **Sem empacotamento**: o repositório não tem `pyproject.toml`, e criar um para dois invólucros pesaria mais que o retorno.
- Subcomandos por `argparse` com subparsers; `python tooling/loop/driver.py` continua funcionando, porque é o que os invólucros chamam e o que a suíte exercita.
- **Repassar a saída de `homologar` não fere a regra do `D3`.** Aquela regra é sobre a decisão nunca *usar* o texto de retorno — e não usa. Aqui o texto é repassado **verbatim** ao humano, que é o oposto de resumir: o que amacia um parecer é a paráfrase, não o encaminhamento. E `homologar` é a única fase cuja saída é endereçada a você e não tem arquivo próprio.
- `homologar` não tem artefato esperado em disco: o sucesso dela é exit code, e é por isso que `S12` existe separado.
- Reverte a decisão registrada em `d48cb49` — "o driver PARA ao chegar em `homologar`". O argumento de lá era que ela termina em gate humano de qualquer forma; o argumento melhor é que a suíte completa é a parte lenta e mecânica, e é justamente ela que merece rodar desatendida.

## Fora de escopo

- **Empacotar como pacote Python instalável.** Dois invólucros de três linhas resolvem, e um `pyproject.toml` traria versionamento, publicação e um ciclo de release que ninguém pediu.
- **Tornar `homologar` interativa.** Ela prepara perguntas e não as responde; conversa ali não acrescenta, e o checklist espera você de qualquer forma.
- **Um subcomando que faça os dois segmentos seguidos.** Existe um gate humano entre eles, e um atalho que o pule seria o mesmo que não tê-lo.
- **Responder o checklist, ou registrar a resposta.** Arquitetura é julgamento humano, e não há onde guardar isso que não vire campo que alguém marca sem ler.

## Plano

1. `tooling/loop/driver.py` — subparsers, código de saída por tipo de parada, e a invocação de `homologar` com os insumos e o repasse da saída (S1–S4, S6–S12).
2. `scripts/sle` e `scripts/sle.ps1` — os invólucros (S5).
3. `tooling/loop/tests/test_cli.py` e `test_homologar.py`.

Sem fatias: os critérios de `integração` e `miolo` compartilham o mesmo laço e a mesma saída, e separá-los produziria reconciliação.

## Perguntas em aberto

Nenhuma.
