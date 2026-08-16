# O modo emenda, e por que ele cabe em `homologar`

> **Origem:** uso real do SLE no projeto `cla_vendetta`, mini-game `expedicao` —
> as horas seguintes ao fechamento do lote de 10 specs, com o dono da demanda
> validando o portal ao vivo em 2026-08-16.
> **Estado:** proposta. Nenhuma skill foi alterada.
> **Decisão de forma já tomada pelo autor do método:** isto é **atribuição nova de
> `homologar`**, não um passo novo do ciclo.
> **Log de pressão:** entrada Tipo G de 2026-08-16 aponta para este arquivo.
> **Irmã:** [`degradacao-silenciosa-do-orquestrador.md`](./degradacao-silenciosa-do-orquestrador.md).

## O buraco

O ciclo é `especificar` → `codificar` → `verificar` → `homologar`. Ele termina em
`homologar`, e o modelo implícito é que ali o trabalho acabou.

**Não acabou.** Homologar é justamente quando o dono da demanda abre o produto e
começa a pedir mudanças de duas linhas: um botão que devia ser clicável, um texto
que não informa nada, um aviso no lugar errado da tela, uma barra que mente.

O método não tem lane para isso. Fazer spec para *"tira o ×4 do nome no cinto"* é
absurdo — o teto de 15 critérios e o gate humano custam mais que a mudança. E como
a única alternativa oferecida é essa, o que acontece na prática é **nada**: quem
está conduzindo escreve o código, escreve o teste, declara verde e segue.

Foi exatamente o que aconteceu neste projeto.

## O que aconteceu, sem atenuar

Depois de as 10 specs fecharem verificadas, com 254 testes verdes, o dono da
demanda passou a validar ao vivo. Em poucas horas saíram **sete emendas**:

1. o nó da batalha virou o botão de entrar, e o botão separado saiu;
2. a barra de vitalidade passou a usar o teto real em vez da vitalidade de entrada;
3. versão automática nos assets, porque o navegador servia JS antigo;
4. a trilha sonora passou a retomar de onde parou entre telas;
5. vencer sozinho passou a encerrar o pedido de ajuda aberto e devolver o ouro;
6. o aviso de fim de expedição subiu do rodapé para o topo da tela;
7. os atributos passaram a mostrar efeito medido e as três parcelas da soma.

**Todas as sete foram escritas, testadas e declaradas verdes pela mesma sessão que
as conduziu.** Nenhuma passou por `verificar`. É o verde autoatestado que a segunda
invariante existe para cortar — e é a mesma falha que este projeto já tinha cometido
nas specs 01–03 e corrigido dias antes.

### O que segurou, e o que não segurou

**Segurou:** a suíte de 279 testes pegou regressões, e `FidelidadeDaTelaTest` —
que só existe porque uma verificação independente reprovou o C14 da spec 10 e
obrigou a criar testes de **marcação renderizada** — reprovou a emenda 6 na
primeira execução, porque ela mudou uma classe do HTML.

Vale o registro: **um método bem aplicado antes deixou a rede que segurou o
trabalho mal aplicado depois.** Isso é um argumento a favor do método, não contra.

**Não segurou, e este é o ponto:**

- Na emenda 5, quem conduzia **afirmou um vazamento de ouro que não existia**. O
  teste recém-escrito somava a parcela retida duas vezes (`ouroDoSistema()` já
  soma `ouro + ouro_retido`). O erro só foi descoberto por inspeção de bytes, por
  iniciativa própria. Se tivesse sido "corrigido" com base naquela leitura, teria
  quebrado o caminho de escrow que a verificação da spec 08 havia sondado com
  sete provas independentes.
- Uma recalibragem de uma linha (`ouro_presenca_diaria`, 1000 → 300) foi aplicada
  **sem rodar a suíte**. Quebrou seis asserções de `PresencaTest`, que comparavam
  contra o literal semeado. A quebra só apareceu porque uma `verificar` de outra
  spec rodou a suíte completa por acaso, horas depois.

## O dano que ninguém lembra: divergência de spec

Este é maior que o verde autoatestado, e é o argumento mais forte da proposta.

Várias das sete emendas **contradizem critérios de specs já fechadas e verificadas**.
O C14 da spec 10 exige que cada tela seja visualmente idêntica ao protótipo; as
emendas 1, 6 e a remoção da contagem de cartas mudaram três telas por pedido
direto do dono.

Consequência: **rodar `verificar` na spec 10 hoje reprova — e está certa em
reprovar.** O próximo `codificar` que receber esse veredito vai desfazer o que o
dono pediu, com toda a razão do mundo, e ninguém vai entender por quê.

O verde autoatestado arrisca um defeito. A divergência não reconciliada faz o
método trabalhar **contra** a decisão de quem manda. É a falha mais cara das duas,
e é silenciosa: só aparece no ciclo seguinte.

## A proposta: quatro atribuições novas para `homologar`

`homologar` deixa de ser um ato terminal e passa a descrever o que de fato
acontece: **homologa → o dono valida ao vivo → emendas → fecha**. Nenhum passo
novo no ciclo; nenhuma cerimônia própria para uma mudança de dois minutos.

### 1. A emenda tem limite declarado

> **Emenda é a mudança cujo critério cabe em uma frase falsificável.** Se não
> cabe, não é emenda: é spec, e volta para `especificar`.

*"Tira o ×4 do nome no cinto"* cabe. *"Fecha todas as atividades e declara o
campeão"* não coube — e quem percebeu isso, no caso real, foi o próprio dono da
demanda, antes de quem conduzia. O limite precisa estar escrito para não depender
disso.

### 2. Toda emenda vira linha num registro, na hora

Sem registro, a homologação termina e ninguém sabe o que mudou depois da última
verificação. No caso real, as sete emendas existem apenas como histórico de
conversa — nenhum arquivo do repositório sabe que elas aconteceram.

O registro é o insumo das atribuições 3 e 4. Uma linha por emenda: o que mudou, o
critério em uma frase, e qual spec ela toca (se tocar).

### 3. Uma `verificar` para o LOTE de emendas, não uma por emenda

É o que evita a verbosidade que mataria a proposta. Custa **uma** sessão isolada
no fim da homologação, não uma por mudança de duas linhas, e ainda assim corta o
verde autoatestado.

Custo aceito, e ele é real: uma emenda ruim vive mais tempo, porque a verificação
só chega no fim. Em compensação o dono está validando ao vivo — o laço de
realimentação já é curto por outro caminho.

### 4. Reconciliação: toda emenda que toca critério existente resolve a divergência

Para cada emenda do registro que contradiz um critério de spec fechada, uma das
duas, e a escolha é do humano:

- **o critério é atualizado** para descrever o que o dono decidiu; ou
- **a divergência é registrada como aceita**, no veredito daquela spec, para o
  próximo ciclo não a tratar como defeito.

Sem isto, o método desfaz decisão do dono no ciclo seguinte, com razão formal e
resultado errado.

## O que esta proposta NÃO resolve

- **Não substitui a suíte.** Foi a suíte, e não o método, que segurou as
  regressões deste episódio. A atribuição 3 acrescenta julgamento independente;
  ela não acrescenta cobertura.
- **Não impede emenda errada.** Impede emenda errada **não medida**, que é outra
  coisa — e é a que sai cara.
- **Não decide quando parar de emendar.** Homologação com registro que nunca
  esvazia é sinal de que a spec estava errada, não de que as emendas são muitas.
  Detectar isso continua sendo leitura humana.

## Nota sobre o custo em tokens

O dono da demanda observou que o isolamento custa mais tokens e considerou o custo
aceitável. Registro a contrapartida honesta: **boa parte do que se gastou nas horas
de emenda foi gasto operando FORA do método**, não dentro dele — inclusive um
diagnóstico inteiro perseguindo um vazamento de ouro inexistente, que uma
verificação independente teria fechado em uma passada.
