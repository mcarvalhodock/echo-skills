# Veredito — loop-pedido-interativo

Base: `git diff d8a8698 -- tooling/loop`.

- **Q1** — atendido
- **Q2** — atendido
- **Q3** — atendido
- **Q4** — atendido
- **Q5** — atendido
- **Q6** — atendido
- **Q7** — atendido
- **Q8** — atendido
- **Q9** — atendido

## Por quê

**Q1 — sessão interativa, sem captura.** `invocacao.executar_interativo` chama
`subprocess.run(list(comando), cwd=str(cwd))` sem `capture_output`, `stdout`,
`stderr`, `input` ou `text`: os três descritores são herdados do terminal.
Retorna `(returncode, "")`, e o comentário assume a string vazia como honesta —
ninguém leu. `invocar` passa a escolher o executor por `interativo: bool = False`
(`executar_interativo if interativo else executar_de_verdade`), e
`rodar_pedidos` invoca com `interativo=True`. O teste
`test_a_sessao_interativa_nao_captura_saida` fixa isso pela negativa: afirma que
nenhuma das cinco chaves de captura chega ao `subprocess.run`, o que é mais
forte que checar só `capture_output`.

**Q2 — comando interativo configurável e sem flag headless.**
`COMANDO_INTERATIVO_PADRAO = ("claude", MARCADOR)` — sem `-p`, com o marcador
preservado. `Config.comando_interativo` recebe esse default e a CLI ganhou
`--comando-interativo`, parseado por `.split()` como o `--comando`. O teste
`test_o_comando_interativo_e_configuravel` prova o caminho de ponta a ponta
(`("agent", "{prompt}")` chega ao executor). Detalhe correto de borda:
`_preparar` passou a receber o comando do segmento que vai rodar, e
`rodar_pedidos` lhe entrega `config.comando_interativo` — sem isso a validação
de marcador e de executável no PATH continuaria olhando para o headless e
deixaria passar template interativo quebrado.

**Q3 — uma sessão por vez.** A fila é um laço sequencial sobre os pedidos
(`invocacoes += 1` a cada volta) e a chamada é síncrona: `subprocess.run` sem
`Popen` nem concorrência em lugar nenhum do diff. Não há paralelismo a excluir.
`test_a_fila_espera_cada_sessao_terminar` cobra isso por efeito observável —
quando a segunda sessão começa, a spec da primeira já existe em disco
(`existentes == [[], ["cadastro.md"]]`), o que só vale se a primeira terminou.

**Q4 — o artefato continua sendo cobrado.** A chamada de `invocar` mantém
`artefato_esperado=f"docs/specs/{pedido.nome}.md"`; a única mudança na chamada é
o template e a flag. Em `invocacao.invocar`, a checagem
`presente = bool(artefato_esperado) and (Path(alvo)/artefato_esperado).exists()`
é independente da saída — e é justamente por isso que perder a saída não
enfraquece a cobrança. `test_a_spec_continua_sendo_cobrada` roda um executor que
devolve `(0, "")` sem escrever nada e afirma `Acao.ESCALAR`: exit code zero e
saída vazia não compram aprovação.

**Q5 — o segmento 2 segue headless.** `rodar` não foi tocado; `_preparar` mantém
`comando = comando or config.comando`, e nenhuma chamada de `invocar` fora de
`rodar_pedidos` passa `interativo`, cujo default é `False`.
`test_o_segmento_dois_continua_headless` afirma `all("-p" in comando ...)` sobre
todas as invocações de um ciclo de `codificar`/`verificar`/`homologar`.

**Q6 — `pedidos.md` não é sujeira.** `git_alvo.sujos` ganhou a exceção
`normalizado == ARQUIVO_DE_PEDIDOS` ao lado da escrituração, aplicada sobre o
caminho já normalizado (aspas removidas, barras invertidas trocadas) — a mesma
normalização que a escrituração usa. É igualdade de caminho exato, não prefixo,
e o contrato técnico exigia isso nominalmente: `test_nome_parecido_com_pedidos_
ainda_e_sujeira` prova que `pedidos-antigos.md` continua bloqueando.
`test_pedidos_nao_conta_como_sujeira` cobre o não versionado e o modificado.

**Q7 — commit próprio, antes da fila.** `commitar_pedidos` delega a `_commitar`
com `assunto="loop(pedidos): registrar pedidos"`, `marca="pedidos#registro"` e
`escopo=("--", ARQUIVO_DE_PEDIDOS)` — escopo estreito, então o commit não
arrasta mais nada. A chamada em `rodar_pedidos` está antes do laço da fila, o
que satisfaz a ordem exigida pelo contrato técnico ("antes da primeira sessão,
não junto da primeira spec"). `test_pedidos_vira_commit_proprio_antes_da_fila`
verifica os três eixos: o assunto é o do commit mais antigo com marca `SLE-Loop`
(portanto precede o da spec), o `show --name-only` lista `pedidos.md` e só ele,
e o corpo traz `SLE-Loop: pedidos#registro`.

**Q8 — sem mudança, sem commit.** `_commitar` mantém a verificação de índice
vazio, agora escopada pelo mesmo `escopo` recebido; com `pedidos.md` versionado
e intacto, `git add -A -- pedidos.md` não estagia nada e a função retorna `None`.
`test_pedidos_ja_versionado_nao_gera_commit` afirma a ausência do assunto e
ainda amarra a contagem exata de commits novos (`antes + 2`), o que impede um
commit vazio passar despercebido.

**Q9 — modo seco não abre sessão nem commita.** `test_modo_seco_nao_abre_sessao_
nem_commita` afirma as três coisas de uma vez: `executor.chamadas == []`,
contagem de commits inalterada e `pedidos.md` ainda fora do `ls-files`. Ressalva
de leitura: a guarda de `--seco` em `rodar_pedidos` não aparece no diff (é código
anterior a `d8a8698`), então o que o diff demonstra é que a inserção de
`commitar_pedidos` ficou depois dessa saída antecipada — evidência indireta, mas
o teste é direto e usa o alvo com `pedidos.md` não versionado, que é o caso em
que um commit indevido apareceria.

## Observações que não são veredito

- Todos os nove critérios têm teste dedicado com marcação `spec:Qn`, e nenhum
  teste depende do texto de retorno da fase — coerente com o contrato técnico de
  que `Resultado.saida` fica vazio no modo interativo.
- O README foi atualizado junto (tabela de flags com `--comando-interativo` e a
  seção dizendo que o segmento 1 é conversa), o que não é critério, mas fecha a
  documentação da flag nova.
