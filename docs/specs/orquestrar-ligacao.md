# orquestrar-ligacao

## Intenção
O contrato de isolamento ganha ligação executável no harness, e a skill nova passa a ser instalada junto das outras.

## Depende de
`orquestrar`

## Critérios

- [ ] **G1** `integração` — Existe uma definição de agente por fase isolada — `codificar`, `verificar`, `homologar` — fora de `orquestrar/SKILL.md`.
- [ ] **G2** `integração` — Cada definição de agente recebe apenas os insumos que `orquestrar/SKILL.md` nomeia para aquela fase.
- [ ] **G3** `plataforma` — Nenhum arquivo versionado fora de `docs/specs/` cita "o roteador"; onde ele era quem encadeia, o texto nomeia `orquestrar`.
- [ ] **G6** `miolo` — `verificar/SKILL.md` atribui a `orquestrar` a leitura da classificação do veredito e a decisão do próximo passo.
- [ ] **G7** `miolo` — `especificar/SKILL.md` atribui a `orquestrar` a invocação de `codificar` depois do gate, e a leitura de "Depende de" como grafo.
- [ ] **G4** `plataforma` — Os dois instaladores copiam `orquestrar` junto das outras, cada um numa lista só.
- [ ] **G5** `plataforma` — A ajuda dos dois instaladores para de anunciar "5 skills" e anuncia o número correto.

## Contrato técnico

A ligação é **substituível sem tocar no contrato**: `orquestrar/SKILL.md` não pode nomear harness, e o guarda disso é critério da spec de que esta depende. Trocar de harness troca os arquivos de **G1** e nada mais.

"O roteador" era `tooling/loop/`, removido em `1cfcc86`. São **cinco** referências, em quatro arquivos: `metodologia-sle.md:16`, `codificar/SKILL.md:71`, `especificar/SKILL.md:11` e `:102`, `verificar/SKILL.md:83`. Todas apontam hoje para algo que não existe, e o orquestrador é quem assume o papel — **G3** não é limpeza oportunista.

**G6 e G7 existem porque duas dessas referências não são troca de nome.** `verificar/SKILL.md:83` descreve a tabela de roteamento por classificação do veredito, que é o **O8** de `orquestrar`; `especificar/SKILL.md:102` descreve a leitura de "Depende de" como grafo, que é condução de lote. Trocar só a palavra deixaria o texto correto e a responsabilidade órfã — por isso são critérios `miolo`, e não parte da varredura de `G3`.

`docs/specs/` fica fora de **G3**: specs e vereditos antigos são registro do que era verdade na época, e reescrevê-los é o que a decisão de `1cfcc86` recusou.

Os instaladores copiam a pasta inteira da skill (`cp -R` em `scripts/install.sh`, `Copy-Item -Recurse` em `scripts/install.ps1`), numa lista só que hoje tem cinco entradas — a contagem aparece em `install.sh:74` e `:123`, e em `install.ps1:95` e `:137`.

## Fora de escopo

- **Instalar as definições de agente no consumidor.** O orquestrador roda com o método, sobre N alvos; `.sle/manifesto.md:78` registra que não copiar esse tipo de componente para o consumidor é deliberado.
- **Teste que prove que o contexto não vazou.** Não é observável por instalação: quem detecta vazamento é a leitura limpa, depois, no veredito de cada demanda.

## Plano

1. **Definições de agente, uma por fase isolada** (G1, G2).
2. **`metodologia-sle.md`, `codificar/SKILL.md`, `especificar/SKILL.md`, `verificar/SKILL.md`** — a varredura das cinco referências (G3), e as duas que mudam de dono junto com o nome (G6, G7).
3. **`scripts/install.sh` e `scripts/install.ps1`** — a lista e a contagem na ajuda (G4, G5).

Não é fatiável por tamanho: sete critérios, e os dois de `integração` são o motivo dos de `plataforma` existirem.

## Perguntas em aberto

Vazio.
