# Veredito — sle-casa

Base: `docs/specs/sle-casa.md` contra `git diff 2b44536` (`casa.py`, `repos.py`, `driver.py` e os três arquivos de teste). Leitura de código, mais uma execução de `pytest tests/test_casa.py tests/test_repos.py tests/test_repo_cli.py`: 25 passaram, nenhuma falhou.

- **H1** — atendido
- **H2** — atendido
- **H3** — atendido
- **H4** — atendido
- **H5** — atendido
- **H6** — atendido
- **H7** — atendido
- **H8** — atendido
- **H9** — atendido
- **H10** — atendido
- **H11** — atendido

## Porquê

**H1** — `casa.caminho()` lê `SLE_CASA` e só cai para `Path.home() / ".sle"` quando a variável está ausente: a precedência é a ordem do próprio `if`. Os dois ramos têm teste (`test_a_casa_padrao_e_ponto_sle_no_home`, `test_a_variavel_de_ambiente_tem_precedencia`). Nota, não objeção: `SLE_CASA=""` cai para o padrão, porque a leitura testa verdade e não presença — o critério não fala do caso.

**H2** — `casa.garantir()` devolve `(destino, criada)`; o `mkdir(parents=True)` só acontece quando o destino não é `is_dir()`, e o segundo elemento diz se nasceu agora. Quem imprime é `_comando_repo`, e só quando `criada` é verdadeiro — o aviso sai uma vez, não a cada execução. A criação é disparada pelo `repo`, que é o comando que precisa escrever; `resolver_cadastrado` só lê e não cria casa, o que é coerente com "a primeira execução que precise dela". Coberto por `test_casa_ausente_e_criada_e_a_criacao_e_informada`, `test_casa_existente_nao_e_reportada_como_criada` e, no nível de CLI, `test_add_cria_a_casa_e_informa_uma_vez`, que compara a saída da primeira e da segunda invocação.

**H3** — Toda escrita do cadastro passa por `repos.gravar`, cujo destino é `casa.caminho() / "repos.md"`; não há no diff nenhum caminho de escrita derivado do alvo. No sentido inverso, o que o `sle` faz com o alvo por causa de cadastro é `repos.resolver_cadastrado`, que só lê. A separação é estrutural — duas origens de caminho distintas — e não uma checagem em runtime. `test_criar_a_casa_nao_toca_em_alvo_nenhum` compara a árvore do alvo antes e depois, e `test_nada_de_alvo_entra_na_casa` cadastra um alvo cheio de `docs/specs` e `.sle/loop.jsonl` e afirma que a casa contém exatamente `["repos.md"]` — o critério é falsificável nos dois sentidos e sobrevive.

**H4** — `_LINHA` reconhece `- <apelido>: <caminho>` e `ler` devolve os repositórios na ordem do arquivo, com o que não casa acumulado em `Leitura.invalidos`. A segunda metade do critério agora acontece de verdade: `_comando_repo` percorre `repos.leitura_atual().invalidos` antes de qualquer ação e imprime `linha ignorada, fora do formato ...: {linha}`, citando o texto da linha. `test_linha_fora_do_formato_e_nomeada_para_quem_usa` prova pela saída do CLI, não pela estrutura interna: roda `repo list` com um arquivo torto e exige a linha ruim na saída junto do cadastro válido. Limite honesto do escopo: a nomeação só ocorre no subcomando `repo`; `rodar --alvo <apelido>` resolve o apelido sem comentar linhas tortas. O critério está no bloco "O cadastro" e é sobre o arquivo, então considero atendido, mas é onde ele é mais estreito do que parece.

**H5** — `adicionar` não reescreve nada: concatena a linha nova ao texto recebido, normalizando apenas a ausência de `\n` final (`prefixo = texto if texto.endswith("\n") else texto + "\n"`), e `remover` reconstrói a partir das linhas originais. Ordem, comentários e linhas em branco — inclusive as do fim do arquivo — sobrevivem. `test_add_preserva_comentarios_ordem_e_linhas_em_branco` cobre o meio do arquivo e `test_add_preserva_ate_linha_em_branco_no_fim` fecha o falsificador de fim: `- api: /um\n\n\n` mais um `add` dá exatamente `original + "- site: /dois\n"`.

**H6** — `adicionar` monta o mapa `apelido -> caminho` do texto atual e levanta `ApelidoEmUso` com o caminho vigente na mensagem, antes de qualquer concatenação — nada é sobrescrito. `_comando_repo` captura, imprime e devolve 1. Provado nos dois níveis: `test_apelido_repetido_e_recusado_nomeando_o_caminho_atual` (mensagem) e `test_add_de_apelido_repetido_sai_nao_zero` (código de saída não-zero mais o caminho antigo na saída).

**H7** — O ramo `list` imprime `f"{repo.apelido}: {repo.caminho}{estado}"`, com `estado` vindo de `repos.existe`, que é `Path(...).is_dir()` avaliado na hora da listagem. Os três elementos exigidos estão na linha; a existência é comunicada por ausência de marca e a ausência por `(ausente)`. `test_list_mostra_apelido_caminho_e_se_existe` verifica apelido, caminho e a marca na linha certa.

**H8** — `remover` filtra pelo apelido casado em `_LINHA` e mantém intacta qualquer outra linha, inclusive comentários e brancos; quando nada saiu (`len(sobraram) == len(linhas)`) levanta `ApelidoDesconhecido` citando o apelido procurado, e o driver devolve não-zero. `test_rm_remove_so_aquela_linha` mostra que os dois comentários do arquivo continuam lá, e `test_rm_de_apelido_inexistente_e_recusado` mais `test_rm_remove_e_apelido_desconhecido_sai_nao_zero` cobrem a recusa no miolo e no CLI.

**H9** — `resolver` percorre o cadastro procurando apelido igual e, não achando, devolve `Path(valor)`: a precedência é a ordem do laço e do `return`. O caminho de produção está ligado — `Config(alvo=repos.resolver_cadastrado(args.alvo))` em `main`, com releitura do arquivo na hora. Os dois ramos têm teste unitário (`test_resolver_prefere_apelido_e_cai_para_caminho`) e de CLI (`test_alvo_aceita_apelido_cadastrado`, `test_alvo_desconhecido_e_tratado_como_caminho`), este último interceptando `driver.rodar` para ver o `Path` que chegou na `Config`.

**H10** — A existência do caminho não participa de nenhuma decisão de fluxo: `ler` não filtra por existência, `carregar` devolve tudo, e `existe` só é consultado para escolher o sufixo `(ausente)` na listagem. Um repositório apagado aparece marcado e os seguintes continuam sendo impressos no mesmo laço; `add` e `rm` também não consultam o disco do alvo. `test_caminho_cadastrado_que_sumiu_nao_impede_nada` cobre o par vivo/morto no miolo e `test_list_mostra_apelido_caminho_e_se_existe` no CLI.

**H11** — Não há estado de módulo: `carregar`, `texto_atual`, `leitura_atual` e `resolver_cadastrado` fazem `read_text` a cada chamada, e `caminho_do_cadastro` recalcula a casa em vez de guardá-la. Não existe cache, memoização nem variável global no diff, e o único artefato persistido é o próprio `repos.md`. `test_o_cadastro_e_relido_a_cada_chamada` reescreve o arquivo entre duas leituras e vê o valor novo; `test_cadastro_ausente_devolve_lista_vazia` cobre a ausência do arquivo.
