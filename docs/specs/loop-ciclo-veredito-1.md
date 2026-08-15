# loop-ciclo — veredito

Base: `docs/specs/loop-ciclo.md` contra `git diff 23f4166 -- tooling/loop/`.
Evidência limitada ao diff: trechos de `driver.py` e `registro.py` fora dos hunks
não foram lidos, e isso está dito onde pesa.

- **R1** — atendido
- **R2** — atendido
- **R3** — atendido
- **R4** — atendido
- **R5** — atendido
- **R6** — atendido
- **R7** — atendido
- **R8** — não verificável

## Porquê

**R1** — `driver.rodar` passa a chamar `gravar(caminho_reg, decisao=decisao.decisao,
instante=carimbar(), alvo=alvo, spec=ultima_spec)` depois do laço, com a mesma
função e a mesma assinatura usadas para as invocações de dentro do laço; a linha
gravada é portanto a mesma forma de campos fixos, não um formato paralelo. Quando o
laço termina em `escalar`, é essa decisão que vai para o registro. `ultima_spec` é
inicializada com `decisao.proxima_spec or ""` antes do laço e reatribuída a cada
volta, então a escalada carrega a spec em que ela ocorreu — inclusive quando o laço
nem chega a rodar uma vez. A escalada por guarda do alvo, que o contrato técnico
excluiu, não passa por esse ponto porque a guarda aborta antes; consistente com o
escrito. `test_escalada_e_gravada` fixa `transicao == "escalar"` e o motivo.

**R2** — o mesmo `gravar` pós-laço cobre o encerramento do lote. A condição do laço
é `while decisao.decisao.acao is Acao.INVOCAR`, e existe um `break` interno antes da
execução da fase — é por ele que `invocar: homologar` sai do laço sem ser executada e
chega ao `gravar` final. `test_encerramento_do_lote_e_gravado` verifica a linha
`invocar:homologar` no arquivo.

**R3** — `registro.ciclo_encerrado` lê a última linha e compara `transicao` contra
`_TRANSICOES_TERMINAIS = (escalar, invocar:homologar)`; `arquivar_se_encerrado`
renomeia quando encerrado, e o driver a chama na abertura, antes de qualquer
gravação (`if not config.seco: registro.arquivar_se_encerrado(caminho_reg)`). Depois
do rename o caminho corrente não existe mais, então as gravações da execução seguinte
abrem arquivo novo. A ressalva do modo `seco` não fere o critério: em modo seco não há
ciclo a encerrar nem registro a abrir. Coberto por
`test_ciclo_encerrado_e_arquivado_e_o_novo_comeca_vazio` e
`test_escalada_e_homologar_sao_terminais`.

**R4** — `arquivar_se_encerrado` devolve `None` e não mexe no arquivo quando a última
linha não é terminal (`test_ciclo_interrompido_nao_e_arquivado`). Para o caso do
`Ctrl+C`: o `gravar` final está no corpo de `rodar`, sem `try`/`finally` no diff, de
modo que um `KeyboardInterrupt` propaga antes dele e a última linha em disco continua
sendo uma invocação — não terminal. A execução seguinte, portanto, retoma o mesmo
arquivo. É o comportamento exigido, e ele vem da ausência de captura, não de código
que trate o sinal.

**R5** — `origem.rename(destino)` é renomeação, não cópia com reescrita: o conteúdo é
preservado byte a byte, incluindo o encoding do que já estava gravado
(`test_arquivamento_preserva_byte_a_byte` compara `read_bytes()` e ainda checa uma
spec acentuada). O nome sai do laço `while (destino := ...f"{stem}-{numero}{suffix}").exists(): numero += 1`,
partindo de 1 — o menor inteiro livre, derivado do diretório e não do relógio, como
o contrato técnico pede. `test_arquivamentos_sucessivos_nao_colidem` percorre
`loop-1`, `loop-2`, `loop-3`.

**R6** — `ciclo_encerrado` devolve `False` quando `linhas(caminho)` vem vazio, e
`arquivar_se_encerrado` devolve `None` sem tocar em disco nesse caso; nenhum
`Path.exists` prévio é necessário porque o rename só é alcançado depois do teste.
`test_registro_inexistente_e_ciclo_novo` afirma ainda que o diretório continua vazio,
e `test_registro_vazio_nao_quebra` cobre o arquivo existente com zero linhas. O que
não está no diff é o corpo de `linhas()` — ele é anterior a este commit e a ausência
de erro nos testes é a evidência de que já tolerava arquivo ausente.

**R7** — a contagem não mudou: `contar_tentativas` continua somando linhas
`invocar:codificar` do arquivo que recebe. O isolamento por ciclo vem do arquivamento
na abertura, que tira as linhas antigas do caminho corrente. `test_tentativas_do_ciclo_anterior_nao_contam`
mostra 3 → 0 depois do arquivamento, e
`test_o_driver_arquiva_e_a_spec_emendada_nao_nasce_esgotada` reproduz o cenário
inteiro pelo driver: primeira execução estoura o teto 2 com `TETO_DE_TENTATIVAS`,
segunda execução acha `.sle/loop-1.jsonl` arquivado, chega a `HOMOLOGAR` e conta 1
tentativa nova.

**R8** — o mecanismo está certo no que o diff mostra: sem arquivamento, as gravações
da execução seguinte acumulam no mesmo arquivo, e `test_tentativas_acumulam_dentro_do_mesmo_ciclo`
chega a 2. O que impede o verdicto de atendido é o `gravar` pós-laço combinado com o
`break` interno, cujo predicado está fora do hunk. Se esse `break` puder disparar com
`fase is CODIFICAR` — no modo seco, num limite de invocações, ou em qualquer guarda
de meio de laço —, a decisão gravada ao final será uma linha `invocar:codificar` de
uma invocação que não aconteceu, e `contar_tentativas` a somará na execução seguinte,
que é exatamente a contagem que R8 governa. Se o único `break` for o de `HOMOLOGAR`,
o risco não existe. Não dá para decidir isso sem ler o trecho de `driver.py` que o
diff omite, e nenhum teste do diff exercita uma saída do laço em `codificar`.
