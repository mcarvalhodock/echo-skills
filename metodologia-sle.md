# Método SLE — Spec Loop Engineering

Rigor de engenharia na velocidade da IA. Quatro skills, duas invariantes, um artefato.

## O ciclo

| skill | entrega |
|---|---|
| `especificar` | plano específico da demanda — no máximo **15 critérios falsificáveis** |
| `codificar` | o código que satisfaz a spec, mais os testes **daquela demanda** |
| `verificar` | roda o que a demanda toca, e obtém veredito de **leitura limpa** |
| `homologar` | **no fim do desenvolvimento**: suíte completa e o checklist arquitetural |

`homologar` não roda por demanda. Cada demanda fecha em `verificar`; a suíte inteira roda uma vez, no fim. Homologar cada spec contra a suíte completa é o custo que essa separação existe para evitar.

Cada fase roda em **sessão limpa** e não invoca a seguinte. Quem encadeia é o roteador — ou você, à mão. Uma fase que emenda na próxima dentro da mesma sessão leva o próprio raciocínio junto, e é esse vazamento que a separação existe para cortar.

## As duas invariantes

**1. O contrato precede a construção.** A spec é escrita antes de existir contexto de implementação. Uma spec escrita por quem já sabe como vai construir deixa de ser contrato e vira descrição: os critérios se moldam ao que é fácil, e nenhuma verificação posterior detecta isso — quem verifica confere a entrega contra o contrato, e o contrato já nasceu torto.

**2. Quem escreve não atesta.** Escrever e afirmar que está pronto são atos distintos, e é o segundo que a invariante protege. Como `codificar` escreve o próprio teste, a suíte verde é autoatestada — e verde autoatestado já produziu "está pronto" em cima de critério não atendido. O antídoto é a leitura limpa, dentro de `verificar`.

Nada mais é invariante. Não há papel bloqueado por hook, não há marker-file de sessão, não há fronteira de quem pode tocar qual arquivo. Essas defesas custaram mais do que o que protegiam.

## Leitura limpa

Um subagente de contexto limpo, que não participou, lê só os artefatos e escreve em arquivo:

```
Leia <alvo>/docs/specs/<nome>.md e o diff de <base>..HEAD limitado a <escopo>.
Para cada critério, uma linha "- **<ID>** — atendido|não atendido|não verificável", e o porquê depois.
Não sugira correção. Não leia mais nada.
Saída em <alvo>/docs/specs/<nome>-veredito.md.
```

Três regras, e existem porque o desenho vaza sem elas:

1. **O veredito vai para arquivo, e ninguém o resume.** Ele audita a sessão que o pediu; repassado, amacia sem má intenção.
2. **O pedido é o molde acima, literal.** "Confira se a correção está certa" já afirma que existe correção e que ela é plausível.
3. **Confira o que ele recebe de graça.** Se o harness entrega mensagem de commit junto do diff, passe o diff sem elas.

Custa dez linhas. É o único ritual que se pagou.

## Um artefato

**O veredito.** Só ele.

Não há passagem entre fases, log de fase, mapa de cobertura nem registro de pressão. Documentação sobre o trabalho não é trabalho — e, pior, dá credibilidade a afirmações que ninguém verificou.

### Estado é campo. Explicação continua morta.

Sessão limpa não herda conversa. O que a conversa carregava de graça precisa de outro lugar — e a distinção entre o que merece esse lugar e o que não merece é decidível:

- **Estado** é fato: o ref base do diff, quais specs pertencem a este ciclo, qual é o alvo, qual insumo falta. Pode estar errado e se confere contra a realidade. Vira **campo** — insumo declarado na entrada da fase.
- **Explicação** é leitura: como o código resolve o problema, por que aquele padrão, o que foi difícil. Não se confere contra nada. Continua fora.

O teste: **se o item tem um valor que se confere, é campo; se tem uma leitura, é prosa.** A passagem da v2 reprovava nesse teste em cada frase — é por isso que a sessão limpa não a traz de volta.

## O teto de 15 critérios

Se a demanda não cabe em 15 critérios, ela é grande demais: vira duas demandas.

Spec sem teto cresce sozinha, e tudo abaixo dela incha junto — implementação, teste, verificação. Uma spec de 36 critérios não é mais completa que duas de 18; é uma que ninguém termina.

## Uma spec pode depender de outra. Um critério, não.

Dependência entre specs é normal e se declara. O que não pode existir é um critério da spec 06 sendo pré-requisito para a spec 01 fechar: aí a spec que é dependência só fecha depois de quem depende dela, e nenhuma das duas fecha nunca.

O sintoma é característico e demora a ser lido: toda entrega sai "parcial", nenhuma spec aparece inteira verde, e a causa parece falta de trabalho quando é ordem invertida.

A mesma regra vale dentro da spec: uma fatia só é fatia se **fecha sozinha**. Domínio que não separa limpo não vira fatia — spec pequena inteira vale mais que spec fatiada que precisa de reconciliação.

## O que nem chega a virar critério

**Um item que seria verdadeiro numa spec que ainda não foi escrita não pertence a esta spec.**

Regra decidível a priori e válida para o projeto inteiro é **convenção com régua permanente**, não critério. Escrita como critério, é re-litigada a cada spec e o teste dela morre junto com a demanda; escrita como convenção com teste estrutural, é escrita uma vez e vale para sempre.

Ninguém escreve "esta tabela terá RLS" como critério de aceite — existe um teste estrutural que quebra o build. Generalize isso. É a poda que corta mais cerimônia, porque age na entrada.

## Conserto dispensa o ciclo

Um conserto pula tudo quando as três valem:

1. A régua é um comando com exit code, e você a escreve **antes** do conserto.
2. Nada persiste de novo — sem migração, sem campo, sem decisão de authz.
3. Nenhum contrato público muda — rota, schema, permissão.

Falhou uma, é demanda e entra em `especificar`. **Nenhuma das três é pergunta de julgamento**, e isso é deliberado: enquanto o ônus for "justifique por que isto é barato", a resposta segura é sempre escalar — e trabalho a mais parece rigor.

O ciclo do conserto: escreve a régua, vê vermelho, conserta, vê verde. O registro é o teste.

## Verbosidade é defeito

Spec que passou de duas telas está explicando em vez de decidir. Entrega em três blocos — o que mudou, o que está vermelho, o que precisa da sua decisão — e o terceiro costuma ser vazio.

Quem lê já tem o contexto. O que não pode faltar é o que precisa ser **verdade**, não por que alguém acha que precisa.

## Gates humanos

Arquitetura é julgamento humano. As skills calculam **prontidão**; nunca **aceitação**.

**Duas paradas por ciclo, e o número não cresce com o tamanho do lote:**

```
especificar × N → ┤aprovar o lote├ → (codificar → verificar) × N → homologar → ┤checklist├
```

O lote é o que mantém o número em dois. As N specs são escritas antes de qualquer código, e as perguntas que sobrarem sobem todas juntas no mesmo gate. Aprovar de uma em uma devolveria N+1 interrupções — o custo que o loop existe para eliminar.

`verificar` não faz pergunta arquitetural. Se fizesse, faria trinta vezes por ciclo, e ninguém responde trinta.

Fora das duas paradas planejadas, o loop só interrompe por exceção: critério `não verificável`, que é defeito de spec; teto de tentativas estourado; ou insumo que falta. Spec bloqueada por insumo entra em quarentena junto com as que dependem dela, e o resto do lote segue — problema local não vira parada global.

## O alvo

O método não mora no codebase que ele trabalha. Instala-se uma vez, num diretório, e opera sobre N codebases: o **alvo** é parâmetro de cada fase, e todo caminho — `docs/specs/`, `.sle/manifesto.md`, a suíte, o ref base — é relativo a ele.

A exceção é `dominios.md`: o catálogo é do método, e é o mesmo para todo alvo. É essa separação que permite ao alvo deixar de ser um diretório local e virar outra coisa depois, sem tocar em nenhuma fase.

## Por que é replicável

Nada aqui depende de plataforma: são quatro prompts, uma leitura de contexto limpo e um arquivo de veredito. Roda em qualquer harness que saiba abrir uma sessão limpa — e, no limite, roda com duas pessoas e um editor de texto.
