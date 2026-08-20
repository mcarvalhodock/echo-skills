## Teste de spec

Faça um teste de especificação com critérios de aceite fake para testar a ferramenta utilitária.

## A5 regrediu: os 14 testes de `test_install_sh.py` reprovam no ref base

Em `1396c4f`, `python -m pytest scripts/tests` fecha 14 failed / 21 passed nesta máquina, e todas as falhas são de `test_install_sh.py`. Nenhuma linha de código mudou desde que o A5 de `docs/specs/instalador-alvo-e-remocao-do-loop.md` — "Todos os testes de `test_install_sh.py` passam" — fechou verde.

A causa é qual `bash` a máquina resolve. Quem responde é `C:\WINDOWS\system32\bash.EXE`, o atalho do WSL, e ele perde as barras invertidas do caminho do script:

```
/bin/bash: C:dock-codesecho-skillsscriptsinstall.sh: No such file or directory
```

A sondagem em `scripts/tests/_helpers.py` aceita esse candidato porque testa se o `bash` executa, não se ele recebe um caminho do Windows.

Duas coisas para a spec decidir, e nenhuma é obviamente certa: se a sondagem deve rejeitar candidato que não aceita caminho do sistema, ou se a suíte deve passar caminho que qualquer `bash` entenda. E vale a pergunta maior — um critério atestado verde que hoje está vermelho sem mudança de código diz que o veredito não alcança o ambiente em que ele foi medido.

Descoberto durante a spec `plugin-cursor`, que declarou isso fora de escopo de propósito.

## Versão limpa das skills: genéricas em vez de escritas para o Claude

**Prioridade declarada: antes da `plugin-cursor`.** Ela fica parada esperando esta.

O pedido é a versão limpa das skills — hoje elas carregam decisões do Claude Code na forma, e isso as quebra em outro harness. **O que "limpa" significa não está decidido**, e é o que `especificar` tem que extrair: as duas direções mencionadas foram (a) uma versão genérica que serve qualquer harness, ou (b) especializações por utilitário a partir de um núcleo comum.

### O que foi medido, e como

Três das seis skills **não carregam no Cursor**: `especificar`, `codificar` e `prototipar-frontend`. As outras três carregam.

A causa é `: ` — dois-pontos seguido de espaço — dentro da `description` da frontmatter, sem quotes. Em YAML, escalar simples não pode conter `: `, porque ali começaria um mapeamento; a frontmatter não parseia e a skill é descartada em silêncio, sem erro visível.

| skill | trecho | carrega? |
|---|---|---|
| `especificar` | "Termina no gate humano**: **não invoca" | não |
| `codificar` | "Entrega e para**: **não invoca" | não |
| `prototipar-frontend` | "só falta construir**: **aí a demanda" | não |
| `verificar`, `homologar`, `orquestrar` | nenhum `: ` (usam `;`) | sim |

**Provado por intervenção, não por correlação.** Numa cópia descartável fora do repositório, a `description` do `codificar` foi envolvida em quotes duplas e nada mais mudou: a listagem de skills do CLI passou de 17 para 18, com `codificar` presente. Instrumento: `cursor-agent -p --plugin-dir <dir>`, pedindo a lista em ordem alfabética com total, duas execuções concordantes antes da intervenção.

### O que isso revela sobre a distribuição

A cópia instalada em `~/.claude/skills/especificar/SKILL.md` está **com** quotes; a do repositório está **sem**:

```
INSTALADA: description: 'Use antes de escrever ou m
REPO_____: description: Use antes de escrever ou mo
```

O método funciona hoje por acidente de uma cópia velha no destino. O instalador pula o que já existe, a cópia boa ficou parada e a fonte derivou para um estado que não carrega — o risco que o README nomeia, agora com instância. Não se sabe o que o parser do Claude Code faz com a versão sem quotes, porque a que está instalada não é ela.

### Outros pontos de "escrito para o Claude", para `especificar` avaliar

- `disable-model-invocation: false` nas seis é **no-op**: é o default. Seis linhas que não fazem nada.
- `.claude/agents/*.md` usa `tools:` na frontmatter, que é campo do Claude Code. O Cursor documenta `readonly`, `model` e `is_background`. Mesma definição de agente não serve aos dois sem decisão sobre qual forma é a canônica.
- `allowed-tools` e `model`, se aparecerem, não são campos documentados de skill no Cursor.
- O link `../dominios.md` de `especificar/SKILL.md` (ver pedido próprio acima) é do mesmo tipo: caminho que só resolve num layout de destino específico.

### Decisão que não é derivável

Se a forma canônica passa a ser a genérica, alguém perde: uma frontmatter que serve os dois harnesses provavelmente não usa o melhor de nenhum. Trocar expressividade por portabilidade é apetite, não dedução — e por isso sobe para o gate em vez de ser resolvido na spec.

## A disciplina em multi-repo: análise de impacto de uma funcionalidade

O pedido original, que originou os outros três. Dada uma funcionalidade nova: **quais repositórios ela afeta, o que precisa mudar em cada um, e como** — e depois a implementação coordenada entre eles.

### A pergunta que decide o desenho, e que é do método

O SLE tem **um** `alvo`, e `especificar/SKILL.md` fixa que `docs/specs/` e `.sle/manifesto.md` são relativos a ele. Uma demanda que atravessa cinco repositórios não tem um alvo — e daí saem perguntas que nenhuma ferramenta responde:

- Onde mora a spec? Num repositório eleito, num repositório de coordenação, ou uma por repo?
- Qual `.sle/manifesto.md` governa, se cada repo declara domínios ativos e ferramental próprios?
- O que `verificar` roda, se "a suíte que a demanda toca" está em cinco lugares?
- O veredito é um ou cinco? Uma demanda "parcialmente verde" em três repos fechou?
- O teto de 15 critérios vale para a demanda inteira ou por repo? Se for inteira, cinco repos couberam em 15 critérios — o que provavelmente significa que a demanda é grande demais e a divisão é por repo.

Note que a regra de fatiabilidade já existente talvez responda parte disso: fatia é entregável separadamente quando fecha sozinha. Repo pode ser um eixo de fatia natural — mas só quando as mudanças não são interdependentes, e o caso interessante de multi-repo é justamente quando elas são.

### O que o mecanismo permite (pesquisado em 2026-08-20, verificar antes de usar)

- **Ambiente multi-repo de Cloud Agent é suportado.** Vários repositórios num ambiente; o agente inspeciona o workspace inteiro, faz mudanças coordenadas e abre PR nos repos que alterou. Ressalva documentada: *long-running* não está disponível para multi-repo, sem definir o que isso desabilita. [docs](https://cursor.com/docs/cloud-agent)
- **API:** `POST /v1/agents` aceita `repos` com **até 20** repositórios, cada um com `startingRef` ou `prUrl`. `repos` e ambiente nomeado são mutuamente exclusivos. O resultado volta como `git.branches[]`, uma entrada por branch/PR. [docs](https://cursor.com/docs/cloud-agent/api/endpoints)
- **Resolução de ambiente**, primeiro que casa: `.cursor/environment.json` do repo → ambiente pessoal salvo → ambiente do time.
- **Multi-root workspace local indexa todos os repos**, mas **Cloud Agents não aceitam multi-root** — a análise local e a execução na nuvem se configuram separado. E worktrees ficam desabilitados em multi-root, o que remove a principal isolação local exatamente quando se trabalha entre repos.
- **Plan mode** é o encaixe natural da análise: pesquisa, pergunta o que falta, produz plano revisável antes de código, e "Save to workspace" o transforma em artefato commitável. Mas plano é um markdown único, sem noção de repositório.
- **Segredos podem ser escopados por ambiente**, o que cobre o caso multi-repo.
- **`repositoryDependencies`** existe no schema publicado de `environment.json` ("repos necessários, incluídos no token de acesso gerado") e **não** aparece na prosa da doc. É o gancho para clonar repos irmãos com um token que os alcança — verificar antes de depender.
- **Submódulos** recebem só um aviso de permissão na doc, e nada além.
- **Não há exemplo documentado** de fan-out de uma mudança por N repositórios em CI. Matrix com `CURSOR_API_KEY` de organização é natural, mas seria construção própria.

### Depende de

Da versão limpa das skills e da `plugin-cursor`, nesta ordem: nada disto alcança agente na nuvem enquanto as skills só existirem em `~/.claude/skills`, e três das seis não parseiam.

## O ciclo disparado por pessoa, com solicitante e aprovador separados

O gatilho sai da sessão que especificou e passa para a pessoa. Forma pretendida:

```
solicitante (outro time) registra o pedido
        ↓
especificar, em ambiente multi-repo — análise de impacto entre repositórios
        ↓ dúvidas vão e voltam COM O SOLICITANTE
spec fechada
        ↓ ┤aprova ou reprova: o DONO, que não é o solicitante├
orquestrar (topo)
        ↓
(codificar → verificar) × N
        ↓
        ┤homologar: checklist├
```

**A pergunta que isto abre é do método, não da ferramenta.** `especificar/SKILL.md` diz "sobe para o humano", no singular, e a régua dele manda subir preferência, prioridade e apetite de risco. Com solicitante ≠ aprovador, as duas metades da régua endereçam pessoas diferentes: o que o pedido quer é do solicitante; prioridade e apetite de risco são do dono que aprova. Endereçar ao interlocutor errado produz spec aprovada contra a intenção de quem não foi consultado — e nenhum veredito posterior detecta isso, porque o código atende o critério escrito.

Decidir: o `especificar` passa a nomear o destinatário de cada pergunta em aberto, ou passa a ter duas seções de perguntas? E "o humano" do gate deixa de ser um papel só?

Restrições que já se sabem do mecanismo, se for por Cloud Agents:

- **A ida e volta com o solicitante** é o caso de uso de `subscriptions`: o agente responde na thread do Slack ou no comentário da issue, encerra o turno e acorda quando a pessoa responde, por até 180 dias.
- **A aprovação por quem é dono** não deve ser label — qualquer um adiciona. A spec é arquivo, então é review obrigatório de PR com CODEOWNERS por caminho. É o mecanismo que o item 4 de `propostas/expansao-para-times.md` (aprovador nomeado por domínio) pedia sem nomear.
- **A análise de impacto multi-repo** é ambiente multi-repo de Cloud Agent: até 20 repositórios num run, PR aberto em cada repo alterado. Long-running não está disponível para multi-repo.
- **`orquestrar` tem de ser o topo do run.** Subagente aninha um nível só; com ele como subagente, a leitura limpa do `verificar` cairia no terceiro nível e não seria criada — o que mataria a segunda invariante pelo mecanismo.

Isto torna concretos os itens 2 (ID rastreável) e 4 (aprovador nomeado) de `propostas/expansao-para-times.md`, que seguiam como hipótese. O pré-requisito de tooling é a spec `plugin-cursor`, porque nada disso alcança agente na nuvem enquanto as skills só existirem em `~/.claude/skills`.

## `plugin-cursor` está parada, e por quê

**Estado:** treze dos quinze critérios atendidos, veredito em `docs/specs/plugin-cursor-veredito.md`, implementação inteira no working tree **sem commit**, ref base `1396c4f`. Nenhum critério voltou para `codificar`; o teto de tentativas está intacto.

**O que a demanda provou, e vale guardar:** o campo `skills` em array **funciona**. O Cursor lê o manifesto e expõe as pastas de skill apontadas por ele, sem mover nada e sem segunda cópia dos `SKILL.md`. Era a incerteza que o contrato técnico mandava medir, e ela caiu do lado que preserva a fonte única.

**M14 e M15 são defeito de spec.** Eles fixaram o mecanismo de carga na letra do critério — "carregado de `~/.cursor/plugins/local`" — e esse diretório **não é varrido** nesta instalação: `userLocal=false` em toda carga do log de plugins, inclusive horas antes de o pacote existir, e sem `--plugin-dir` nenhuma skill do SLE aparece. Nenhuma implementação atende um critério assim.

Reescrever medindo **efeito** em vez de mecanismo: o pacote expõe as seis skills quando carregado, com o instrumento (`--plugin-dir`, marketplace, ou o que existir) como detalhe do plano e não do critério. É a lição geral — critério que nomeia o instrumento envelhece junto com ele.

**E ela depende da versão limpa das skills:** enquanto três das seis não parseiam, "expõe as seis" é inalcançável por motivo que não é do pacote.

Resíduo no ambiente: a junção `~/.cursor/plugins/local/sle` → raiz do repositório continua montada. Inofensiva, já que a fonte não é varrida.