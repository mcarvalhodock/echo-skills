# plugin-cursor — veredito

Medido contra `1396c4f45aa89d96962d4ab0c67707dee76cb0a0` e o working tree atual, escopo `.`.
Evidência: `tests/test_cursor_plugin.py` (12 passed), `tooling/ci/tests/` (15 passed),
`git diff --name-status` contra o ref base, e leitura de `.cursor-plugin/plugin.json`,
`README.md`, `.sle/manifesto.md` e `docs/specs/plugin-cursor-manual-validation.md`.

- **M1** — atendido
- **M2** — atendido
- **M3** — atendido
- **M4** — atendido
- **M5** — atendido
- **M6** — atendido
- **M7** — atendido
- **M8** — atendido
- **M9** — atendido
- **M10** — atendido
- **M11** — atendido
- **M12** — atendido
- **M13** — atendido
- **M14** — não verificável
- **M15** — não verificável

## Por quê

**M1.** `.cursor-plugin/plugin.json` existe na raiz, é JSON válido, e declara
`"name": "sle"` — que casa `^[a-z0-9]+(?:-[a-z0-9]+)*$` e é o nome que o contrato
técnico pinou — e `"version": "3.0.0"`, não vazia.
`TestManifestoDoPlugin::test_declara_nome_kebab_case_e_versao` passa.

**M2.** `skills` é array de seis entradas: `./especificar/`, `./codificar/`,
`./verificar/`, `./homologar/`, `./orquestrar/`, `./prototipar-frontend/`. Todas
começam por `./` e nenhuma tem `..`, como o contrato exige. O teste não confia na
lista: resolve cada caminho e compara com o conjunto das pastas que de fato têm
`SKILL.md` no repositório — as duas coleções são iguais, então o manifesto aponta
para as seis pastas da raiz e para nenhuma outra.

**M3.** `agents` é `"./.claude/agents/"`, e resolve para o diretório
`.claude/agents/` do repositório. O critério cobra o campo apontando para lá, não
uma forma específica; o valor é string em vez de array, e o teste normaliza os
dois casos. Prefixo `./` presente, sem `..`.

**M4.** `git diff --name-status 1396c4f4` reporta cinco linhas, todas `M`
(`.sle/manifesto.md`, `README.md`, `tooling/ci/README.md`,
`tooling/ci/scripts/pr_spec_diff.py`, `tooling/ci/tests/test_pr_spec_diff.py`).
Nenhuma linha `R`. Nenhuma pasta de skill aparece no diff, nem como rename nem
como modificação.

**M5.** `git ls-tree -r --name-only 1396c4f4 .claude/agents/` lista três arquivos,
e a listagem do diretório no working tree é a mesma lista, path por path. Não é
só a contagem: os caminhos são idênticos.

**M6.** A varredura por `SKILL.md` em todo o repositório (excluídos `.git`,
`__pycache__`, `.pytest_cache`) acha exatamente seis arquivos, em seis diretórios
distintos, e nenhum deles está sob `.cursor-plugin/`. O pacote é um manifesto que
referencia a fonte, não um diretório que a copia — coerente com a fonte única do
contrato técnico.

**M7.** `git diff --exit-code 1396c4f4 --` sobre os seis `SKILL.md` mais os três
arquivos de `.claude/agents/` sai 0. Byte-idêntico ao ref base para os nove
arquivos.

**M8.** `git diff --exit-code 1396c4f4 -- scripts/install.ps1 scripts/install.sh`
sai 0, e nenhum dos dois aparece no `--name-status`. O instalador não mudou.

**M9.** `pytest scripts/tests` no working tree não produz nenhuma reprovação fora
de `scripts/tests/test_install_sh.py::` — que é justamente o conjunto que a spec
põe fora de escopo por defeito de ambiente já presente no ref base, e que
`pedidos.md` registra como pedido próprio. A asserção é de subconjunto, então
mede regressão: qualquer vermelho novo fora daquele arquivo reprovaria. Não há.

**M10.** `tooling/ci/tests/test_pr_spec_diff.py::TestManifestoDesteRepositorio`
lê o `.sle/manifesto.md` real — não um fixture — e afirma
`is_production_path(".cursor-plugin/plugin.json", patterns)`. Passa. Duas coisas
sustentam isso: `^\.cursor-plugin/` foi acrescentado a "Paths de produção" no
manifesto, e o `lstrip("./")` de `pr_spec_diff.py` foi trocado por `normalize()`
com `removeprefix("./")`. O `lstrip` removia qualquer caractere do conjunto
`{'.', '/'}` do início, então o path chegava aos padrões como
`cursor-plugin/plugin.json` e o padrão com ponto inicial nunca casava — o
critério reprovaria mesmo com o manifesto correto.

**M11.** A árvore da seção `## O que tem neste repo` do `README.md` ganhou a linha
`├── .cursor-plugin/plugin.json  # manifesto que faz o Cursor enxergar as skills daqui`.
A checagem é feita dentro da seção, não no arquivo todo.

**M12.** A seção `## Instalação` continua citando `install.sh` e `install.ps1`, e
o parágrafo novo diz literalmente "ao lado do instalador e não em vez dele",
fechando com "O Claude Code segue servido pelo instalador, que não muda". As duas
metades do critério — declarar o plugin e não desalojar o instalador — estão no
texto.

**M13.** `pytest tooling/ci/tests` sai verde: 15 passed, 0 failed. O critério fala
em 14 porque foi escrito antes do teste de M10, que o passo 3 do plano acrescenta
à mesma suíte; o 15º é aquele teste. Os 14 anteriores seguem passando, nenhum
regrediu, e `tooling/ci/README.md` foi atualizado de 14 para 15 para não deixar a
doc mentindo. Leio o critério como atendido: a contagem antiga era descrição do
estado de então, e a exigência é a suíte verde.

**M14.** Não verificável por mim. O critério pede o painel do Cursor desenhado
com as seis skills, e nenhuma asserção deste repositório vê esse painel — é por
isso que a spec o classifica como validação manual.
`docs/specs/plugin-cursor-manual-validation.md` existe, tem o marcador `spec:M14`
como `tooling/ci/` exige, documenta o carregamento por junção
(`~/.cursor/plugins/local/sle` → raiz do repositório, e não cópia, para não criar
a segunda cópia dos `SKILL.md`) e o critério de aprovação. Mas o próprio arquivo
declara **"Estado: pendente de observação humana"**: o carregamento foi feito, o
painel não foi visto. O que existe é o instrumento de medição, não a medição.

**M15.** Não verificável, pelo mesmo motivo de M14. Marcador `spec:M15` presente
no arquivo de validação manual, com as três definições de agente nomeadas
(`sle-codificar`, `sle-verificar`, `sle-homologar`) e o mesmo estado pendente de
observação humana.
