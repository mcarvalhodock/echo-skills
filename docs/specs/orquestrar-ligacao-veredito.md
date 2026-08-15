# Veredito — orquestrar-ligacao

Base: `git diff 003eebb -- .` (árvore de trabalho, não commitada).

- **G1** — atendido
- **G2** — não verificável
- **G3** — atendido
- **G6** — atendido
- **G7** — atendido
- **G4** — atendido
- **G5** — atendido

## Por quê

**G1** — O diff cria três arquivos novos, um por fase isolada, fora de `orquestrar/SKILL.md`: `.claude/agents/sle-codificar.md`, `.claude/agents/sle-verificar.md` e `.claude/agents/sle-homologar.md`. Cada um traz frontmatter com `name`, `description` e `tools`, e um corpo que manda invocar a skill homônima e declara a fronteira. Nenhuma definição foi colocada dentro da skill.

**G2** — As três definições declaram seus insumos de forma fechada — `codificar`: caminho da spec e alvo ("dois, e nenhum a mais"); `verificar`: spec, ref base do diff, escopo e alvo ("quatro"); `homologar`: specs do ciclo e vereditos, ref base do ciclo e alvo ("três"). Mas o critério exige comparação com a tabela de insumos por fase de `orquestrar/SKILL.md`, e essa tabela não aparece no diff — ela é texto anterior a `003eebb`, e os hunks de `orquestrar/SKILL.md` presentes tocam roteamento, lote, teto e checklist, não a tabela. Com o material desta verificação (spec + diff) não há como confrontar as duas listas, nem como saber se as definições incluem insumo que a tabela não nomeia. Por isso o critério não é decidível aqui — não é reprovação, é falta de evidência no recorte medido.

**G3** — O contrato técnico da spec enumera cinco referências, em quatro arquivos, e as cinco aparecem convertidas no diff: `metodologia-sle.md` ("Quem encadeia é o `orquestrar` — ou você, à mão"), `codificar/SKILL.md` ("é o `orquestrar` que a chama"), `especificar/SKILL.md` nos dois pontos (o parágrafo de abertura e o gabarito de "Depende de"), e `verificar/SKILL.md` ("quem lê a classificação e decide o próximo passo é o `orquestrar`"). Em todos, onde "o roteador" era quem encadeia, o texto agora nomeia `orquestrar`. A parte universal do critério — *nenhum* arquivo versionado fora de `docs/specs/` — está sustentada pela própria enumeração da spec, que fixa o conjunto em cinco; ocorrência fora dessa lista não seria visível num diff.

**G6** — `verificar/SKILL.md`, seção "Se o veredito aponta lacuna", passa a atribuir explicitamente a `orquestrar` as duas coisas que o critério pede: ler a classificação e decidir o próximo passo. A tabela fixa que segue (`não atendido` → `codificar` até o teto; `não verificável` → sobe para o humano) permanece descrita como do orquestrador, e o parágrafo mantém "A rota não é sua" — a responsabilidade mudou de dono junto com o nome, que era o motivo do critério ser `miolo`.

**G7** — `especificar/SKILL.md` cobre os dois membros do critério. A invocação depois do gate: "quem aprova é o humano, e quem invoca `codificar` depois é o `orquestrar`". A leitura como grafo: no gabarito da seção "Depende de", "O `orquestrar` lê esta seção como grafo, e a relação invertida vira ciclo — que trava o lote em vez de ordená-lo". A justificativa do ciclo travando o lote sobreviveu à troca, então a responsabilidade não ficou órfã.

**G4** — Os dois instaladores ganham `orquestrar` na lista única já existente, sem lista nova nem caminho especial: em `scripts/install.sh`, `local skills=(especificar codificar verificar homologar orquestrar prototipar-frontend)`; em `scripts/install.ps1`, o mesmo array `$skills` com `'orquestrar'` acrescentado (quebrado em duas linhas de código, mas um array só). Cada um segue passando pelo mesmo `copy_skill_folder` / `Copy-SkillFolder` do laço, ou seja, a cópia recursiva da pasta inteira descrita no contrato técnico. Os testes acompanham: `test_instala_o_orquestrador` em `scripts/tests/test_install_sh.py` e em `scripts/tests/test_install_ps1.py` exercitam a instalação real e checam `.claude/skills/orquestrar/SKILL.md`.

**G5** — As quatro ocorrências da contagem apontadas no contrato técnico foram atualizadas: em `install.sh`, o bloco `COMPONENTS` da ajuda ("Copy the 6 skills") e a opção 1 do modo interativo ("the 6 SLE skills"); em `install.ps1`, os dois equivalentes. O número novo é o correto — quatro do ciclo, mais `orquestrar`, mais `prototipar-frontend` — e bate com o tamanho da lista de G4. Os testes `test_ajuda_anuncia_a_contagem_certa_de_skills` dos dois arquivos passaram a negar `"5 skills"`, exigir `"6 skills"` e exigir a menção a `orquestrar` na ajuda.

## Observação de escopo

O diff também contém mudanças que não pertencem a esta spec: as seções novas de `orquestrar/SKILL.md` (lote, régua do que sobe, mapa problema→fase, teto e as quatro exceções), a linha de exceções de `metodologia-sle.md` e o arquivo `docs/specs/orquestrar-lote.md`. São os critérios `L*` da spec `orquestrar-lote`, medidos em outro veredito; não foram considerados aqui, e nada nelas contradiz os critérios `G*`.
