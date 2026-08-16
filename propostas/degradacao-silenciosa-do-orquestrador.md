# Degradação silenciosa do orquestrador

> **Origem:** uso real do SLE no projeto `cla_vendetta` (portal de clã de Ragnarok Online),
> lote `expedicao` — 10 specs, ciclo conduzido por `orquestrar` entre 2026-08-15 e 2026-08-16.
> **Estado:** proposta. Nenhuma skill foi alterada.
> **Log de pressão:** entrada Tipo G de 2026-08-16 aponta para este arquivo.
> **Irmã:** [`modo-emenda-na-homologacao.md`](./modo-emenda-na-homologacao.md) — mesmo
> padrão, outra ponta do ciclo: o método é correto no que descreve e silencioso onde
> a prática força a mão, e o silêncio é preenchido pela pior opção disponível.

## O que aconteceu

`orquestrar` conduziu um lote de 10 specs aprovadas no gate. As três primeiras
(`expedicao-01`, `-02`, `-03`) foram implementadas e declaradas prontas com **68 testes
verdes**. Nenhum desses verdes valia nada:

- `codificar` rodou em contexto isolado apenas na spec 01; as specs 02 e 03 foram escritas
  dentro da própria sessão do orquestrador;
- `verificar` **não rodou nenhuma vez** nas três;
- portanto o código, os testes e o veredito implícito saíram todos da mesma sessão que
  conduzia o lote — verde autoatestado, que é exatamente o que a segunda invariante existe
  para cortar.

A causa não foi decisão de método nem preguiça de julgamento. **A ferramenta de contexto
isolado exigia autorização explícita do humano naquele harness, e ela não tinha sido dada.**
Sem o mecanismo, `orquestrar` fez a única coisa que sabia fazer: continuou.

Quem detectou foi o **dono da demanda**, perguntando por que o lote não andava sozinho.
Nenhuma fase do método detectou. Não havia como: a fase que deveria medir era justamente a
que não estava sendo invocada.

## Por que o método não pegou

A skill `orquestrar` trata o mecanismo de isolamento como acessório, e está certa nisso:

> Onde o ambiente oferece contexto isolado sob demanda, use. Onde não oferece, **abra uma
> sessão nova à mão e entregue os insumos da tabela** — o contrato é o mesmo, e o resultado
> também. No limite, isto roda com duas pessoas e um editor de texto.

O texto é correto para um humano conduzindo. Ele é **inerte para um agente conduzindo**:
um agente não "abre uma sessão nova à mão". Ele tem a ferramenta ou não tem. E o arquivo
não diz o que fazer quando não tem — então o comportamento emergente é seguir em frente,
que é o pior dos três caminhos possíveis (isolar / parar / seguir fingindo).

O buraco não é de disciplina. É de **especificação de fallback**: o método descreve o estado
desejado e o estado degradado, mas não a transição entre eles.

## Falhas observadas, todas do orquestrador

As três falhas do lote foram do papel condutor. Nenhuma foi pega por fase nenhuma.

| # | falha | como apareceu | quem pegou |
|---|---|---|---|
| 1 | degradou para sessão única sem declarar | 68 verdes autoatestados em 3 specs | o humano |
| 2 | parou entre cada spec pedindo "continuo?" | humano virou barramento de mensagens | o humano |
| 3 | despachou 3 `verificar` em paralelo contra um banco só | vermelho falso; 2 dos 3 acusaram a entrega, 1 acusou um `ALTER TABLE` inocente | um dos próprios agentes, rodando sozinho depois |

A #3 merece nota: **os três verificadores eram igualmente capazes.** O que mudou foi que um
rodou sem concorrência e teve como medir. Independência não é virtude do agente; é
propriedade do arranjo. E o sintoma mentiu na direção mais cara possível — acusou a entrega
quando a culpa era do despacho. Um dos agentes registrou ter "perdido um bom tempo
perseguindo isto como defeito do produto".

## Correções propostas

### 1. `orquestrar` — isolamento indisponível é insumo que falta

**Não criar uma quinta exceção.** A skill diz, corretamente, que "não se inventa uma quinta",
e o caso já cabe numa das quatro: **o mecanismo de isolamento é insumo**. Sem ele, o insumo
falta, e insumo que falta sobe.

Acrescentar à seção *"O isolamento é o contrato; o mecanismo é acessório"*:

> **Se você não tem como isolar, isso é insumo que falta — pare e suba.**
> Não conduza o ciclo em sessão única "enquanto isso". Um `codificar` e um `verificar` que
> rodam na sessão de quem conduz não produzem verificação: produzem concordância com
> aparência de verde. Declarar a degradação é obrigatório; absorvê-la em silêncio é a
> única forma de falha do método que nenhuma fase posterior consegue detectar.

Acrescentar ao checklist *"Antes de devolver"*:

> - [ ] Cada fase rodou em contexto isolado de verdade — ou a impossibilidade foi declarada
>   ao humano **antes** de qualquer código ser escrito.

### 2. `orquestrar` — paralelismo e recurso exclusivo

A skill hoje é **silenciosa** sobre despachar fases em paralelo. O silêncio foi lido como
permissão. Acrescentar, próximo ao despacho automático:

> **Fases isoladas podem correr em paralelo apenas quando não compartilham estado mutável.**
> Banco de teste, arquivo de lock, porta de servidor, diretório de build e worktree são
> estado mutável compartilhado. Duas fases que rodam a mesma suíte contra o mesmo banco se
> derrubam, e o vermelho resultante acusa a entrega em vez do despacho — é o defeito mais
> caro de diagnosticar porque mente sobre a própria origem.
> Na dúvida, serialize: o custo é tempo de parede, e o custo do erro é um diagnóstico inteiro.

### 3. `orquestrar` — a tabela de insumos está incompleta para `verificar`

Na tabela da seção *"A fronteira: o que atravessa"*, a linha de `verificar` lista
"o caminho da spec; o ref base do diff; o escopo; o alvo".

**Faltou o que a spec cita como contrato mas não contém.** No lote real, `verificar` da spec
01 classificou a fidelidade visual como `não verificável` — não porque o critério fosse
imensurável, mas porque o protótipo de referência não estava na lista de leitura que o
orquestrador passou. Um `não verificável` falso é caro: pela tabela de roteamento ele **sobe
para o humano** como defeito de spec, quando era insumo faltando por erro do despacho.

Alterar a linha para:

> | `verificar` | o caminho da spec; o ref base do diff; o escopo; o alvo; **os artefatos que a spec cita como contrato e não contém** (protótipo, esquema externo, documento de referência) |

### 4. `especificar` — contrato do dono da demanda vira critério numerado

No lote real, o dono da demanda declarou uma exigência dura e literal:

> "Entendo que o protótipo não é copiado igual em termos de CÓDIGO, mas visualmente deve
> ser IGUAL."

Nas specs 01 a 09 isso virou linha de **contrato técnico**, fora de C1–C15. Consequência
medida na spec 04: o verificador comparou as telas, achou uma diferença real (o bloco de
rendimento perdeu a moldura da tela de fim do protótipo) e **classificou a spec como 15/15
atendida assim mesmo** — não tinha onde pendurar o veredito. O achado só não se perdeu
porque foi anotado como item extra, fora da estrutura.

Acrescentar a `especificar`, perto da seção *"O que é critério"*:

> **Exigência dura do dono da demanda é critério numerado, não contrato técnico.**
> O contrato técnico restringe *como* implementar; o critério declara *o que precisa ser
> verdade*. Se o dono da demanda disse "tem de ser X" e X é observável, X é critério — senão
> `verificar` mede e não tem onde classificar, e a spec fecha verde com a exigência violada.
> Contrato técnico é para o que restringe a implementação, não para o que define o aceite.

### 5. Lacuna que estas correções **não** fecham

Vale registrar explicitamente, para não criar falsa sensação de cobertura:

**O isolamento compra independência de julgamento, não correção do contrato.** Na spec 04 o
verificador mediu certo contra uma spec que perguntava a coisa errada. Nenhuma quantidade de
sessões limpas conserta uma spec que não pede o que o dono da demanda quer — isso se conserta
no gate humano, e é por isso que ele existe.

As quatro correções acima reduzem falha de *condução*. A qualidade do contrato continua sendo
trabalho do humano no gate, e continua sendo a coisa mais barata de fazer e mais cara de pular.

## O que este ciclo demonstrou a favor do método

Registrado para equilíbrio, porque o log acima é todo de falhas.

Assim que o isolamento passou a funcionar de verdade, `verificar` devolveu três achados que a
sessão única não produziria:

- **`MotorDeCombate::TRAVA_LACO_INFINITO` participava da condição do `while`.** Se atingida, o
  combate saía com `desfecho = 'recuo'` — um defeito de programa virando resultado de jogo
  silencioso. Corrigido para lançar, com a exceção deliberadamente fora da hierarquia que os
  endpoints capturam, para não virar redirect com motivo.
- **A tela de fim da spec 04 não era visualmente igual ao protótipo** (moldura, largura,
  centralização), com o CSS interno correto — o tipo de defeito que só aparece comparando, e
  que quem escreveu o código não vê.
- **A instabilidade da suíte era do despacho, não do produto** — corrigido por um agente
  contra o diagnóstico de dois outros.

Nenhum dos três seria encontrado por quem escreveu o código, na sessão em que o escreveu.
