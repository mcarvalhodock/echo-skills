# loop-especificar — veredito

Base: `docs/specs/loop-especificar.md` contra `git diff 7c85547 -- tooling/loop`.
Julgamento por leitura do diff; a suíte não foi executada.

- **P1** — atendido
- **P2** — atendido
- **P3** — atendido
- **P4** — atendido
- **P5** — atendido
- **P6** — atendido
- **P7** — atendido
- **P8** — atendido
- **P9** — atendido
- **P10** — atendido
- **P11** — atendido

## Por quê

**P1** — `pedidos.ler` (`tooling/loop/pedidos.py`) varre `^##\s+(.+?)$` com `finditer`, itera na ordem do
arquivo e fatia o corpo do fim de um cabeçalho até o `start()` do seguinte (fim do texto no último).
O que vem antes do primeiro `##` fica de fora por construção. Devolve `Pedido(nome, texto)`.
`test_pedidos.py` cobre ordem, não-invasão entre pedidos, prosa inicial e pedido de corpo vazio.

**P2** — `NOME_VALIDO = ^[a-z0-9-]+$`. Cabeçalho que não casa vai para `Leitura.invalidos` com o
título **literal**; não há slugificação, `lower()`, troca de espaço por hífen ou remoção de acento em
nenhum ponto do módulo. `rodar_pedidos` testa `leitura.invalidos` antes de qualquer invocação e
retorna `_travado(...)` com `f"cabeçalho não serve como nome de spec: {titulo}"` — ESCALAR nomeando o
cabeçalho recusado. `test_cabecalho_invalido_escala_nomeando_o_cabecalho` ainda assere
`executor.chamadas == []`, ou seja, a fila inteira para antes de nascer processo.

**P3** — três portas, todas para ESCALAR e nenhuma para fila vazia bem-sucedida: arquivo ausente
(`if not caminho.exists()` → `arquivo de pedidos não encontrado`), e `if not leitura.pedidos` →
`nenhum pedido em <caminho>`, que cobre tanto arquivo vazio (`ler("")` devolve `Leitura((), ())`)
quanto arquivo só com prosa ou só com `#` de nível 1. Não existe caminho em que `leitura.pedidos`
vazio siga adiante.

**P4** — `if caminho_da_spec(alvo, pedido.nome).exists():` aparece **antes** do `gravar`/`invocar`,
faz `continue` e empurra `f"  {pedido.nome}: pulado — a spec já existe"` para o relatório. Nenhuma
escrita toca a spec anterior. O teste confirma uma única chamada ao executor e o conteúdo original
preservado byte a byte. O modo seco tem a linha equivalente ("pularia — a spec já existe").

**P5** — um `invocar(Fase.ESPECIFICAR, ...)` por pedido dentro do laço, com
`prompt_de(...)` produzindo `Use a skill especificar. Nome da spec: <nome>. Alvo: <alvo>.\n\nPedido:\n<texto>`
— os três elementos exigidos. O "processo novo" vem de `invocacao.invocar`, reusado sem alteração
(não aparece no diff): o driver não mantém sessão nem acumula histórico entre pedidos, e o template
`config.comando` é o mesmo do segmento 2, que já nasce processo por fase.

**P6** — `artefato_esperado=f"docs/specs/{pedido.nome}.md"` é passado a `invocar`, e o caminho é
conhecido antes da invocação justamente porque P2 proíbe derivação de nome. `if not resultado.ok`
trata ausência do artefato pelo mesmo ramo de qualquer falha: `Motivo.FALHA_DE_INVOCACAO`, gravação
do final e retorno com o texto da escalada. `test_spec_nao_producida_escala` usa executor que
retorna exit 0 sem escrever nada e confirma ESCALAR — isto é, o veredito não confia no exit code.

**P7** — `git_alvo.commitar_spec` monta assunto `loop(<spec>): especificar` e marca `<spec>#spec`,
delegando ao `_commitar` extraído de `commitar_tentativa`, que preserva o pathspec com
`:!ESCRITURACAO_DO_LOOP` e o `commit` com caminhos (não grava índice alheio). O trailer é o mesmo
`TRAILER` da tentativa de codificar, como o contrato técnico pede. O commit é emitido logo após o
`resultado.ok`, por spec, e só quando `com_git` — o que é coerente com o resto do driver, que trata
alvo sem git como caso avisado e não como erro.

**P8** — não há `Fase.CODIFICAR` em lugar nenhum de `rodar_pedidos`; `roteador.decidir` não é
chamado, e o final é sempre `_decisao_solta(Motivo.GATE_SPEC_APROVADA, ())`. A única transição
gravada por iteração é `invocar:especificar`. O `main` escolhe **um** segmento (`rodar_pedidos if
config.pedidos else rodar`) e retorna; não encadeia. O teste checa as três frentes: ação, ausência
de "codificar" nos prompts e ausência de `invocar:codificar` no registro.

**P9** — `_linha_do_relatorio` lê a spec recém-produzida, chama `secoes.criterios` e emite
`<nome>: <N> critérios [<domínios ordenados>]`. `secoes.criterios` casa
`- [ ] **C1** \`[miolo, plataforma]\`` com o checkbox e o bloco de domínio opcionais, devolvendo
`(identificador, domínios)` na ordem. Ressalva de robustez, não de atendimento: o identificador
exigido é `[A-Z]\d+` — uma letra só; spec que usasse prefixo de duas letras não seria contada.
As specs deste repositório usam prefixo de uma letra.

**P10** — a mesma linha recebe `— bloqueada: <perguntas separadas por ";">` quando
`secoes.perguntas_em_aberto` devolve itens. Como aquela função extrai **itens de lista** da seção, o
`Nenhuma.` em prosa do caso comum não marca a spec como bloqueada — o teste verifica exatamente essa
assimetria, exigindo "bloqueada" na linha de `cobranca` e sua ausência na de `cadastro`.

**P11** — `TETO_DE_CRITERIOS = 15` no driver, com comentário declarando que espelha o teto de
`especificar`, e `if len(criterios) > TETO_DE_CRITERIOS:` acrescenta `— acima do teto de 15`.
Comparação estrita: 15 critérios não marcam, 16 marcam — que é a leitura de "estoura o teto de 15".
O relatório expõe o furo e segue; não bloqueia nem trunca, como a spec descreve. O teste usa 18
critérios e confirma marca em uma linha e ausência de marca na outra.
