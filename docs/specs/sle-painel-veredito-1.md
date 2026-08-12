# sle-painel — veredito

Base: `docs/specs/sle-painel.md` contra `git diff 56fcc46`
(`tooling/loop/driver.py`, `tooling/loop/painel.py`, `tooling/loop/tests/test_painel.py`).

- **V1** — atendido
- **V2** — não verificável
- **V3** — atendido
- **V4** — atendido
- **V5** — atendido
- **V6** — atendido
- **V7** — atendido
- **V8** — atendido
- **V9** — atendido
- **V10** — atendido
- **V11** — atendido
- **V12** — não verificável

## Por quê

**V1** — `_comando_painel` itera `repos.carregar()` e imprime `painel.linha_de(repo.apelido, repo.caminho)`, uma linha por cadastrado. `test_o_painel_lista_todos_os_cadastrados` cadastra dois alvos em estados diferentes e confere que ambos aparecem, cada um com o rótulo do seu próprio estado — não só o nome.

**V2** — o subcomando aceita `--alvo` e o caminho feliz existe, mas a metade "ou caminho" não é exercida nem visível. A resolução é delegada a `repos.resolver_cadastrado`, que não está no diff, e `test_alvo_mostra_so_aquele` passa apenas um apelido (`"um"`). Nada no material lido diz se um caminho de disco é aceito. Some junto o fato de o rótulo impresso ser o próprio `args.alvo`: com um caminho, a linha viria rotulada pelo caminho inteiro em vez do apelido — mas isso também só se confirma exercitando a forma que ninguém exercitou.

**V3** — `_comando_painel` retorna `0` nos dois ramos, sem nenhum ramo condicionado ao estado derivado. `test_sai_com_zero_mesmo_com_travado` fixa isso com um alvo escalado por `FUSIVEL`.

**V4** — `estado_de` retorna `Estado("não começou", "sem registro de ciclo")` quando `registro.linhas` vem vazio, e o teste correspondente afirma tanto a presença de "não começou" quanto a ausência de "ocioso" e "pronto" — a distinção que o critério pede, e não apenas o rótulo. O alvo de teste é construído com `docs/specs/` já existente, então o ponto do contrato técnico (spec à mão não é ciclo iniciado) fica coberto de fato.

**V5** — `_ROTULO_POR_MOTIVO[Motivo.GATE_SPEC_APROVADA.value]` é `"aguarda você: aprovação do lote"`, aplicado quando a transição é `escalar`. Teste direto.

**V6** — mesmo mapa, `Motivo.GATE_CHECKLIST` → `"aguarda você: checklist de homologação"`, no ramo `escalar`. `test_pronto_nunca_e_afirmado` cobre por tabela o terminal `invocar:homologar`, que reusa o mesmo rótulo em vez de dizer "pronto" — consistente com o Fora de escopo.

**V7** — qualquer outro motivo cai no `return Estado("travado", f"{motivo} em ...")`, ou seja, o motivo entra no detalhe da linha, que é o que o critério exige ("a linha nomeia o motivo"). O teste usa `TETO_DE_TENTATIVAS` e afirma o rótulo e o motivo separadamente.

**V8** — o ramo final devolve `Estado("em andamento", f"{fase} em `{spec}`")`, com a fase extraída de `transicao.split(":")[-1]` e a spec vinda da linha. Teste confere rótulo, fase (`codificar`) e spec (`cobranca`) — os três elementos do critério.

**V9** — `estado_de` lê exclusivamente `registro.linhas(registro.caminho_do_registro(caminho))` do próprio alvo; não há leitura nem escrita de arquivo derivado, e o módulo não tem cache em memória entre chamadas (a releitura é feita a cada `estado_de`). `test_nao_ha_armazenamento_proprio_de_estado` fecha o outro lado: depois de rodar o painel, a casa contém só `repos.md`, o dado autorado.

**V10** — o ramo `painel` em `main` desvia antes de qualquer caminho de invocação, e `_comando_painel` só chama `repos.carregar`/`resolver_cadastrado`, `painel.linha_de` e `print`. Os dois testes atacam as duas metades: `monkeypatch` de `driver.invocar` para explodir se for chamado, e comparação de `mtime_ns` de todos os arquivos do alvo antes e depois — comparação de dicionários, então também pega arquivo criado ou removido, não só modificado.

**V11** — `estado_de` testa `caminho.is_dir()` antes de tudo e devolve `Estado("inacessível", ...)`, sem levantar; como isso vira um valor de retorno e não uma exceção, o laço de `_comando_painel` segue para os demais. `test_um_inacessivel_nao_impede_os_outros` confirma que o vivo e o morto aparecem na mesma saída, com saída `0`.

**V12** — o desenho sustenta o critério (nenhum lock, nenhuma escrita, releitura direta do arquivo), mas o teste que carrega o ID não cria concorrência: `test_o_painel_le_com_ciclo_em_andamento_sem_esperar` roda em processo único, com o registro parado, e apenas compara os bytes antes e depois — é a mesma garantia de V10 sob outro nome, não a de "com um ciclo em andamento noutro terminal". Fica sem verificar o que a concorrência real expõe: o comportamento de `registro.linhas` diante de uma última linha escrita pela metade enquanto o painel lê, e `registro.linhas` não está no diff.

## Observação sobre cobertura

`V2` e `V12` são justamente os dois cujos testes exercitam uma versão mais fácil do enunciado do que o enunciado: um apelido no lugar de "apelido ou caminho", uma leitura tranquila no lugar de "com um ciclo em andamento noutro terminal".
