# Método SLE — Spec Loop Engineering
### Uma disciplina para unir rigor de engenharia e velocidade de IA, com invariantes que aguentam pressão

> Prompt não é trabalho. Prompt é intenção. O trabalho é o que acontece entre a intenção e o sistema que sobrevive em produção — e é aí que a estrutura precisa segurar quando o cansaço bate.

> **Status: em teste, v6 do método.** Sucessor do ECHO. Documento vivo — trate como hipótese bem fundamentada, não como regra pronta. A tese completa que originou esta linhagem está em [`propostas/spec-loop-engineering.md`](./propostas/spec-loop-engineering.md).

---

## O que mudou na v6, e por quê

A v5 corrigiu o eixo da invariante 2 — de *escrever* para *atestar* — e o comportamento diário não acompanhou: continuou-se trocando de sessão para **escrever**, que é o custo alto, em vez de para **assinar**, que é o único que compra segurança. O resultado foi medido em campo: três colapsos de papel registrados em log de pressão num só mês, todos com a mesma causa (o humano escolhendo o resultado melhor porque contexto fresco corrige melhor), e uma válvula de escape morta — uma spec em vinte e sete usando o nível barato.

A v6 leva a correção da v5 até a consequência. Ela **não afrouxa nenhuma garantia**; ela move a fronteira do lugar caro para o lugar onde a garantia realmente mora.

| | v5 | v6 |
|---|---|---|
| fronteira dura | quatro (uma por handoff) | **uma** (o contrato precede a construção) |
| independência vem de | sessão nova a cada fase | **veredito de contexto limpo**, delegado a subagente |
| quem pode escrever teste | só o Validador | Validador (régua de critério) **e** Executor (régua de descoberta, provada por mutação) |
| ordem do TDD | vermelho sempre primeiro | vermelho primeiro **ou** mutação depois (`amplificado`) |
| menor unidade de trabalho | N1 (spec de 5 linhas) | **N0 — conserto**, sem spec, com regra de entrada objetiva |
| suíte completa | rodada em toda fase | **instrumento de atestação**, roda uma vez, por quem assina |

---

## Por que "SLE"

**Spec** — o contrato é a única fonte de verdade. Especificação primeiro, sempre.

**Loop** — não é linear. Cada tarefa entrega dados sobre a próxima. O que aprendemos na execução realimenta o desenho.

**Engineering** — disciplina de longo prazo, não atalho tático. Regras que sobrevivem à pressa.

Seis fases:

**D**efinir → **D**esenhar → **T**raduzir → **I**mplementar → **H**omologar → **O**bservar

*(Para quem for portar o método: Define → Design → Translate → Implement → Attest → Observe. "Homologar" não tem cognato usual em inglês de engenharia; **Attest** é o termo que carrega o conceito, e não por acaso — atestação é o que a v6 coloca no centro.)*

Distribuídas em cinco skills — nunca uma skill faz mais do que seu papel:

| Skill | Fases | Papel |
| --- | --- | --- |
| `specifier` | Definir | Spec: contrato falsificável. Não desenha, não planeja, não implementa |
| `designer` | Desenhar | Contrato arquitetural, plano, protótipo N3. Não escreve código de produção |
| `validator` | Traduzir + Homologar | Réguas de critério, esqueleto, homologação. Não implementa comportamento |
| `executor` | Implementar | Código de produção, réguas de descoberta. Não emite veredito |
| `observer` | Observar | Sinais, drift, propostas de reconciliação. Independente das outras |

**Por que cinco e não quatro (mudança v6).** Até a v5, `designer` cobria Definir e Desenhar, e o argumento era que o handoff entre elas custava mais do que a granularidade comprava. Esse argumento assumia **fronteira de skill = fronteira de sessão**. Na v6 as duas coisas são independentes: `specifier` e `designer` rodam na mesma sessão, sem passagem entre si. O custo que o argumento temia deixou de existir, e o que se ganha é real — o gate humano passa a cair sobre o *contrato* antes de alguém gastar desenhando o *como*, e os dois textos param de se contaminar. Uma frase do plano que poderia reprovar a entrega é critério, e está no arquivo errado.

---

## As 5 invariantes

O método se apoia em regras que **não são aspiracionais**. Elas são verificadas por hooks in-session (`tooling/hooks/`) e por CI (`tooling/ci/`):

1. **Quem desenha não implementa.** `specifier` e `designer` não escrevem código de produção. Bloqueado pelo hook `block-designer-writing-code`.
2. **Quem escreve não emite o veredito que chega ao humano (v6).** Escrever e atestar são atos distintos, e é o segundo que a invariante protege. O veredito de uma fase é produzido por leitura de contexto limpo — subagente ou sessão — sobre os artefatos, nunca pela parte que os produziu.
3. **Nenhum agente é árbitro.** Decisões arquiteturais, disciplinares e de trade-off ficam com o humano em pontos explícitos ("gates"). A ferramenta calcula **prontidão**; nunca **aceitação**.
4. **Observer é independente.** Quem observa e propõe reconciliações não é quem executou o que está sendo observado.
5. **O contrato precede a construção (v6).** A spec é escrita antes da sessão que constrói, e por um papel que ainda não sabe como vai implementar. É a única fronteira dura que sobrou, e a seção seguinte explica por que ela não é negociável enquanto as outras foram.

Se uma dessas invariantes é violada em silêncio, o método degrada — e degrada primeiro na direção que menos dói no curto prazo (aceitar a spec vaga, deixar o executor "consertar" o teste, homologar sem revisar).

---

## A única fronteira dura, e por que é essa

Sessão separada **não produz código melhor**. Produz **veredito não contaminado**. Isso é bem mais estreito do que "sessões separadas para tudo", e a v6 opera essa distinção.

Contexto fresco corrige melhor — é fato observado, e foi por isso que os colapsos aconteceram: o humano escolheu o resultado superior, e o método chamou isso de dívida. Um método que cobra pedágio sobre a escolha certa está errado, não a pessoa.

O que a separação comprava era uma coisa só: **quem diz que está pronto não ser quem se convenceu de que está.** Isso se preserva movendo a fronteira da *sessão* para a *atestação* — ver "Atestação por leitura limpa", abaixo.

Uma coisa **não** se recupera assim, e por isso continua sendo fronteira dura: uma spec escrita dentro do contexto que já sabe como vai implementar deixa de ser contrato e vira descrição. Os critérios se moldam ao que é fácil de construir, e nenhum veredito posterior detecta isso — o verificador só consegue conferir a entrega contra o contrato, e o contrato já nasceu torto. Foi exatamente o que produziu um critério silencioso sobre um dos três estados de uma máquina: a cabeça já estava no caminho feliz do código quando o critério foi escrito.

**Consequência prática:** `specifier` roda antes, e sozinho. Depois dele, `designer` → `validator` → `executor` → conserto podem ser **uma sessão só**, com o contexto quente do começo ao fim.

---

## Atestação por leitura limpa (v6)

O veredito de fim de fase é produzido por um leitor que não participou do trabalho. Na prática, um subagente na mesma sessão: ele não herda a conversa, lê só os artefatos, e custa zero troca de contexto para o humano.

Três regras, e as três existem porque o desenho vaza sem elas:

**1. O veredito vai para arquivo, não para o repasse.** O resultado do subagente volta para a sessão que produziu o trabalho — que é exatamente a parte que ele audita. Repassado, ele pode ser amaciado sem má intenção. O verificador escreve em `docs/specs/<nome>-veredito.md`, e o humano lê o arquivo. A sessão de trabalho diz onde está o arquivo, e nada além.

**2. O input é derivado, não redigido.** Quem escreve o prompt do verificador é a parte contaminada, e um prompt como *"verifique se a correção está certa"* já afirma que existe correção e que ela é plausível. Pior: pode omitir o arquivo onde o problema mora. O molde é fixo:

```
Leia <spec> e o diff de <base>..HEAD.
Para cada critério, diga: atendido / não atendido / não verificável, e por quê.
Saída em <arquivo>. Não sugira correção.
```

Sem uma linha de prosa de quem trabalhou. É o mesmo princípio que faz a passagem ser gerada em vez de escrita: tirar do agente contaminado a chance de enquadrar.

**3. Confira o que o verificador recebe de graça.** Um harness pode pré-carregar assunto de commit, status do repositório ou resumo de sessão — e isso já entregou, uma vez, a conclusão que uma auditoria existia para derivar. Teste **uma vez** o que chega ao subagente sem você mandar. Se chegar histórico, o verificador precisa rodar sem ele, ou receber diff sem mensagens de commit.

**Quando não é necessário.** Quando o critério é objetivo, a suíte é o atestador. Ninguém abre leitura limpa para confirmar que um teste estrutural passou. Veredito por leitura limpa é para o que exige julgamento.

---

## Regra de ouro

**Nenhuma linha de código antes de existir contrato; nenhuma implementação antes de existir régua (ou plano manual aprovado); nenhuma tarefa "pronta" sem verificação real e sem veredito de leitura limpa.**

Tamanho escala com o risco:

- **N0 (conserto):** sem spec, sem plano, sem passagem. Uma sessão. Ver a regra de entrada abaixo.
- **N1 (micro):** spec de 5 linhas. Pula Desenhar.
- **N2 (padrão):** spec completa + contrato arquitetural.
- **N3 (complexo):** spec enriquecida + contrato arquitetural + **protótipo preservado como artefato de fidelidade**. Testes de fidelidade compõem a Camada 3 do Validator.

### N0 — a regra de entrada do conserto

Um **conserto** dispensa o ciclo quando as três valem:

1. A régua é um comando com exit code, e você consegue escrevê-la **antes** do conserto.
2. Nada persiste de novo — sem migração, sem campo, sem decisão de authz.
3. Nenhum contrato público muda — rota, schema, permissão.

Falhou uma, sobe para N1. **Nenhuma das três é pergunta de julgamento** — e isso é deliberado.

**O ciclo do conserto:** escreve a régua, vê vermelho, conserta, vê verde, commit. O registro é o teste: ele fica no repositório dizendo o que foi combinado, que é mais do que uma spec arquivada faz.

**Por que N0 existe (e por que N1 morreu sem ele).** O nível é declarado no começo, quando se sabe menos, e os dois erros não custam igual: declarar barato e errar é visível e caro; declarar caro sem precisar é invisível, porque produz trabalho, e trabalho parece rigor. Enquanto o ônus for "justifique por que isto é barato", a resposta segura é sempre escalar. Por isso a entrada do N0 é **consulta objetiva, não julgamento** — e por isso o nível em geral deveria ser derivado das mesmas três perguntas em vez de escolhido.

### Roteamento a-priori: o que nem chega a virar critério

> **Um item que seria verdadeiro numa spec que ainda não foi escrita não pertence a esta spec.**

Regra decidível a priori e válida para o projeto inteiro é **convenção com régua permanente**, não critério. Escrita como critério, ela é re-litigada a cada spec e o teste dela morre junto com a fatia; escrita como convenção com teste estrutural, ela é escrita uma vez e vale para sempre.

O precedente já existe e funciona: RLS obrigatório em toda tabela é verificado por teste estrutural que quebra o build, e ninguém escreve "esta tabela terá RLS" como critério de aceite. Generalize isso. Esta é a poda que corta mais cerimônia, porque age na **entrada** do ciclo em vez de aparar o que já entrou.

---

## Fase 1 — Definir (D) — skill `specifier`

**Objetivo:** transformar intenção vaga em contrato verificável, **antes** de existir qualquer contexto de implementação.

- **O que**, em uma frase — comportamento esperado, não implementação.
- **Critérios de aceite** — cada um vira régua na Fase Traduzir. Critério que não pode virar verificação concreta volta para reescrita.
- **Casos de borda** previsíveis, marcados por domínio em N2+.
- **Escopo negativo** — o que fica de fora.
- **Restrições não-funcionais** e **ambiente/destino**.

**Marcação por domínio (N2+):** cada critério e caso de borda é classificado como pertencente a um domínio, cross-cutting retido, ou miolo. Catálogo em [`dominios.md`](./dominios.md).

**Falsifiability gate:** a spec só é pronta se cada critério pode ser objetivamente falseado. Checado aqui, reforçado pelo `validator` na Fase T.

**Regra de fechamento:** decisão técnica pendurada = spec incompleta.

**Forma (v6):** um critério é **uma frase falsificável e o nome da régua**. Sem parágrafo de justificativa. Se o porquê importa, ele é decisão, e decisão mora em `.sle/pressao-metodo.md` — não no meio do contrato.

---

## Fase 2 — Desenhar (D) — skill `designer`

**Objetivo:** dar precisão ao *como*, sem escrever código de produção. Só existe em N2 e N3.

- **Contrato arquitetural** — componentes, interfaces, invariantes de dados, trade-offs resolvidos. Falsificável, uma cláusula por linha. Ele é rede de junção entre spec, teste e módulo; rede não precisa de prosa.
- **Plano** — passos em ordem, arquivos afetados, mapeamento com os critérios.
- **Protótipo (só N3)** — código exploratório salvo em `docs/specs/<nome>-prototipo/`, preservado, disponível como referência não-copiável.

**Handoff:** `designer` **não abre sessão nova** para `validator` (v6). Ele fecha com o gate humano sobre o plano e o trabalho continua. A passagem continua existindo como registro — ver "Passagem gerada", abaixo.

---

## Fase 3 — Traduzir (T) — skill `validator`

**Objetivo:** transformar cada cláusula em verificação concreta.

- **Camada 1 (BDD):** cada critério de aceite vira régua Given/When/Then.
- **Camada 2 (contrato):** cada cláusula vira teste de invariante estrutural.
- **Camada 3 (fidelidade, só N3):** confronto com o protótipo preservado.

### O esqueleto pertence a esta fase (v6)

Em linguagem de tipos, um teste não falha pelo motivo certo se o alvo não existe — ele falha na compilação, e vermelho de compilação não é vermelho de TDD. Criar a classe vazia, a assinatura sem corpo, o módulo sem comportamento é **fazer o vermelho ser vermelho**, e é trabalho do Validador.

A fronteira é mecânica e se verifica rodando: **depois do esqueleto, nenhum teste pode passar.** Se algum ficou verde, não era esqueleto — era implementação, e aí existe comportamento a atestar. Zero verde = zero comportamento = nada a assinar.

### TDD contextualizado

O manifesto local (`.sle/manifesto.md`) declara `tdd-aplicavel`:

- `ortodoxo` — tudo é teste automatizado, vermelho antes do código.
- `amplificado` **(v6)** — código primeiro, régua derivada **da spec** logo em seguida, falsificabilidade provada por **mutação descartável** antes de a fase fechar. Régua que não quebra sob mutação não conta como cobertura.
- `parcial` — o que der, automatiza; o que não der, plano manual estruturado.
- `manual` — codebase legada; plano de validação manual com evidências anexáveis.

**Por que `amplificado` é legítimo.** Vermelho-primeiro é falsificabilidade **de graça**; teste-depois é falsificabilidade **comprada com mutação**. As duas chegam ao mesmo lugar — um teste que pode reprovar. A segunda custa um passo e devolve o fluxo de escrever código com o problema quente na cabeça.

**Os dois limites, e nenhum é opcional:**

- **Derive da spec, nunca da leitura do próprio código.** Teste escrito olhando a implementação concorda com ela por construção, e nenhuma mutação salva isso. Abra o critério, não o arquivo.
- **Mutação não encontra o ramo que ninguém escreveu.** Ela prova conteúdo sobre o código que existe. Critério ausente continua invisível, e é por isso que a Camada 1 continua derivada da spec.

**Exceção que fica em `ortodoxo`:** os domínios obrigatórios do manifesto (tipicamente `segurança` e `privacidade`). Não por pureza — porque ali um teste que concorda com o defeito não produz bug visível, produz vazamento silencioso, e é a única classe onde o custo do erro justifica o custo da ordem.

### Poder estrutural e emenda

Se o Validador não consegue escrever régua porque a spec é vaga, **retorna estruturalmente para o `specifier`**.

Para spec que estava certa até o mundo mostrar o contrário, o movimento é **emendar**: altera-se critério, régua ou código; roda-se só o que foi tocado; registra-se uma linha em `.sle/pressao-metodo.md`. Vale em qualquer fase, inclusive depois do verde.

**Destravar ≠ ajustar (v6).** Nem toda emenda gera dívida de atestação:

| movimento | o que é | dívida? |
|---|---|---|
| **destravar** | a régua não chegava a rodar — erro de gramática, import quebrado, tabela renomeada, compilação | **não** — não muda o que ela afirma, só permite que ela chegue a afirmar |
| **ajustar** | a régua rodava; mudou **o que ela consegue pegar** — recorte, assertion, tolerância | **sim** — cobertura estreitada pode esconder defeito |

Só `ajustar` exige veredito de leitura limpa sobre o critério afetado.

---

## Fase 4 — Implementar (I) — skill `executor`

**Objetivo:** código de produção fiel à spec, às réguas existentes e (em N3) ao protótipo.

### Duas classes de régua (v6)

| classe | origem | quem escreve | prova de conteúdo |
|---|---|---|---|
| **régua de critério** | derivada da spec | quem leu a spec sem ler o código | vermelho-primeiro |
| **régua de descoberta** | achada implementando | quem achou | **mutação obrigatória** |

Até a v5 o Executor não podia escrever teste, e isso era perda pura: ele descobre casos reais implementando e não tinha onde registrá-los. A v6 libera a segunda coluna. A primeira não some, porque mutação não revela critério ausente.

O Executor continua **sem poder alterar semanticamente régua de critério**. Refactor não-semântico é permitido (DRY, fixture, nome interno), verificado pelo hook `block-executor-writing-tests-semantically`. Teste de critério que parece errado é sinal para o humano — retorno ou emenda —, nunca edição silenciosa.

### As três réguas, e de quem é cada uma (v6)

| régua | escopo | quando | quem |
|---|---|---|---|
| **foco** | um método / um arquivo, em watch | o tempo todo | Executor |
| **fatia** | só os testes desta spec | ao fechar uma frente | Executor |
| **completa** | tudo, incluindo e2e que exige build | uma vez, ao fechar a fase | quem assina |

> **A suíte completa é instrumento de atestação, não de desenvolvimento.**

O Executor nunca a roda. Rodá-la "para garantir" no meio da implementação é ansiedade operando como método: torna a sessão exaustiva e não compra nada que a régua de fatia não compre mais barato. A régua de fatia não precisa de tag nem de infraestrutura — **a passagem já lista os arquivos de teste da spec**, e aquela lista é a seleção.

O que só a completa pega é quebra **fora** da spec — e isso é real: um teste de contenção de uma spec antiga reprovando uma spec nova só aparece ali. Ela não some; ela muda de dono, e o dono é quem não tem mais nada a fazer além de esperar um runner.

**Sinal de alerta:** re-prompting da mesma tarefa pela terceira vez. Quase sempre significa spec ou régua ambígua — retorno ou emenda, não insistência.

---

## Fase 5 — Homologar (H) — skill `validator`

**Objetivo:** provar, com evidência, que o código atende ao contrato.

- Roda a **régua completa**. Se falha, volta para Implementar.
- Executa o plano de validação manual, anexando evidências.
- Conduz **checklist de revisão arquitetural** — perguntas que o humano responde.
- **Emite o pedido de veredito de leitura limpa** (molde fixo, saída em arquivo) e aponta o arquivo ao humano sem resumi-lo.
- Fecha o log em `docs/specs/<nome>-log.md` com resultado real.

**Isolamento em N3:** durante Homologar, o protótipo não é carregado. Ele é referência de fidelidade da Fase T, não critério de aceite.

**A Homologar pode corrigir código (v6).** Contexto fresco corrige melhor, e a correção acontece onde o problema foi encontrado. O que muda é que a atestação **do que foi corrigido** vem da leitura limpa, não da própria sessão. Corrigir e assinar continuam sendo atos distintos; só deixaram de exigir duas sessões.

---

## Fase 6 — Observar (O) — skill `observer`

**Event-driven** — bug, drift, feedback. Analisa, propõe reconciliação, registra padrão.
**Cadence-driven** — retrospectiva periódica sobre pressão-método e pressão-catálogo.

**Saída estritamente propositiva.** O Observer nunca decide. Reservado ao humano: calibração disciplinar.

**Isolamento:** Observer não é quem executou o trabalho observado.

---

## Verbosidade — a regra que poda tudo

> **Prosa só onde há decisão humana. Em todo o resto, uma linha.**

| artefato | forma |
|---|---|
| **critério** | uma frase falsificável + nome da régua |
| **cláusula de contrato** | uma linha |
| **resumo ao humano** | três blocos: *o que mudou*, *o que está vermelho*, *o que precisa da sua decisão*. Terceiro vazio → resumo de duas linhas |
| **passagem** | gerada, não escrita (abaixo) |
| **`pressao-metodo.md`** | **prosa inteira** — é o único lugar do sistema onde alguém pensa |

O teste para cortar qualquer texto: *alguém decide algo depois de ler isto?* Se não, é uma linha.

E o critério geral, que serve para podar o que sobrar:

> **Artefato que não é lido por ninguém depois de produzido é burocracia, por melhor que esteja escrito.**

O plano vira engenharia quando dirige a ordem dos commits e a seleção de testes. A passagem, quando abre a sessão seguinte. A spec, quando alguém a consulta para escrever régua. O que não passar nisso, corta.

### Passagem gerada

A passagem continua obrigatória como **registro auditável**, mas metade dela é derivável e não deve ser escrita à mão: mapa de cobertura critério→teste (o teste cita o critério), estado da suíte (é a saída do runner), lista de arquivos tocados (é o diff).

O que é insubstituível, e não passa de umas quarenta linhas: **o que o destino recebe**, **o que o destino não pode receber e por quê**, e **as derivações de nome que o tradutor fez** — rotas, colunas, componentes. Sem a última, o papel seguinte "corrige" um nome que era escolha deliberada.

---

## Enforcement em duas camadas

**Camada 1 — hooks in-session** (`tooling/hooks/`). Bloqueia no momento da violação. Depende do harness expor a identidade do papel ativo.

**Camada 2 — CI de repositório** (`tooling/ci/`). Verifica no PR: paridade spec/teste, cobertura de critério, coerência entre mudança de código e de spec. Independente do harness.

**Ordem de instalação importa (v6).** Instale o caminho barato **antes** do enforcement. Enforcement sobre um ciclo pesado tranca a porta do labirinto em vez de abrir a saída — e o método degrada exatamente aí, porque a pessoa passa a contornar a regra em vez de usá-la.

---

## Por que isso é replicável em qualquer plataforma

| Fase | Neste repo (Claude Code) | Qualquer outra ferramenta |
| --- | --- | --- |
| Definir | skill `specifier` | Documento de spec versionado, escrito antes |
| Desenhar | skill `designer` | Contrato + plano + protótipo em pasta separada |
| Traduzir | skill `validator` (fase T) | Réguas + esqueleto antes do comportamento |
| Implementar | skill `executor` | Agente focado em passar nas réguas existentes |
| Homologar | skill `validator` (fase H) | Suíte completa + plano manual + veredito de leitura limpa |
| Observar | skill `observer` | Retro periódica + log de pressão |

A ferramenta muda. O contrato entre intenção, execução e verificação, não.

---

## Checklist rápido

- [ ] A spec foi escrita **antes** da sessão que constrói (invariante 5)?
- [ ] Cada critério é falsificável, em uma frase, com régua nomeada?
- [ ] Nenhum item da spec seria verdadeiro numa spec futura (senão é convenção)?
- [ ] O nível saiu das três perguntas objetivas, e não de julgamento?
- [ ] Se `amplificado`: toda régua nova tem mutação registrada?
- [ ] O Executor rodou só régua de foco e de fatia — nunca a completa?
- [ ] O veredito de fim de fase veio de leitura limpa, em arquivo, com input derivado?
- [ ] Toda emenda foi classificada em **destravar** ou **ajustar**, e só a segunda abriu dívida?
- [ ] Alguma dívida de atestação segue aberta? Spec com dívida aberta não é spec fechada.
- [ ] O Observer analisou os sinais e propôs reconciliação, e o humano decidiu?

---

*Documento vivo — revisado depois de aplicar em tarefas reais. Ajuste o que não encaixar; o método serve ao trabalho, não o contrário.*
