# prototipar-frontend

## Intenção
Quem tem uma demanda de frontend cujo caminho ainda não está decidido ganha uma skill que produz tela reagível ancorada na codebase, e devolve como insumo o que sobreviveu à reação — em vez de escrever spec sobre hipótese não testada.

## Depende de
Nenhuma. É a primeira skill acessória; o contrato que ela materializa vale para as próximas áreas (jogos, dev-ops, backend), mas nenhuma delas precede esta.

## Critérios

- [ ] **P1** `miolo` — Existe `prototipar-frontend/SKILL.md` com frontmatter no mesmo formato das quatro do ciclo: `name`, `description` e `disable-model-invocation: false`.
- [ ] **P2** `miolo` — A `description` do frontmatter contém uma cláusula de recusa iniciada por "NÃO use", como as quatro do ciclo têm.
- [ ] **P3** `miolo` — O corpo da skill afirma que ela roda antes de `especificar` e que não é fase do ciclo.
- [ ] **P4** `miolo` — A skill manda ler a codebase antes de propor qualquer coisa, e produzir uma ancoragem que nomeia arquivos ou componentes existentes.
- [ ] **P5** `miolo` — A skill exige que a ancoragem declare ao menos um padrão herdado e ao menos uma contradição — ou afirme, em texto, que não há contradição.
- [ ] **P6** `experiência` — A skill define o artefato como tela navegável e enumera os estados que ela precisa mostrar; prosa descritiva é recusada em texto explícito.
- [ ] **P7** `miolo` — A skill afirma que descartar o protótipo é resultado bem-sucedido, não desperdício.
- [ ] **P8** `miolo` — A skill fixa um teto de esforço numérico e diz o que fazer quando ele estoura.
- [ ] **P9** `miolo` — A skill define o formato do resíduo, e o resíduo preenche o insumo "o pedido" que `especificar/SKILL.md` exige na seção Insumos.
- [ ] **P10** `miolo` — O formato do resíduo separa o que sobreviveu à reação do que foi descartado, e nomeia o descartado.
- [ ] **P11** `miolo` — A skill proíbe, em texto, três coisas: escrever teste, commitar como produção e invocar `codificar`.
- [ ] **P12** `miolo` — A skill declara que frontend é disciplina de prática e não domínio, e que ela consome `dominios.md` sem entrar nele.
- [ ] **P13** `miolo` — A tabela "Os domínios" de `dominios.md` continua com as mesmas seis linhas depois desta demanda.
- [ ] **P14** `plataforma` — `scripts/install.sh` e `scripts/install.ps1` copiam `prototipar-frontend` junto das outras, cada um numa lista só.
- [ ] **P15** `plataforma` — A ajuda dos dois instaladores para de anunciar "4 skills" e passa a anunciar o número correto.

## Contrato técnico

O teto de **P8** é contado em rodadas de reação, não em tempo de relógio: o método não mede relógio em nenhuma outra skill, e introduzir isso aqui criaria uma unidade que nada mais no repositório sabe ler.

O resíduo de **P9** é arquivo, não conversa: `especificar` roda em sessão limpa (`especificar/SKILL.md`, seção Insumos) e nada da sessão do protótipo chega lá.

A skill não ganha entrada em `dominios.md` — **P13** é o guarda disso, e existe porque a regra de crescimento do catálogo (`dominios.md:9`) só admite domínio novo quando nasce especialista novo.

## Fora de escopo

- **Framework de protótipo, servidor de preview, ferramenta de build.** A skill descreve o que produzir; com que stack, quem decide é a codebase do alvo — que a skill acabou de ler.
- **As outras três áreas** (jogos, dev-ops, backend). O contrato comum só se prova depois que uma área rodar de verdade; escrever as quatro agora é escrever três sobre suposição.
- **Automação do handoff resíduo→`especificar`.** O humano leva o arquivo; um roteador para acessórios pressupõe que o formato do resíduo já estabilizou, e ele nasce nesta demanda.
- **Emenda ao `especificar`.** Ele fica intacto — a decisão foi dele continuar como está.

## Plano

1. **`prototipar-frontend/SKILL.md`** — frontmatter (P1, P2), depois o corpo na ordem: posição fora do ciclo (P3), ancoragem (P4, P5), artefato e estados (P6), descarte e teto (P7, P8), resíduo (P9, P10), proibições (P11), fronteira com `experiência` (P12).
2. **`scripts/install.sh` e `scripts/install.ps1`** — a lista de skills e os textos de ajuda que citam a contagem (P14, P15). Duas listas, uma por arquivo; a contagem aparece também no bloco de `--components`.
3. **`README.md`** — a seção "O que tem neste repo" ganha a skill acessória, marcada como fora do ciclo. Passo de fechamento: não fecha critério, mas sem ele a skill existe e ninguém descobre.

Não é fatiável: onze dos quinze critérios são `miolo` e caem no mesmo arquivo. Os dois de `plataforma` (P14, P15) separariam limpo, mas instalar uma skill que ainda não existe não é entregável — e uma fatia de dois critérios que só fecha depois da outra é a mesma spec com o trabalho espalhado.

**Proposta a confirmar no gate:** teto de **três rodadas de reação**. Na quarta, a skill para e devolve o resíduo com o que tiver. Três é o menor número que permite a sequência "propõe → você corrige → confirma"; o número é preferência sua, e é a única coisa aqui que não saiu do repositório.

## Perguntas em aberto

Vazio.
