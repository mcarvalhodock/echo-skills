# prototipar-frontend — veredito

Base: `git diff d218dce` (trabalho não commitado) contra `docs/specs/prototipar-frontend.md`.
Escopo de leitura limitado à spec e ao diff — critérios que dependem de arquivos fora do diff estão marcados como não verificáveis.

| # | Veredito |
|---|---|
| P1 | atendido (com ressalva) |
| P2 | atendido |
| P3 | atendido |
| P4 | atendido |
| P5 | atendido |
| P6 | atendido |
| P7 | atendido |
| P8 | atendido |
| P9 | parcial — formato atendido, correspondência não verificável |
| P10 | atendido |
| P11 | atendido |
| P12 | atendido |
| P13 | atendido |
| P14 | atendido |
| P15 | atendido |

---

**P1 — frontmatter no mesmo formato das quatro** — **atendido, com ressalva de verificabilidade.**
`prototipar-frontend/SKILL.md` nasce com os três campos que o critério enumera: `name: prototipar-frontend`, `description: ...`, `disable-model-invocation: false`. A cláusula "no mesmo formato das quatro do ciclo" não é verificável aqui: os frontmatters de `especificar`, `codificar`, `verificar` e `homologar` não aparecem no diff e a leitura foi restrita. O que o critério enumera explicitamente está presente e bem formado.

**P2 — cláusula de recusa "NÃO use"** — **atendido.**
A `description` termina com: "NÃO use quando o caminho já está decidido e só falta construir: aí a demanda vai direto para `especificar`." Recusa iniciada por "NÃO use", com destino alternativo nomeado.

**P3 — roda antes de `especificar`, não é fase do ciclo** — **atendido.**
Seção "Você está fora do ciclo": nomeia o ciclo completo, afirma em negrito "Esta skill não é fase dele" e "Ela roda **antes** do `especificar`, e o que ela entrega é insumo, não etapa". As duas afirmações que o critério pede estão literais.

**P4 — ler a codebase antes de propor; ancoragem nomeando arquivos/componentes** — **atendido.**
Seção "Ancoragem: leia antes de propor" abre com "**Não desenhe nada antes de ler o alvo.**" e manda escrever a ancoragem "antes da primeira tela". O template exige "Parte de: [arquivos ou componentes existentes, pelo caminho]", reforçado por "Nomeie caminhos. 'Segue o padrão do projeto' não é ancoragem; é elogio." O checklist final repete a exigência.

**P5 — ao menos um padrão herdado e ao menos uma contradição, ou "nada" em texto** — **atendido.**
Template: "Herda: [ao menos um padrão que o protótipo repete de propósito]" e "Contradiz: [ao menos uma coisa que ele quebra, e por quê — ou 'nada']". O texto seguinte fecha a saída de escape: "As três linhas são obrigatórias... Se for esse o caso, escreva 'nada' e siga — mas escreva".

**P6 — tela navegável, estados enumerados, prosa recusada em texto explícito** — **atendido.**
Seção "O artefato é tela, não texto": recusa explícita em negrito ("**Descrição em prosa é recusada aqui.**"); navegabilidade definida operacionalmente ("o que parece clicável, clica... tela morta não"); estados enumerados em lista — vazio, carregando, erro, cheio, mais o estado que a demanda inventa.

**P7 — descartar é sucesso** — **atendido.**
Seção "Descartar é o resultado bom": "**Jogar o protótipo fora é sucesso, não desperdício.**" — literalmente a formulação do critério, com a justificativa de custo em seguida.

**P8 — teto numérico e o que fazer quando estoura** — **atendido.**
"O teto é **três rodadas de reação**", com a rodada definida ("você mostra, o humano reage, você ajusta"). O que fazer no estouro está dito: "Na quarta, **pare e entregue o resíduo com o que tiver**, mesmo insatisfeito", mais "Não peça permissão para estourá-lo; entregue." Consistente com o Contrato técnico, que exige contagem em rodadas e não em relógio — não há nenhuma unidade de tempo no arquivo.

**P9 — formato do resíduo definido, e resíduo preenche o insumo "o pedido" de `especificar`** — **parcialmente atendido.**
A primeira metade está atendida: seção "O resíduo" fixa caminho (`<alvo>/docs/prototipos/<nome>-residuo.md`), forma (arquivo, não conversa — alinhado ao Contrato técnico) e um template markdown com quatro seções.
A segunda metade é **não verificável** sob a restrição de leitura: a skill *afirma* que "**O resíduo é o insumo 'o pedido'** que ele exige", mas confirmar que `especificar/SKILL.md` de fato nomeia um insumo chamado "o pedido" na seção Insumos exigiria ler aquele arquivo, que não está no diff. A afirmação é declarada, não demonstrada.

**P10 — separa sobreviveu de descartado e nomeia o descartado** — **atendido.**
O template tem as seções distintas "## O que sobreviveu" e "## O que foi descartado", esta última instruindo "nomeado, com o motivo em meia linha", e o texto seguinte a torna obrigatória: "**'O que foi descartado' não é opcional.**" A instrução de fatos ("a busca é incremental, sem botão", não "a busca ficou boa") reforça a nomeação.

**P11 — proíbe teste, commit como produção e invocar `codificar`** — **atendido.**
Seção "O que você não faz", três itens, um por proibição: "**Não escreve teste.**", "**Não commita como produção.**", "**Não invoca `codificar`.**" As três aparecem também no fechamento (checklist e "Entregue o resíduo e **pare**").

**P12 — frontend é disciplina, não domínio; consome `dominios.md` sem entrar nele** — **atendido.**
Seção "Frontend é disciplina, não domínio": "O catálogo endereça *especialista*...; esta skill endereça *prática*", com a proibição direta "não acrescente `frontend` a ele". O consumo está descrito: "A relação certa é de consumo: o domínio `experiência` te diz o que a interface precisa sustentar... Quem marca domínio é o `especificar`, depois, sobre o resíduo."

**P13 — a tabela "Os domínios" continua com as mesmas seis linhas** — **atendido.**
`.sle/dominios.md` (ou qualquer arquivo `dominios.md`) não aparece no diff: os sete arquivos tocados são README.md, a spec, o SKILL.md novo, os dois instaladores e os dois testes. Nenhuma linha da tabela foi alterada porque o arquivo não foi tocado. Ressalva de forma: verifica-se a ausência de mudança, não a contagem de seis linhas no estado atual — a contagem prévia é premissa da spec, não observável no diff.

**P14 — os dois instaladores copiam `prototipar-frontend`, cada um numa lista só** — **atendido.**
`scripts/install.sh`: `local skills=(especificar codificar verificar homologar prototipar-frontend)` — uma lista, o loop existente cobre a nova entrada.
`scripts/install.ps1`: `$skills = @('especificar', 'codificar', 'verificar', 'homologar', 'prototipar-frontend')` — idem. Nenhum caminho separado para acessórias foi criado; o comentário acima de cada lista registra a decisão. Há teste por instalador (`test_instala_a_acessoria_de_prototipagem`) verificando o diretório e o `SKILL.md` no destino — resultado da execução não observado neste veredito.

**P15 — a ajuda para de anunciar "4 skills" e anuncia o número correto** — **atendido.**
Nos dois arquivos, o bloco `COMPONENTS` passou de "Copy the 4 skills (...)" para "Copy the 5 skills: the 4 of the cycle (especificar, codificar, verificar, homologar) + the accessory prototipar-frontend", e o menu interativo de "(the 4 SLE skills)" para "(the 5 SLE skills)". A ocorrência remanescente de "4" é "the 4 of the cycle", que não é contagem de skills instaladas e não colide com a asserção `"4 skills" not in stdout` dos testes. Os dois blocos que o Plano cita (`--components` e ajuda) foram cobertos.

---

## Observações fora dos critérios

- O passo 3 do Plano (README) foi executado: `README.md` ganha a linha `prototipar-frontend/SKILL.md # acessória: roda ANTES do ciclo, não é fase dele` na árvore de "O que tem neste repo". Não fecha critério, como a própria spec diz.
- O diff inclui a própria spec (`docs/specs/prototipar-frontend.md`, 54 linhas novas), o que é esperado num diff a partir de `d218dce`.
- Nenhum critério foi julgado **não atendido**.

---

## Resolução dos não verificáveis

Os três itens acima ficaram em aberto por restrição de leitura do `verificar` — escopo limitado ao diff —, não por incerteza sobre o artefato. Abertos os arquivos que faltavam, os três fecham em **atendido**. Nenhum deles era código divergente do critério, critério pedindo a coisa errada, ou lacuna a declarar fora de escopo.

**P1 — resolvido, atendido.** Os cinco `SKILL.md` têm exatamente os mesmos três campos de frontmatter, na mesma ordem: `name`, `description`, `disable-model-invocation: false`. Nenhum campo a mais nas quatro do ciclo, nenhum a menos na acessória. A cláusula "no mesmo formato das quatro" está observada, não presumida.

**P13 — resolvido, atendido.** `dominios.md:26-31` tem seis linhas — `segurança`, `privacidade`, `dados`, `integração`, `plataforma`, `experiência` — e nenhuma `frontend`. A contagem de seis agora é observada no estado atual, não herdada da spec como premissa.

**P9 — resolvido, atendido.** `especificar/SKILL.md:13` tem a seção `## Insumos`, e `:17` nomeia o insumo `**o pedido** — a demanda em texto`. Correspondência literal com o que o critério exige. A afirmação de `prototipar-frontend/SKILL.md:77` é verdadeira, não apenas declarada.

Adjacente ao P9, e registrado porque nenhum critério o cobre: `especificar` exige **dois** insumos — "o pedido" e "o alvo" (`especificar/SKILL.md:18`). O resíduo carrega o alvo apenas implicitamente, por morar em `<alvo>/docs/prototipos/`. Não é lacuna nova: a spec já decidiu, em "Fora de escopo", que o humano leva o arquivo — e quem leva sabe de qual codebase ele saiu. A entrega do alvo é do humano, por decisão explícita.

**Veredito final: 15 de 15 atendidos.** `especificar` fica intacto, como estava decidido.
