# Veredito — prototipar-frontend-preview

Base: `e02879c..HEAD` mais o trabalho não commitado.

Nota de método: `git diff e02879c` **não** mostra `prototipar-frontend/preview/` — a pasta está
não rastreada (`?? prototipar-frontend/preview/` em `git status --porcelain`). Os arquivos foram
lidos direto do disco. O diff versionado cobre `README.md`, `prototipar-frontend/SKILL.md` e os
dois arquivos de teste; nenhum dos dois instaladores aparece alterado em relação a `e02879c`.

Resultado: **15 atendidos, 0 não atendidos, 0 não verificáveis.**

## Miolo

- **V1 — atendido.** `prototipar-frontend/SKILL.md:67` abre "A escada: como a tela sobe" com os
  três degraus numerados e nessa ordem: (1) o jeito que o alvo já roda o frontend dele, (2) o
  preview em docker, (3) degradação declarada. A escada é nomeada como escada, não apenas
  descrita.

- **V2 — atendido.** `SKILL.md:69`: "**Mostrar arquivo em disco para o humano abrir é recusado.**
  […] Você entrega **uma URL**." A recusa está em texto, com a razão junto, e não só como item de
  checklist.

- **V3 — atendido.** `SKILL.md:77`: "**O degrau 3 não bloqueia.** Sem docker e sem jeito do alvo,
  você **não para**: registra no resíduo que a tela não foi servida […] e segue até a entrega."
  Cobre a ausência de docker e a dos dois primeiros degraus, e amarra o registro ao resíduo.
  Reforçado em `preview/README.md:21-23` ("Sem docker — Não bloqueia").

- **V4 — atendido.** `SKILL.md:81`: "**Capture a tela e olhe a imagem antes de mostrá-la ao
  humano.** Depois conserte o que estiver visivelmente quebrado — tela branca, layout desmontado,
  estado que não renderiza." As três exigências do critério estão presentes: capturar, ler como
  imagem, consertar.

- **V5 — atendido.** `SKILL.md:85`: "**Essa conferência não consome rodada.** O teto de três conta
  reação humana; olhar a própria tela é trabalho seu, e você repete quantas vezes precisar antes
  de mostrar." Afirma as duas metades: não consome, e o teto continua contando só reação humana.

- **V6 — atendido.** `SKILL.md:87`: "Não existe ferramenta obrigatória aqui. […] o que se cobra é
  a **evidência de que a tela foi vista**, não o instrumento que a produziu." Nenhuma ferramenta
  de captura é nomeada em lugar nenhum do arquivo — nem como exemplo, nem como padrão.

- **V7 — atendido.** O template do resíduo ganhou a seção `## Como a tela subiu` (`SKILL.md:115`),
  pedindo o degrau (com o comando, quando for o jeito do alvo) e se a tela foi vista — "capturada
  e conferida, ou não, e por quê". Cobre as duas coisas que o critério exige registrar.

- **V8 — atendido.** Dois itens novos no checklist "Antes de entregar" (`SKILL.md:149-150`): "A
  tela subiu por URL, e o resíduo diz por qual degrau — ou por que não subiu" e "A tela foi
  capturada e conferida antes de ser mostrada."

- **V9 — atendido.** `SKILL.md:65`: "O preview **serve o que já está pronto; ele não escolhe a
  stack do alvo.** Essa escolha continua sendo da codebase que você leu na ancoragem". O vínculo
  com a ancoragem é explícito, como o critério pede. Repetido no cabeçalho do
  `preview/compose.yml:1-5`.

- **V15 — atendido.** Seção própria em `SKILL.md:59`, "Servível sem build, desde a primeira
  linha": "**O protótipo nasce abrível direto.** HTML que carrega o próprio CSS e o próprio JS,
  sem passo de compilação entre escrever e ver." E `SKILL.md:63` fecha a metade temporal do
  critério: "é insumo de construção, e por isso vem antes da escada e não depois. Saber que a tela
  vai subir sem build determina o que você escreve na primeira linha." A seção está de fato
  posicionada antes da escada no arquivo (59 vs. 67), como o plano previa.

## Plataforma

- **V10 — atendido.** `prototipar-frontend/preview/compose.yml` existe, com um serviço `preview`
  (`nginx:alpine`) publicando porta e montando `${SLE_PREVIEW_DIR:-./publico}` em
  `/usr/share/nginx/html:ro`. É diretório do host servido por HTTP.
  Observação factual, sem juízo de correção: o default `./publico` não existe no repositório — o
  uso documentado em `preview/README.md:6` e no cabeçalho do compose sempre passa
  `SLE_PREVIEW_DIR`.

- **V11 — atendido.** Não há `Dockerfile` na pasta, nenhum `build:`, `command:` ou `entrypoint` no
  compose, nenhuma instalação de dependência. Imagem pronta + volume montado. O cabeçalho do
  arquivo declara a razão (`compose.yml:1-5`) e `preview/README.md:17` repete: "Não compila, não
  instala dependência, não pressupõe framework."

- **V12 — atendido.** `compose.yml:15`: `"${SLE_PREVIEW_PORT:-8173}:80"`. Porta fixa em 8173,
  declarada em comentário adjacente, no README (`http://localhost:8173`) e na skill; a variável
  `SLE_PREVIEW_PORT` sobrescreve, com o caso de colisão documentado em `preview/README.md:9-13`.

- **V13 — atendido, verificado por execução.** Nenhum dos instaladores foi alterado em relação a
  `e02879c` — não há lista nova, como o contrato técnico exigia. Rodei os dois contra um destino
  descartável: `scripts/install.ps1` (via o teste real, que passou) e `scripts/install.sh`
  executado manualmente com `--components skills --scope local`. Em ambos,
  `.claude/skills/prototipar-frontend/preview/` chegou ao destino com `compose.yml` e `README.md`.
  A cópia recursiva já existente carrega o ativo.

- **V14 — atendido.** Um teste por instalador, ambos nomeados
  `test_instala_o_preview_junto_da_skill` e ambos afirmando `preview.is_dir()` e
  `(preview / "compose.yml").is_file()` no destino: `scripts/tests/test_install_ps1.py:93` e
  `scripts/tests/test_install_sh.py:76`.
  Sobre a execução nesta máquina: o teste do PowerShell passa; o do bash é pulado
  (`bash não disponível` — o pytest não encontra bash no PATH). Isso não torna o critério
  inverificável: o critério cobra a existência do teste por instalador, e o comportamento que ele
  afirma foi confirmado à mão, conforme V13.

## Item do plano sem critério

`README.md` ganhou a linha da árvore para `prototipar-frontend/preview/`. O plano já declarava que
não fecha critério; registrado apenas para constar que foi feito.
