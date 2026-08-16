# Insumo canônico não é opcional

> **Origem:** ciclo `expedicao` no projeto `cla_vendetta` — 13 specs, 292 testes,
> homologado em 2026-08-16.
> **Formulação do autor do método, ao ler os achados:** *"requisitos canônicos
> PRECISAM ser cumpridos, independente da existência ou não de arquivos."*
> **Estado:** proposta. Nenhuma skill foi alterada.
> **Log de pressão:** entrada Tipo G de 2026-08-16 aponta para este arquivo.
> **Irmãs:** [`degradacao-silenciosa-do-orquestrador.md`](./degradacao-silenciosa-do-orquestrador.md)
> e [`modo-emenda-na-homologacao.md`](./modo-emenda-na-homologacao.md).

## A forma comum

Três propostas, um padrão só. O método é correto no que descreve; o que falha é
sempre a mesma coisa:

> **Um insumo canônico não chega, e a fase prossegue degradada sem que ninguém
> seja avisado.**

O texto das skills descreve o estado desejado. Não descreve o que fazer quando o
insumo falta — e o comportamento emergente, todas as vezes, foi **seguir em
frente**. Não por má-fé: seguir é a única coisa que o arquivo não proíbe.

## As quatro degradações deste ciclo

### 1. Contexto isolado indisponível → sessão única

A ferramenta de contexto isolado exigia autorização humana que não tinha sido
dada. `orquestrar` degradou para sessão única **em silêncio**: três specs fecharam
com 68 testes verdes escritos por quem escreveu o código, na mesma sessão que
escreveu a spec.

Detectado pelo dono da demanda, perguntando por que o lote não andava sozinho.
Detalhado em [`degradacao-silenciosa-do-orquestrador.md`](./degradacao-silenciosa-do-orquestrador.md).

### 2. `dominios.md` ausente → taxonomia improvisada

`especificar` referencia `../dominios.md`. O catálogo existe em
`echo-skills/dominios.md`, mas **não é instalado** em `~/.claude/skills/` — só os
sete diretórios de skill vão. O caminho resolve para um arquivo inexistente.

**As treze specs deste ciclo foram escritas sem o catálogo canônico de domínios.**
Cada agente caiu no vocabulário praticado nas specs anteriores (`miolo`,
`experiência`, `segurança`). Funcionou **por acidente**: havia specs anteriores de
onde copiar. Num repositório novo, cada spec inventaria a própria taxonomia — e o
roteamento por domínio, que é a razão de o catálogo existir, viraria adivinhação.

Detectado por um agente de `especificar` que resolveu declarar em vez de omitir —
comportamento correto, mas **não exigido por lugar nenhum**.

### 3. `.sle/manifesto.md` ausente → nível TDD por default

O alvo não tem manifesto. Consequência: `tdd-aplicavel` caiu no default
`ortodoxo`, **nenhum padrão de Clean Code foi declarado** para o Executor seguir, e
nenhum domínio está declarado como ativo no repositório.

Isto já estava registrado no `pressao-metodo.md` do alvo **desde 2026-08-08**, no
ciclo anterior, com a consequência sugerida ("criar o manifesto antes do próximo
ciclo"). O ciclo seguinte rodou inteiro sem ele. **Registrar não impediu nada** —
o que mostra que o log é instrumento de observação, não de enforcement, e que
falta o enforcement.

### 4. Ref base do diff ausente → o contra-exemplo que prova o ponto

O alvo não é repositório git. Sem ref base, **nenhuma verificação consegue medir o
delta da demanda** — só o estado atual. Nenhum veredito distingue *"isto é
verdade"* de *"isto passou a ser verdade neste ciclo"*.

**Esta foi declarada. Todas as treze vezes, no cabeçalho de cada veredito.**

E é justamente por isso que ela prova a tese: a declaração aconteceu porque o
orquestrador **escreveu a exigência em cada despacho**, à mão, treze vezes. A
skill `verificar` lista o ref base como insumo, mas não obriga a declarar a falta.
Bastaria o orquestrador esquecer uma vez para aquele veredito parecer completo
medindo um recorte.

**Confiabilidade que depende de alguém lembrar não é confiabilidade.**

## A proposta

### Regra geral, para todas as skills

> **Insumo canônico que falta é exceção, não default.** Nenhuma fase prossegue em
> silêncio por falta de insumo declarado na própria skill. Ou ela para e sobe, ou
> ela **declara a degradação no artefato que produz** — spec, veredito, relatório —
> em lugar fixo e visível, e nunca só no texto de resposta.
>
> Prosseguir degradado sem declarar é o único modo de falha que nenhuma fase
> posterior consegue detectar, porque o artefato sai com aparência de completo.

### Por skill

**`especificar`** — sem `dominios.md`, ou sem `.sle/manifesto.md` declarando os
domínios ativos: a spec sai com um bloco de degradação declarada no topo, dizendo
qual catálogo faltou e que vocabulário foi usado no lugar. Hoje ela cai no
default e a spec não carrega marca nenhuma.

**`verificar`** — a ausência de ref base já é insumo faltando pela tabela de
`orquestrar`, mas **quem exige a declaração hoje é o texto do despacho**. Ela
precisa ser exigida pela skill: veredito sem ref base declara no cabeçalho que
julga estado e não delta. Isso não pode depender de quem escreveu a chamada.

**`orquestrar`** — sem mecanismo de isolamento, para e sobe (é insumo que falta, e
cabe numa das quatro exceções que já existem, sem inventar uma quinta). Ver a
proposta irmã.

**`homologar`** — o relatório ganha seção fixa de **insumos ausentes**, preenchida
sempre, inclusive quando vazia. Seção que só aparece quando há problema é seção
que se esquece; seção que sempre aparece obriga a olhar.

### E o item que fecha o buraco de instalação

Os casos 2 e 3 não são de método, são de **instalação**: o `dominios.md` existe e
não é copiado; o `manifesto.md` tem template e não é gerado. Enquanto o instalador
não levar os dois, cada repositório novo começa degradado — e agora sabemos que a
degradação não aparece, porque nada obriga a declará-la.

Já há dois sinais Tipo G de 2026-08-07 sobre fricção de instalação, ambos
convergindo para "modo lite" e autodetecção do manifesto. Este é o terceiro, e ele
muda a leitura dos dois primeiros: o problema não é só a instalação ser trabalhosa
— é que **instalação incompleta é silenciosa**.

## O que esta proposta não resolve

Não impede que um insumo esteja **errado**, só que esteja **ausente e calado**.
Um `dominios.md` desatualizado passaria por todos os controles propostos aqui.

E não substitui julgamento: declarar a degradação não a conserta. O que muda é que
a decisão de aceitar o custo passa a ser de quem lê o artefato, e não uma omissão
que ninguém escolheu.
