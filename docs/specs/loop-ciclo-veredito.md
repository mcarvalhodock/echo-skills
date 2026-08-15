# loop-ciclo — veredito

Base: `docs/specs/loop-ciclo.md` contra `git diff 23f4166 -- tooling/loop/`.
Nada além do diff e da spec foi lido; onde a decisão depende de código não
mostrado no diff, isso está dito.

- **R1** — atendido
- **R2** — atendido
- **R3** — atendido
- **R4** — atendido
- **R5** — atendido
- **R6** — atendido
- **R7** — atendido
- **R8** — atendido

## Porquê

**R1 — escalada gravada.** `driver.rodar` ganhou uma gravação incondicional
depois do laço, com `decisao=decisao.decisao` e a mesma assinatura das
invocações (`instante`, `alvo`, `spec`) — logo, mesma linha de campos fixos, sem
campo novo. O laço só sai quando `decisao.decisao.acao` deixa de ser `INVOCAR`
(ou por `break`), então a decisão de `escalar` é exatamente a que chega nessa
gravação. `test_escalada_e_gravada` confirma `transicao == "escalar"` e
`motivo == "defeito-de-spec"` no registro. A guarda do alvo, que o contrato
técnico isenta, não passa por esse ponto — ela aborta antes de `rodar` chegar
ali.

**R2 — encerramento do lote gravado.** É a mesma gravação final. O `break`
existente no topo do laço tira o fluxo antes de executar a fase, e a decisão
`invocar: homologar` sobrevive intacta até a gravação. `spec` é preenchida com
`ultima_spec`, variável nova inicializada com `decisao.proxima_spec or ""` e
atualizada a cada iteração — ou seja, a linha terminal carrega a última spec
tocada, não vazio, no caso comum. `test_encerramento_do_lote_e_gravado` cobre a
gravação no nível do registro e
`test_a_linha_terminal_nunca_e_uma_invocacao_de_codificar` cobre no nível do
driver o caso `"fechamento"`, afirmando `ciclo_encerrado(...)` verdadeiro.

**R3 — última linha terminal vira ciclo novo.** `registro.ciclo_encerrado` lê a
última linha e compara `transicao` contra `_TRANSICOES_TERMINAIS`, que é
exatamente `("escalar", "invocar:homologar")` — o par do contrato técnico, e
derivado dos enums, não de literais soltos. `arquivar_se_encerrado` renomeia e
devolve o destino; o driver o chama na abertura, antes de qualquer decisão, de
modo que o ciclo seguinte encontra o arquivo ausente e começa em zero.
`test_ciclo_encerrado_e_arquivado_e_o_novo_comeca_vazio` verifica os três fatos
(destino, conteúdo, origem sumida).
Ressalva sem impacto no critério: a chamada está sob `if not config.seco`. Em
execução seca não há ciclo a arquivar; a gravação final, porém, ficou fora desse
`if`, e se `gravar` não for inerte em modo seco isso escreveria registro numa
execução que não arquiva. A definição de `gravar` não aparece no diff, então
esse ponto não é decidível aqui — mas ele não é o que R3 pede.

**R4 — última linha não terminal retoma.** Caminho complementar do mesmo
predicado: `arquivar_se_encerrado` devolve `None` e não toca no arquivo quando a
última linha é uma invocação de meio. O cenário `Ctrl+C` é coberto por
construção: a gravação terminal só acontece na saída normal do laço, então uma
execução cortada deixa como última linha uma invocação, e a próxima retoma.
`test_invocacao_no_meio_nao_e_terminal` e
`test_ciclo_interrompido_nao_e_arquivado` cobrem os dois lados.
O risco real deste critério é o inverso — o laço sair por fusível/teto/falha com
`decisao` ainda em `invocar:codificar`, produzindo uma linha final não terminal e
uma tentativa fantasma. O bloco de `break` que garante que isso não ocorre está
fora do diff, mas
`test_a_linha_terminal_nunca_e_uma_invocacao_de_codificar` exercita as quatro
saídas (fusível, teto, falha de executor, fechamento) contra o driver de verdade
e afirma que nenhuma delas termina em `invocar:codificar`. Critério coberto por
teste, não por leitura do trecho.

**R5 — arquivamento fiel e sem colisão.** `Path.rename` move o inode; não há
releitura nem reescrita, logo a preservação byte a byte é estrutural, e
`test_arquivamento_preserva_byte_a_byte` a confirma inclusive com acentuação
(isto é, sem passar por recodificação). O nome vem do laço `while (destino :=
...-{numero}...).exists(): numero += 1`, começando em 1 — menor inteiro livre,
derivado do diretório e não de relógio, como o contrato técnico exige, e o
formato bate com `<alvo>/.sle/loop-<n>.jsonl` porque `origem.stem`/`suffix` vêm
do próprio `loop.jsonl`. `test_arquivamentos_sucessivos_nao_colidem` percorre
1-2-3 e checa o conteúdo do diretório.

**R6 — registro inexistente.** `ciclo_encerrado` devolve `False` quando
`linhas(...)` vem vazia, e `arquivar_se_encerrado` sai por esse mesmo `False`
antes de qualquer `rename` — sem `exists()` explícito, sem `try`. Isso só é
correto se `registro.linhas` tolerar arquivo ausente; o corpo dessa função é
anterior ao diff e não aparece nele. O comportamento está afirmado por
`test_registro_inexistente_e_ciclo_novo` (que também checa que nada foi criado
no diretório) e por `test_registro_vazio_nao_quebra` para o arquivo vazio, que a
spec não pediu mas que é o vizinho perigoso do caso.

**R7 — contagem só do ciclo corrente.** Nada mudou em `contar_tentativas`, como
o contrato técnico manda: quem muda o resultado é o arquivamento na abertura,
que deixa o driver contando um arquivo novo. `test_o_driver_arquiva_e_a_spec_
emendada_nao_nasce_esgotada` reproduz o cenário inteiro pelo driver — teto 2
estourado, segunda execução no mesmo alvo — e verifica `loop-1.jsonl` criado,
fase final `HOMOLOGAR` e contagem 1 (a tentativa nova), não 3.
`test_tentativas_do_ciclo_anterior_nao_contam` isola o mesmo efeito no registro
(3 → 0). A ressalva do `config.seco` anotada em R3 vale aqui também: em modo
seco a contagem continuaria olhando o ciclo anterior.

**R8 — acúmulo dentro do ciclo.** Consequência direta de R4: sem arquivamento, o
arquivo é o mesmo e `contar_tentativas` soma as invocações de `codificar` das
duas execuções. `test_tentativas_acumulam_dentro_do_mesmo_ciclo` grava, deixa em
estado não terminal, confirma que o arquivamento não ocorre e vê a contagem ir a
2. A ausência de tentativa fantasma na linha terminal (R4) é o que impede esse
acúmulo de contar uma invocação que não houve.

## Observação

O diff carrega também mudanças em `git_alvo.py` (exceção de
`.sle/loop*.jsonl` na detecção de sujeira e no `add` da tentativa) com testes
marcados `spec:I5` e `spec:I7`. Não são critérios desta spec e não foram
julgados aqui; são pré-condição prática dela — sem isso o registro escrito no
alvo reprovaria a guarda da execução seguinte.
