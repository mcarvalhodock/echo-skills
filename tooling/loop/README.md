# O loop do SLE — guia prático

Sem o loop, você é o barramento de mensagens do método: cada fase termina, para, e você digita "OK, concordo". Isso é ratificação de transição, não julgamento — e era a maior parte das suas interações.

O loop ocupa esse posto. Ele lê **estrutura** (que fase terminou, o que o veredito classificou), decide a próxima transição por tabela fixa, e só devolve o controle nos pontos de julgamento real.

Ele é agnóstico ao **conteúdo**: não lê o código, não avalia a implementação, não opina sobre arquitetura. É um roteador, não um revisor. É por não julgar que ele pode rodar sozinho.

## Antes de rodar

Três coisas, e o loop recusa começar sem elas:

| requisito | por quê |
|---|---|
| o alvo está num **branch de trabalho**, não no default | o loop commita; `main` não é lugar para tentativa automática |
| a **subárvore do alvo está limpa** | o primeiro commit do loop varreria mudança sua junto, e ninguém separaria depois |
| as specs estão **escritas e aprovadas por você** | o loop parte de spec aprovada; ele não escreve spec |

Sujeira **fora** da subárvore do alvo não impede: num monorepo você roda em `packages/api` sem depender de `packages/web` estar limpo.

Spec com a seção `## Perguntas em aberto` preenchida entra em **quarentena** — não roda, e leva junto quem depende dela. As outras seguem.

## Instalação

O método precisa estar instalado onde o Claude Code enxergue; o loop, não. **O loop mora no clone do `echo-skills` e aponta para os alvos.** Um clone, N codebases.

```bash
# 1. as quatro skills, uma vez
./scripts/install.sh --components skills            # Linux/macOS
.\scripts\install.ps1 -Components skills            # Windows
```

Isso copia `especificar/`, `codificar/`, `verificar/` e `homologar/` para `~/.claude/skills/`. Use `--scope local --target-repo <path>` para instalar só num projeto.

```bash
# 2. opcional: enforcement de CI no repositório-alvo
./scripts/install.sh --components ci --target-repo /caminho/do/alvo
```

Copia os workflows para `<alvo>/.github/workflows/` em **modo warning** (`continue-on-error: true`) e cria `<alvo>/.sle/manifesto.md` a partir de um esqueleto, se não existir. Tire o warning quando parar de dar falso-positivo.

O loop em si não precisa de instalação: Python 3.10+, sem dependência externa. Rode a partir do clone.

## Como invocar

```bash
python tooling/loop/driver.py --alvo /caminho/do/projeto --specs cadastro,cobranca
```

| flag | o que faz |
|---|---|
| `--alvo` | o codebase. Todo caminho é relativo a ele, nunca ao clone do método |
| `--pedidos` | **segmento 1**: escreve uma spec por demanda e para no gate (default: `pedidos.md`) |
| `--specs` | **segmento 2**: nomes separados por vírgula, sem caminho e sem `.md` |
| `--seco` | mostra a próxima decisão e para. Não invoca, não registra, não commita |
| `--teto` | tentativas de `codificar` por spec antes de escalar (default: 3) |
| `--fusivel` | invocações no ciclo inteiro antes de escalar (default: 30) |
| `--comando` | como invocar o agente; `{prompt}` marca onde entra o texto (default: `claude -p {prompt}`) |

### Escrever as specs também

São **dois comandos, com você no meio** — e é essa a única parada obrigatória antes do código:

```bash
# 1. escreve uma spec por demanda e para
python tooling/loop/driver.py --alvo /projeto --pedidos

# 2. você lê, emenda o que precisar — e então:
python tooling/loop/driver.py --alvo /projeto --specs cadastro,cobranca
```

O `<alvo>/pedidos.md` tem um `##` por demanda, e **o cabeçalho é o nome da spec**, exatamente como está escrito:

```markdown
## cadastro

Cliente se cadastra com e-mail e senha. A senha tem regra mínima.

## cobranca-mensal

Cobrar todo mês, e avisar antes.
```

Cabeçalho que não serve como nome (`[a-z0-9-]+`) é **recusado nomeando o cabeçalho**, nunca corrigido — `## Cadastro de Clientes` para o loop em vez de virar `cadastro-de-clientes` sem você saber. Pedido cuja spec já existe é pulado, para não destruir trabalho seu já revisado.

O relatório do gate serve para **triar**, não só listar:

```
lote de specs escrito — revise antes de rodar o segundo comando
  cadastro: 2 critérios [miolo, plataforma]
  cobranca-mensal: 18 critérios [miolo] — acima do teto de 15 — bloqueada: Qual gateway?
```

**Não existe campo "aprovada" na spec**, e isso é deliberado: um campo desses é marcado sem ler. A aprovação é você rodar o segundo comando.

### Outro agente

O loop não fixa executável. Para o agente do Cursor, que importa as skills do Claude e aceita `-p`:

```bash
python tooling/loop/driver.py --alvo /caminho --specs cadastro --comando "agent -p {prompt}"
```

O `{prompt}` pode vir em qualquer posição — há agente que exige o texto antes das outras flags. Template sem o marcador, ou executável fora do PATH, é recusado **antes** da primeira invocação.

Duas coisas que valem saber antes do primeiro uso:

- **`agent` é um nome genérico.** Se houver outro executável com esse nome no seu PATH, o loop vai chamar o errado sem reclamar — ele só confere que existe. Na dúvida, passe o caminho completo no `--comando`.
- **O template é dividido por espaço em branco.** `agent -p {prompt}` funciona; um argumento que precise de espaço **dentro** dele não sobrevive à divisão.

### Monorepo

Aponte o `--alvo` para o pacote, não para a raiz. O loop resolve a subárvore sozinho e escopa nela a guarda, o commit e o diff que a leitura limpa recebe. `docs/specs/` e `.sle/` ficam dentro do pacote, e dois pacotes irmãos não se enxergam.

### Alvo sem git

Roda em **modo degradado**, avisando uma vez: sem commit por tentativa e sem diff. A leitura limpa passa a julgar o estado atual em vez do que mudou.

Isso ainda responde ao critério — critério é asserção sobre o fim, não sobre o que mudou. Mas você perde a diferença entre *"isto é verdade"* e *"isto passou a ser verdade"*: critério satisfeito por código anterior à demanda é lido como atendido.

**Comece sempre pelo `--seco`.** Ele confirma que as specs foram lidas, que o grafo de dependência fecha e que a primeira decisão é a que você espera:

```
modo seco — nada foi invocado, registrado ou commitado
próxima decisão: invocar:codificar
spec: cadastro
insumos: spec=.../docs/specs/cadastro.md alvo=... teto=3 fusível=30
```

## O que acontece a cada volta

```
codificar → verificar → (veredito) → codificar de novo, próxima spec, ou você
```

| situação | o loop faz |
|---|---|
| `codificar` terminou | invoca `verificar` |
| veredito todo `atendido`, e há spec pendente | invoca `codificar` na próxima |
| veredito todo `atendido`, e o lote acabou | para em `homologar` e mostra o relatório |
| veredito com `não atendido`, tentativas < teto | invoca `codificar` de novo |
| veredito com `não verificável` | **para e chama você** — é defeito de spec, e mais uma volta só queima tentativa |
| teto de tentativas estourado | **para e chama você**, com os vereditos produzidos |

Cada fase roda em **processo novo**, em sessão limpa. Retentativa também: retomar sessão traria o raciocínio da tentativa anterior junto, que é o que a sessão limpa existe para cortar.

O loop **não invoca `homologar`** — ele para ali. Homologar termina num gate humano de qualquer forma, e rodá-la sozinha produziria um checklist que ninguém leria na hora em que foi gerado.

## Onde ele para, e o que cada parada quer dizer

O motivo vem impresso. Ele é a primeira coisa a ler:

| motivo | o que aconteceu | o que fazer |
|---|---|---|
| `guarda-do-alvo` | branch default ou working tree sujo | limpe ou troque de branch; nada rodou |
| `defeito-de-spec` | algum critério ficou `não verificável` | o critério está mal escrito — emende a spec |
| `teto-de-tentativas` | N voltas e o critério continua vermelho | leia os vereditos: ou o código não faz, ou o critério pede errado |
| `fusivel` | o ciclo bateu o limite de invocações | **parada por recurso, não diagnóstico.** Nada foi concluído sobre convergência |
| `falha-de-invocacao` | a fase saiu com exit code ruim, ou não produziu o veredito | problema de execução, não de método |
| `dependencia-circular` | duas specs declaram depender uma da outra | conserte o `## Depende de` — provavelmente alguém escreveu a relação invertida |
| `lote-vazio` | todas as specs em quarentena | nada tinha insumo; `homologar` mediria o nada |

**A escalada nunca transcreve o veredito.** Ela dá o caminho do arquivo, e você lê lá. Repassado, o parecer amacia sem má intenção — e é por isso que ele vai para arquivo em primeiro lugar.

### Aviso que não trava

Se alguma das quatro skills instaladas divergir da do clone, o loop **avisa e segue**:

```
skill `codificar` instalada difere da do clone (C:\Users\voce\.claude\skills\codificar\SKILL.md)
```

A comparação é por conteúdo, não por data — data mente depois de um `git checkout`. Escopo local (`<alvo>/.claude/skills/`) tem precedência sobre o global, porque é ele que o agente usa. Não trava porque travar obrigaria a reinstalar a cada linha editada numa skill; mas se você viu esse aviso, o que rodou não foi o que está no clone.

## O que ele escreve no alvo

**`<alvo>/.sle/loop.jsonl`** — uma linha por decisão, append-only, campos fixos: instante, alvo, spec, transição, motivo, evidência, tentativa. Sem campo de texto livre, de propósito: um aqui reabriria a passagem que o método pagou caro para matar, e dessa vez ninguém estaria lendo.

É desse arquivo que sai a contagem de tentativas — não da memória do processo. Interromper o loop com `Ctrl+C` e rodar de novo **não repete tentativa já contada**.

**Um registro por ciclo.** Quando a execução anterior terminou (escalada ou lote encerrado), a próxima arquiva o registro em `loop-1.jsonl`, `loop-2.jsonl`, … e começa limpo. Quando foi interrompida no meio, continua no mesmo arquivo. É isso que impede uma spec emendada de nascer com o teto já esgotado pelas tentativas de semanas atrás.

**Um commit por tentativa de `codificar`**, com formato fixo:

```
loop(cadastro): codificar tentativa 2

SLE-Loop: cadastro#2
```

Tentativa que não muda arquivo nenhum não gera commit vazio. O loop nunca faz push, nunca faz amend, nunca reescreve commit.

## Limpar o histórico depois

O ciclo produz um commit por tentativa, **inclusive das que falharam**. É ruído esperado, e o trailer existe para você achá-lo:

```bash
git log --grep='^SLE-Loop:' --format='%h %s'
```

Daí é rebase interativo normal, juntando as tentativas de cada spec num commit só com mensagem sua. O loop não faz isso por você — reescrever histórico é decisão humana.

## Rodar os testes do loop

```bash
python -m pytest tooling/loop/tests -q
```

100 testes. Nenhum chama `claude`: o invocador é injetável e a suíte passa um falso. Teste que depende de LLM não é régua, é aposta. Os testes de git rodam em repositório temporário e não tocam este repositório.

## Como isso é portável

A decisão é **pura** — `roteador.py`, `lote.py`, `veredito.py`, `secoes.py` e `dependencia.py` não tocam disco, relógio, rede nem API de harness, e um teste varre o fonte deles atrás de import proibido.

Só `driver.py`, `invocacao.py`, `git_alvo.py` e `registro.py` conhecem o mundo. Trocar o Claude Code por outro harness é reescrever esses quatro; a tabela de transições não muda uma linha.
