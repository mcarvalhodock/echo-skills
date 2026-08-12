# roteador-driver — veredito

Base: `docs/specs/roteador-driver.md` contra `git diff 1917568 -- tooling/loop/`
(`driver.py` novo, `tests/test_driver.py` novo, ampliações em `lote.py`,
`registro.py` e `roteador.py`).

- **D1** — atendido
- **D2** — atendido
- **D3** — atendido
- **D4** — atendido
- **D5** — atendido
- **D6** — atendido
- **D7** — atendido
- **D8** — atendido
- **D9** — atendido
- **D10** — atendido
- **D11** — atendido

## Porquê

**D1** — `montar_specs` (`driver.py`) compõe `caminho_da_spec(alvo, nome)` =
`<alvo>/docs/specs/<nome>.md`, lê o texto e entrega a `lote.spec_do_lote`, sem
parsear nada por conta própria. `rodar` chama `montar_specs(alvo, config.specs)`
como primeira coisa depois da guarda do alvo.
`test_monta_o_estado_lendo_as_specs_do_alvo` exercita o caminho com uma spec
livre e uma travada e confere que o `insumo_faltante` veio do parser de `lote`,
não do driver.

**D2** — no laço, `gravar(...)` precede textualmente a chamada a `invocar(...)`,
e não há caminho em que a invocação aconteça sem a gravação anterior (o `seco`
retorna antes das duas; o fusível quebra antes das duas). Como a tentativa é
contada no registro em disco *antes* do processo existir, uma interrupção no
meio da invocação deixa a tentativa já contada — a reexecução parte do registro
gravado e não reaproveita orçamento. `test_registra_a_decisao_antes_de_invocar`
prende a ordem com espiões (`ordem[:2] == ["registrou", "invocou"]`). Ressalva
sobre a evidência do critério: o teste cobre a ordem, não uma reexecução real
após kill; a não-repetição está garantida por construção (contagem derivada do
arquivo), não por teste.

**D3** — não existe contador de tentativas em memória. As duas leituras de
tentativa — `git_alvo.commitar_tentativa(..., tentativa=...)` e
`EstadoDoLote(tentativas=...)` — chamam `registro.contar_tentativas(caminho_reg,
spec)`, que agora é derivado de `registro.linhas` (releitura do arquivo a cada
chamada, sem cache). A única variável incremental do processo é `invocacoes`, e
ela alimenta só o fusível, que é outro eixo (D4).
`test_tentativas_vem_do_registro_e_nao_da_memoria` confere 2 tentativas
recontadas do disco após o ciclo.

**D4** — a checagem `if invocacoes >= config.fusivel` escala com
`Motivo.FUSIVEL`, membro novo do enum em `roteador.py`, textualmente separado de
`TETO_DE_TENTATIVAS` e com comentário registrando o porquê da separação. A saída
imprime `d.motivo.value` (`fusivel`), então nenhum texto de escalada por fusível
pode conter a palavra do outro motivo.
`test_fusivel_escala_com_motivo_proprio` roda com `fusivel=2, teto=99` (força o
fusível a disparar antes do teto), afirma o motivo, o número de invocações e a
ausência da string `teto-de-tentativas` no relato.

**D5** — `if not resultado.ok:` produz `_decisao_solta(Motivo.FALHA_DE_INVOCACAO,
...)` seguido de `break`, antes do commit da tentativa e antes de qualquer nova
chamada a `decidir_lote`; não há como uma invocação falha avançar de fase.
`test_falha_de_invocacao_escala_em_vez_de_avancar` usa exit code 3 e afirma
`ESCALAR` com exatamente uma chamada ao executor. O ramo "artefato ausente" é
delegado corretamente — o driver passa `artefato_esperado=docs/specs/<spec>-veredito.md`
para `verificar` e confia em `resultado.ok`; quem decide `ok` é `invocacao.py`,
que a própria spec remete a `roteador-driver-invocacao` e que está fora deste
diff. O que cabe a esta spec (tratar `not ok` como escalar) está atendido.

**D6** — `Config.alvo` é campo sem default num dataclass frozen, então
`Config(specs=...)` levanta `TypeError`; no CLI, `--alvo` é `required=True`.
Todos os caminhos tocados derivam do parâmetro: `caminho_da_spec`,
`caminho_do_veredito`, `registro.caminho_do_registro(alvo)`,
`git_alvo.impedimentos/head/commitar_tentativa(alvo)` e o `cwd` da invocação.
Não há `Path(__file__)`, `os.getcwd()` nem literal relativo no arquivo novo.
`test_alvo_e_obrigatorio` cobre a obrigatoriedade.

**D7** — consequência direta de D6: nenhuma escrita usa raiz que não seja
`config.alvo`. `test_dois_alvos_nao_se_misturam` roda o ciclo completo em A e
afirma que o registro de B não existe e que `B/docs/specs` está idêntico. A
verificação do teste é do registro e do diretório de specs, não de uma varredura
integral de B; o argumento de construção acima é o que fecha o resto.

**D8** — a captura é única e datada pelo registro: `base =
_base_registrada(caminho_reg, spec)` e só se for `None` e a fase for `CODIFICAR`
é que se lê `git_alvo.head(alvo)`. `_com_base` grava esse ref na `evidencia` da
**primeira** linha `invocar:codificar` da spec (a condição `ja_registrada is
None` impede sobrescrita nas retentativas), e `_base_registrada` devolve sempre a
primeira ocorrência varrendo `registro.linhas` na ordem. O `prompt_de(VERIFICAR)`
recebe esse mesmo valor. Como `codificar` sempre precede `verificar` no laço, o
ref já está no registro quando `verificar` é montada, e o commit de tentativa
(que move o HEAD) não afeta o valor lido.
`test_ref_base_e_o_de_antes_da_primeira_tentativa` afirma que as **duas**
invocações de `verificar` carregam o mesmo `rev-parse HEAD` inicial.

**D9** — `_texto_da_escalada` emite motivo, spec, evidência e os caminhos
(`spec em:`, `veredito em:`, `registro em:`); em nenhum ponto lê ou interpola o
conteúdo do veredito — `_veredito_de` só é chamado dentro do laço para alimentar
`decidir_lote`, e o `Relato` guarda apenas o texto montado.
`test_escalada_nao_transcreve_o_veredito` planta uma frase-sentinela no veredito
e afirma que ela não aparece no relato, enquanto o caminho do arquivo aparece.

**D10** — o encerramento normal do lote é o `break` em `Fase.HOMOLOGAR`, que
mantém `acao is INVOCAR` e por isso cai em `_texto_do_fechamento`, que imprime
`fechadas`, `quarentena` e uma linha `<nome> espera: ...` por item de
`insumos_faltantes` — as três listas de `DecisaoDoLote`.
`test_fechamento_informa_as_tres_listas` monta lote com uma livre, uma travada
por pergunta em aberto e uma dependente da travada, e confere as três presenças
mais o texto do insumo. Ressalva de escopo: encerramentos por escalada (fusível,
falha, guarda do alvo, lote vazio na abertura) usam `_texto_da_escalada` e não
trazem as três listas — leio D10 como sobre o encerramento do lote, coberto por
D9 no ramo de escalada, e não conto isso como falha.

**D11** — o ramo `if config.seco:` retorna antes de `gravar`, antes de `invocar`
e antes de `git_alvo.commitar_tentativa`, com `invocacoes=0`; o que roda antes
dele é só leitura (`git_alvo.impedimentos`, leitura das specs). `_texto_seco`
informa a próxima decisão (`acao:fase`), a spec e os insumos que passaria
(caminho da spec, alvo, teto, fusível).
`test_modo_seco_nao_invoca_nem_registra_nem_commita` afirma executor sem
chamadas, registro inexistente e contagem de commits inalterada.
