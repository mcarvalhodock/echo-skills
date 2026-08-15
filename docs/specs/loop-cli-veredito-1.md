# loop-cli — veredito

Base: `git diff 95c4a88 -- tooling/loop scripts`. Spec: `docs/specs/loop-cli.md`.

- **S1** — atendido
- **S2** — atendido
- **S3** — atendido
- **S4** — atendido
- **S5** — não atendido
- **S6** — atendido
- **S7** — atendido
- **S8** — atendido
- **S9** — atendido
- **S10** — atendido
- **S11** — atendido
- **S12** — atendido

## Por quê

**S1** — `main` ganhou subparsers e o parser `pedir` recebe `_comuns` (`--alvo` obrigatório, `--seco`, `--comando`, `--comando-interativo`) mais `--pedidos` com default `pedidos.md`. O despacho é `segmento = rodar_pedidos if args.subcomando == "pedir" else rodar`, e `Config.pedidos` continua alimentado, então o segmento 1 roda pelo mesmo caminho de antes — o `--pedidos` sem valor, que antes era `nargs="?"/const`, virou default do subcomando, o que preserva o comportamento do uso corrente. `test_cli.py::test_pedir_roda_o_segmento_um` fixa o despacho.

**S2** — o parser `rodar` exige `--specs`, mantém `--fusivel` e `--teto`, e despacha para `driver.rodar`, que é o laço headless (usa `config.comando`, não o interativo). `test_rodar_roda_o_segmento_dois` fixa.

**S3** — sem subcomando, `main` chama `analisador.print_help()` e levanta `SystemExit(2)`. Com subcomando desconhecido, o próprio `argparse` recusa a escolha, imprime o `usage` — que lista `{pedir,rodar}` — e sai com 2. `test_sem_subcomando_ou_com_desconhecido_mostra_ajuda_e_falha` cobre os dois casos e checa o código não-zero. Ressalva de grau, não de atendimento: no caminho do subcomando desconhecido o que sai é o `usage` do argparse, não a ajuda completa; a spec pede "mostra a ajuda" sem distinguir os dois.

**S4** — `--seco` está em `_comuns`, logo é flag dos dois subparsers, e chega como `config.seco` em ambos os segmentos. No laço, o `if config.seco: break` acontece antes de `invocar` e antes de `gravar`, de modo que nada é invocado, registrado ou commitado — `test_modo_seco_nao_invoca_homologar` verifica inclusive que o arquivo de registro não nasce e que `homologar` não é chamada. `test_seco_vale_nos_dois_subcomandos` fixa a paridade entre `pedir` e `rodar`.

**S5** — os dois arquivos existem e chamam o driver por caminho relativo ao clone (`scripts/sle` resolve `dirname $0/..` e dá `exec python`; `scripts/sle.ps1` usa `Split-Path -Parent $PSScriptRoot` e propaga `$LASTEXITCODE`). O que falha é o "executável" do critério: o diff cria `scripts/sle` com `new file mode 100644`, sem bit de execução, então em POSIX `./scripts/sle` não roda — o usuário volta a precisar digitar um interpretador na frente, que é exatamente o que o critério existe para eliminar. O teste `test_os_involucros_existem_e_apontam_para_o_driver` não pega isso porque só inspeciona `exists()` e o conteúdo, nunca o modo nem uma execução real.

**S6** — `GATES_PLANEJADOS = (Motivo.GATE_SPEC_APROVADA, Motivo.GATE_CHECKLIST)` e o retorno virou `0 if relato.final.decisao.motivo in GATES_PLANEJADOS else 1`, o que troca o eixo do código de saída de "ação" para "motivo" — exatamente o que S6/S7 pedem. `test_gate_planejado_sai_com_zero` parametriza os dois motivos. Observação de escopo, fora do critério: como o teste passa a exigir motivo de gate, a parada de `--seco` (que termina com ação `INVOCAR` e motivo que não é gate) passa a sair com 1, onde antes saía 0; nenhum critério desta spec fala do código de saída do ensaio.

**S7** — o `else 1` cobre todo motivo fora da dupla de gates, e `test_excecao_sai_com_nao_zero` parametriza os sete motivos nomeados no critério, um a um.

**S8** — o `break` que interrompia o laço em `Fase.HOMOLOGAR` foi removido; no lugar entrou `fecha_o_ciclo = fase is Fase.HOMOLOGAR`, que só muda os insumos e segue invocando. `test_o_lote_esgotado_invoca_homologar` confirma uma invocação de `homologar` num lote esgotado, e `test_homologar_conta_no_fusivel` confirma que ela é invocação como qualquer outra (`invocacoes == 3`). A condição "pelo menos uma spec fechada" mora no roteador/lote, fora deste diff, mas os testes atualizados em `test_driver.py`, `test_alvo.py`, `test_ciclo.py` e `test_agente.py` — que trocaram `fase is Fase.HOMOLOGAR` por `motivo is Motivo.GATE_CHECKLIST` — mostram que o fim de lote agora atravessa a fase em vez de parar nela.

**S9** — `prompt_de` para `homologar` deixou de ser só o alvo e passou a montar `Specs do ciclo: {spec}. Vereditos: {escopo}. Ref base do ciclo: {base}. Alvo: {alvo}.`, com `spec` = `", ".join(decisao.fechadas)` e `escopo` = os `caminho_do_veredito(alvo, n)` das fechadas. `test_o_prompt_de_homologar_carrega_specs_vereditos_e_base` afere os quatro insumos num lote de duas specs (nomes, os dois `-veredito.md`, o SHA base e o caminho do alvo).

**S10** — `_base_do_ciclo` varre `registro.linhas` do começo e devolve a evidência da **primeira** linha `invocar:codificar`, e o laço usa esse valor no lugar do `_base_registrada(spec)` quando `fecha_o_ciclo`. `test_o_ref_base_do_ciclo_e_o_da_primeira_spec` não se contenta com afirmar o SHA certo: também exige que o HEAD final — deslocado pelos commits de tentativa do ciclo — **não** apareça no prompt, o que é o jeito de falsificar "pegou o da última".

**S11** — a saída é guardada crua em `saida_da_homologacao = resultado.saida`, sem transformação, e no fim entra em `partes` como último elemento junto do texto de fechamento e do texto da escalada. Não há corte, truncagem nem paráfrase no caminho. `test_a_saida_de_homologar_e_repassada_na_integra` verifica `CHECKLIST in relato.texto` e, no mesmo teste, que a parada final é `Motivo.GATE_CHECKLIST` — as duas metades do critério.

**S12** — a atribuição de `saida_da_homologacao` vem **depois** do bloco de falha, que faz `break` com `Motivo.FALHA_DE_INVOCACAO`; logo, `homologar` que estoura não deixa saída para repassar e não emite o texto de fechamento, caindo em `escalar` como qualquer outra fase. Coerente com o contrato de não haver artefato esperado em disco: `artefato_esperado` segue `None` para tudo que não é `VERIFICAR`, então o sucesso de `homologar` é só o exit code. `test_falha_de_homologar_escala_e_nao_fecha_o_ciclo` cobre com exit 4.
