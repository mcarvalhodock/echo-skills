# prototipar-frontend-preview

## Intenção
A tela que `prototipar-frontend` produz passa a ser vista antes de ser discutida: sobe do jeito do próprio alvo, cai num preview em docker quando o alvo não serve, e o agente olha a captura antes de mostrar — em vez de entregar arquivos que ninguém abriu.

## Depende de
`prototipar-frontend` (fechada). Esta spec emenda a skill que aquela criou.

## Critérios

- [ ] **V1** `miolo` — `prototipar-frontend/SKILL.md` fixa uma escada de precedência nomeada e nessa ordem: (1) o jeito que o alvo já roda o frontend dele, (2) o preview em docker, (3) degradação declarada.
- [ ] **V2** `miolo` — A skill exige que a tela esteja servida e alcançável por URL antes de ser mostrada ao humano; entregar arquivo em disco para o humano abrir é recusado em texto.
- [ ] **V3** `miolo` — A skill declara que a ausência de docker **não bloqueia**: sem os dois primeiros degraus, ela registra o fato e segue até o resíduo.
- [ ] **V4** `miolo` — A skill exige que o agente capture a tela e a leia como imagem antes de mostrá-la, e conserte o que estiver visivelmente quebrado.
- [ ] **V5** `miolo` — A skill afirma que essa conferência do agente não consome rodada de reação; o teto de três rodadas continua contando só reação humana.
- [ ] **V6** `miolo` — A skill não nomeia nenhuma ferramenta de captura como obrigatória: o que ela exige é a evidência registrada, não o instrumento.
- [ ] **V7** `miolo` — O template do resíduo ganha o registro de como a tela foi servida (qual degrau) e se ela foi vista.
- [ ] **V8** `miolo` — O checklist "Antes de entregar" cobra a tela servida e a captura conferida.
- [ ] **V9** `miolo` — A skill afirma que o preview em docker não escolhe a stack do alvo: ele serve o que já está pronto, e a stack continua sendo decisão da codebase lida na ancoragem.
- [ ] **V10** `plataforma` — Existe `prototipar-frontend/preview/` com um `compose.yml` que serve, por HTTP, um diretório montado do host.
- [ ] **V11** `plataforma` — O preview é agnóstico de stack: não compila, não instala dependência, não pressupõe framework — serve arquivo estático e nada mais.
- [ ] **V12** `plataforma` — A porta do preview é fixa e declarada, com uma variável de ambiente que a sobrescreve quando colide.
- [ ] **V13** `plataforma` — Instalar a skill leva `preview/` junto para o destino, nos dois instaladores, sem lista nova.
- [ ] **V14** `plataforma` — Há teste por instalador verificando `preview/compose.yml` no destino.
- [ ] **V15** `miolo` — A skill diz que o protótipo nasce servível sem passo de build — abrível direto —, e que isso vale desde a primeira linha, não como conversão no fim.

## Contrato técnico

O preview **serve estático e guia a construção — não é a construção**. Ele não compila; mas o fato de que ele não compila é insumo para o agente, e é o que **V15** carrega: saber que a tela vai subir sem build determina o que se escreve desde a primeira linha. Sem esse degrau declarado, o agente constrói às cegas e descobre no fim que o que fez não abre.

Qualquer passo de build ou instalação de dependência dentro do preview seria escolher a stack do alvo — exatamente o que `prototipar-frontend.md` pôs fora de escopo. A reabertura aqui é deliberada e parcial: **servir** entra nesta spec, **construir** continua fora nas duas.

Os instaladores **não ganham lista nova**: `cp -R` (`scripts/install.sh:336`) e `Copy-Item -Recurse` (`scripts/install.ps1:300`) já copiam a pasta inteira da skill. **V13** é o guarda de que isso continue verdade, não um pedido de código novo.

Porta: `8173`, sobrescrita por `SLE_PREVIEW_PORT`. Fixa porque o resíduo cita a URL, e variável porque o alvo pode já estar ocupando a porta.

**V6** existe porque a captura depende do harness — Claude Code, Cursor e o próximo não oferecem a mesma ferramenta. Amarrar uma delas no texto quebraria a skill onde ela não existe; o critério cobra o registro da evidência, que qualquer harness consegue produzir.

## Fora de escopo

- **Regressão visual, diff de pixel, baseline de screenshot.** Prender a aparência é o oposto de um artefato descartável — e a skill proíbe teste por isso.
- **Rodar o preview em CI.** Ninguém reage a uma tela em pipeline; a reação é humana e síncrona.
- **Substituir o dev server do alvo.** O degrau 1 existe justamente para não competir com ele.
- **As outras áreas** (jogos, dev-ops, backend). O contrato comum só se prova depois desta rodar.
- **Instalar docker.** Se não tem, degrada — é o que **V3** garante.

## Plano

1. **`prototipar-frontend/preview/compose.yml`** e um `README.md` curto ao lado — o serviço estático, a porta e a variável (V10, V11, V12).
2. **`scripts/tests/test_install_sh.py` e `scripts/tests/test_install_ps1.py`** — um teste por instalador para o ativo no destino (V13, V14).
3. **`prototipar-frontend/SKILL.md`** — a forma servível (V15) antes da escada, porque ela é o insumo de construção; depois a escada e a URL (V1, V2, V3, V9), a conferência do agente (V4, V5, V6), o resíduo e o checklist (V7, V8).
4. **`README.md`** — a árvore ganha `preview/`. Fechamento: não fecha critério.

**Fatiável em duas, nesta ordem:**

- **Fatia A — `plataforma`** (V10–V14): o ativo e sua instalação. Fecha sozinha; nenhum critério dela depende do texto da skill.
- **Fatia B — `miolo`** (V1–V9, V15): o texto da skill. Vem depois porque aponta para `preview/` — texto que referencia ativo inexistente é ponteiro quebrado, não emenda.

## Perguntas em aberto

Vazio.
