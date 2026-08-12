# Veredito — sle-casa

Base: `docs/specs/sle-casa.md` contra `git diff 2b44536` (casa.py, repos.py, driver.py e os três arquivos de teste). Leitura de código; a suíte não foi executada.

- **H1** — atendido
- **H2** — atendido
- **H3** — atendido
- **H4** — não atendido
- **H5** — não atendido
- **H6** — atendido
- **H7** — atendido
- **H8** — atendido
- **H9** — atendido
- **H10** — atendido
- **H11** — atendido

## Porquê

**H1** — `casa.caminho()` lê `SLE_CASA` e só cai para `Path.home() / ".sle"` quando a variável está ausente; a precedência é a ordem do próprio `if`. Os dois ramos têm teste (`test_a_casa_padrao_e_ponto_sle_no_home`, `test_a_variavel_de_ambiente_tem_precedencia`).

**H2** — `casa.garantir()` devolve `(destino, criada)`: `mkdir(parents=True)` só acontece quando o diretório não é um `is_dir()`, e o segundo elemento diz se nasceu agora. Quem imprime é `_comando_repo`, e só quando `criada` é verdadeiro — logo o aviso sai uma vez, não a cada execução. A criação é disparada pelo `repo`, que é o comando que precisa escrever; `resolver_cadastrado` apenas lê e não cria casa, o que é coerente com "execução que precise dela". Coberto por `test_casa_ausente_e_criada_e_a_criacao_e_informada`, `test_casa_existente_nao_e_reportada_como_criada` e, no nível de CLI, `test_add_cria_a_casa_e_informa_uma_vez`.

**H3** — Toda escrita do cadastro passa por `repos.gravar`, cujo destino é `casa.caminho() / "repos.md"` — não existe no diff nenhum caminho de escrita que derive do alvo. No sentido inverso, o que o `sle` faz com o alvo por causa de cadastro é `repos.resolver_cadastrado`, que só lê. A separação é estrutural (duas origens de caminho distintas), não uma checagem em runtime. Ressalva sobre a prova, não sobre o código: `test_a_casa_nao_fica_dentro_de_um_alvo` só passa porque a fixture aponta `SLE_CASA` para fora do alvo — a asserção é tautológica e não exercita nada; quem sustenta o critério é `test_criar_a_casa_nao_toca_em_alvo_nenhum`, que compara a árvore do alvo antes e depois.

**H4** — A primeira metade está feita: `_LINHA` reconhece `- <apelido>: <caminho>` e `ler` devolve os repositórios na ordem do arquivo. A segunda metade não chega a acontecer. `ler` acumula as linhas fora do formato em `Leitura.invalidos`, mas nenhum consumidor usa esse campo: `carregar()` devolve só `.repos`, `resolver` itera só `.repos`, `adicionar`/`remover` idem, e `_comando_repo` nunca toca em `invalidos`. Resultado: uma linha malformada em `repos.md` é ignorada em silêncio em toda invocação do `sle` — nunca é "recusada nomeando a linha" para quem está na frente do terminal. O único teste do ponto (`test_linha_fora_do_formato_e_recusada_nomeando_a_linha`) afirma sobre a estrutura de dados interna, não sobre uma recusa observável, e por isso passa apesar de o comportamento não existir.

**H5** — Preservação real no miolo: `adicionar` não reescreve nada, só concatena a linha nova ao texto recebido, e `remover` reconstrói a partir das linhas originais — ordem, comentários e linhas em branco internas sobrevivem, como `test_add_preserva_comentarios_ordem_e_linhas_em_branco` e `test_rm_remove_so_aquela_linha` mostram. Há, porém, um falsificador estreito e concreto: `adicionar` faz `corpo = texto.rstrip("\n")`, o que consome as linhas em branco no **fim** do arquivo. Um `repos.md` terminado em `- api: /x\n\n\n` vira `- api: /x\n- novo: /y\n` — linhas em branco autoradas que não "continuam como estavam". O critério enumera linhas em branco sem qualificar posição, então o caso o falsifica; nenhum teste cobre o fim de arquivo.

**H6** — `adicionar` monta o mapa `apelido -> caminho` do texto atual e levanta `ApelidoEmUso(f"`{apelido}` já aponta para {ja[apelido]}")` — o caminho vigente aparece na mensagem, e o retorno acontece antes de qualquer concatenação, então nada é sobrescrito. `_comando_repo` captura, imprime e devolve 1. Provado nos dois níveis: `test_apelido_repetido_e_recusado_nomeando_o_caminho_atual` (mensagem) e `test_add_de_apelido_repetido_sai_nao_zero` (código de saída não-zero + caminho na saída).

**H7** — O ramo `list` de `_comando_repo` imprime `f"{repo.apelido}: {repo.caminho}{estado}"`, com `estado` vindo de `repos.existe`, que é `Path(...).is_dir()` avaliado na hora. Os três elementos exigidos estão na linha. `test_list_mostra_apelido_caminho_e_se_existe` verifica apelido, caminho e a marca `(ausente)` na linha certa.

**H8** — `remover` filtra pelo apelido casado no `_LINHA` e mantém intacta qualquer outra linha, inclusive comentários e brancos; quando nada foi filtrado (`len(sobraram) == len(linhas)`) levanta `ApelidoDesconhecido` citando o apelido procurado, e o driver devolve não-zero. Coberto por `test_rm_remove_so_aquela_linha`, `test_rm_de_apelido_inexistente_e_recusado` e `test_rm_remove_e_apelido_desconhecido_sai_nao_zero`.

**H9** — `resolver` percorre o cadastro procurando apelido igual e, não achando, devolve `Path(valor)` — a precedência é literalmente a ordem do laço e do `return`. O caminho de produção está ligado: `Config(alvo=repos.resolver_cadastrado(args.alvo))` em `main`, com releitura do arquivo. Os dois ramos têm teste unitário (`test_resolver_prefere_apelido_e_cai_para_caminho`) e de CLI (`test_alvo_aceita_apelido_cadastrado`, `test_alvo_desconhecido_e_tratado_como_caminho`).

**H10** — A existência do caminho não participa de nenhuma decisão de fluxo: `ler` não filtra por existência, `carregar` devolve tudo, e `existe` só é consultado para escolher o sufixo `(ausente)` na listagem. Um repositório apagado aparece marcado e os seguintes continuam sendo impressos no mesmo laço. `test_caminho_cadastrado_que_sumiu_nao_impede_nada` e o `test_list_mostra_apelido_caminho_e_se_existe` cobrem o par vivo/morto.

**H11** — Não há estado de módulo: `carregar`, `texto_atual` e `resolver_cadastrado` fazem `read_text` a cada chamada, e `caminho_do_cadastro` recalcula a casa em vez de guardá-la. Não existe cache, memoização ou variável global no diff. `test_o_cadastro_e_relido_a_cada_chamada` reescreve o arquivo entre duas leituras e vê o valor novo; `test_cadastro_ausente_devolve_lista_vazia` cobre a ausência.
