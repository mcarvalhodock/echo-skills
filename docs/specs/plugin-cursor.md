# plugin-cursor

## Intenção
O Cursor passa a enxergar as skills que já existem neste repositório, por um manifesto que aponta para elas — um caminho ao lado do instalador, não em vez dele.

## Depende de
nenhuma.

## Critérios
- [ ] **M1** `integração` — Existe `.cursor-plugin/plugin.json` na raiz do repositório, com `name` em kebab-case e `version`.
- [ ] **M2** `integração` — O manifesto declara o campo `skills` apontando para as seis pastas de skill na raiz do repositório.
- [ ] **M3** `integração` — O manifesto declara o campo `agents` apontando para `.claude/agents/`.
- [ ] **M4** `plataforma` — Nenhuma pasta de skill mudou de lugar: `git diff --name-status` contra o ref base não reporta rename nenhum.
- [ ] **M5** `plataforma` — `.claude/agents/` continua com as três definições de agente, nos mesmos caminhos.
- [ ] **M6** `miolo` — Existe exatamente um `SKILL.md` por skill no repositório: o empacotamento não cria segunda cópia de nenhum.
- [ ] **M7** `miolo` — O texto das seis skills e das três definições de agente fica byte-idêntico ao do ref base.
- [ ] **M8** `plataforma` — `scripts/install.ps1` e `scripts/install.sh` ficam byte-idênticos ao do ref base.
- [ ] **M9** `plataforma` — Nenhum teste de `scripts/tests/` que passa no ref base passa a reprovar.
- [ ] **M10** `plataforma` — `pr_spec_diff` classifica como produção uma mudança em `.cursor-plugin/plugin.json`.
- [ ] **M11** `plataforma` — A árvore "O que tem neste repo" do `README.md` nomeia `.cursor-plugin/`.
- [ ] **M12** `plataforma` — A seção de instalação do `README.md` declara o plugin como caminho ao lado do instalador, e não em vez dele.
- [ ] **M13** `plataforma` — Os 14 testes de `tooling/ci/` passam.
- [ ] **M14** `integração` — Com o pacote carregado, o painel **Customize → Skills** do Cursor lista as seis skills (`especificar`, `codificar`, `verificar`, `homologar`, `orquestrar`, `prototipar-frontend`) vindas do plugin `sle`.
- [ ] **M15** `integração` — Com o pacote carregado, o painel **Customize → Agents** do Cursor lista as três definições de agente (`sle-codificar`, `sle-verificar`, `sle-homologar`) vindas do plugin `sle`.

## Contrato técnico
- **O ref base das comparações byte-idênticas é `1396c4f45aa89d96962d4ab0c67707dee76cb0a0`.**
- **Formato Cursor Plugin** (`.cursor-plugin/plugin.json`), não Agent Plugin: o pacote declara `agents`, e o padrão Agent Plugins carrega apenas skills e MCP.
- Todo caminho do manifesto é relativo e começa por `./`; sem `..`, sem absoluto.
- `name`: `sle`.
- **A doc do Cursor não descreve se os itens de `skills` em array são diretórios de skill ou raízes a varrer. M14 e M15 são a medição disso.** Se elas reprovarem, esse é o resultado da medição — **não é licença para mover as pastas**. Gerar o pacote por script é outra demanda, e a decisão é do humano.
- **Fonte única:** o pacote não contém cópia de nenhum `SKILL.md`; o que se edita continua sendo o arquivo do repositório. M6 cobra isso.
- **O instalador não muda.** O Claude Code continua sendo caminho de primeira classe, e o plugin é adicional. M8 cobra isso.
- M14 e M15 são validação manual: entram em `docs/specs/plugin-cursor-manual-validation.md` com o marcador `spec:<ID>`, como `tooling/ci/` exige.
- `tdd-aplicavel: ortodoxo`, por `.sle/manifesto.md`.

## Fora de escopo
- **Publicar no marketplace do time**, com Auto Refresh e modo de instalação — depende de plano e de admin, não é observável neste codebase, e é spec própria.
- **Confirmar que a camada `plugins` chega a um Cloud Agent** disparado por Slack ou GitHub — só é observável depois de publicado.
- **O link `../dominios.md` de `especificar/SKILL.md`, que fica pendurado depois de instalado em `~/.claude/skills/`** — dentro do repositório ele resolve, e o defeito é do instalador não copiar o catálogo. Demanda própria.
- **Completar "Paths de produção"** com `orquestrar/` e `prototipar-frontend/`, que já faltam hoje — lacuna anterior a esta demanda.
- **A sondagem de `bash` em `scripts/tests/_helpers.py`, e os 14 testes de `test_install_sh.py` que já reprovam no ref base.** É defeito de ambiente anterior a esta demanda, registrado como pedido próprio. **Não conserte aqui** — é por isso que M9 mede regressão em vez de verde absoluto.
- **Mover o layout ou gerar o pacote por script** — as duas alternativas foram recusadas no gate desta spec.
- **Qualquer mudança no método** — texto das skills, invariantes, catálogo de domínios. M7 cobra isso.

## Plano
1. Escrever `.cursor-plugin/plugin.json`, com `skills` apontando para as seis pastas da raiz e `agents` para `.claude/agents/`.
2. Acrescentar `^\.cursor-plugin/` a "Paths de produção" em `.sle/manifesto.md`.
3. Teste em `tooling/ci/tests/` cobrindo M10 — ele falha antes do passo 2 existir.
4. Atualizar a árvore e a seção de instalação do `README.md`.
5. Carregar em `~/.cursor/plugins/local`, e registrar M14 e M15 em `docs/specs/plugin-cursor-manual-validation.md`.

## Perguntas em aberto
nenhuma.
