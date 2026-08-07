# Spec: Instaladores automatizados do SLE (Windows + Linux)

> **Nível: 2 (Padrão).** Múltiplas decisões de trade-off, contrato arquitetural obrigatório, paridade entre duas plataformas. Não é N3 porque a superfície é bem delimitada (dois scripts com escopo idêntico).

## Intenção

Dois scripts idempotentes, um por plataforma (PowerShell/bash), que instalam skills SLE, workflows CI e hooks in-session num repositório consumidor com esforço mínimo e feedback claro em cada passo.

## Contexto

A refatoração ECHO → SLE entregou skills, hooks e CI, mas a instalação real em um repositório consumidor exige 8-12 comandos manuais em ordem específica — o que fricciona a adoção e cria margem para erro (esquecer o `.gitignore`, não criar `.sle/manifesto.md`, aplicar CI bloqueante direto). Além disso, na Fase O anterior identificamos a lacuna "role sem produtor" — o instalador é a oportunidade de fechar essa lacuna por default, configurando marker-file + `.gitignore` de saída, tornando a Estratégia B (marker-file lido pelos hooks) o caminho padrão do repositório consumidor.

## Critérios de aceite (BDD-flavored)

- [ ] **A1**: Dado um Windows com PowerShell 5.1+ ou Core 7+, quando o usuário executa `.\scripts\install.ps1 -Components all -TargetRepo <path>`, então as skills são copiadas para `~/.claude/skills/`, os artefatos CI para `.github/workflows/` e `tooling/ci/` do target, os hooks para `tooling/hooks/` do target, e o script imprime resumo do que foi feito.
- [ ] **A2**: Dado um Linux ou macOS com bash 4+, quando o usuário executa `./scripts/install.sh --components all --target-repo <path>`, então o resultado é semanticamente idêntico ao A1 (mesmos artefatos, mesmos caminhos, mesma sequência de mensagens).
- [ ] **A3**: Dado que nenhum argumento é passado, quando o usuário executa o script, então ele entra em modo interativo com **no máximo 3 perguntas**: (a) o que instalar (`skills`/`ci`/`hooks`/`all`), (b) escopo (`global`/`local`, só quando `skills` é selecionado), (c) repositório destino (só quando `ci`/`hooks` é selecionado, default = CWD).
- [ ] **A4**: Dado `--components skills` (ou equivalente PS), quando o script roda, então as pastas `designer/`, `validator/`, `executor/`, `observer/` são copiadas para `~/.claude/skills/` (se `--scope global`) ou `<target>/.claude/skills/` (se `--scope local`), e nenhum outro artefato é tocado.
- [ ] **A5**: Dado `--components ci`, quando o script roda, então (a) os 3 `.yml` de `tooling/ci/` vão para `<target>/.github/workflows/` **com `continue-on-error: true` injetado em todos os steps** (modo warning por default), (b) `tooling/ci/scripts/` e `tooling/ci/tests/` vão para `<target>/tooling/ci/`, (c) se `<target>/.sle/manifesto.md` não existe, é criado a partir de um esqueleto com `## Paths de produção`, `## tdd-aplicavel`, `## Domínios ativos` como placeholders.
- [ ] **A6**: Dado `--components hooks`, quando o script roda, então (a) `tooling/hooks/` (código, README e testes) é copiado para `<target>/tooling/hooks/`, (b) `.sle/.active-role` é adicionado ao `<target>/.gitignore` (criando o arquivo se não existir), (c) um `<target>/SLE-SETUP.md` é gerado com instruções concretas para criar o marker-file no início de cada sessão e para configurar `.claude/settings.json` / `.cursor/hooks.json`.
- [ ] **A7**: Dado que o script é executado duas vezes consecutivas com os mesmos argumentos e sem `--force`, quando o segundo run acontece, então nenhum artefato é sobrescrito, o script detecta os artefatos existentes, imprime "skipped: já existe" para cada um, e termina com exit code 0.
- [ ] **A8**: Dado `--dry-run` (ou `-DryRun`), quando o script roda, então **nenhum arquivo é criado, modificado ou removido**, mas o output lista exatamente o que seria feito.
- [ ] **A9**: Dado que Python 3.11+ não está disponível no PATH, quando o script tenta instalar `ci` ou `hooks`, então avisa claramente ("Python 3.11+ não encontrado — CI/hooks desabilitados"), segue instalando `skills` se solicitado, e retorna exit code diferente de 0 apenas se `ci`/`hooks` era o único componente pedido.
- [ ] **A10**: Dado que o script terminou com sucesso, quando o usuário lê o output final, então há um bloco "Próximos passos" com no máximo 5 itens acionáveis (declarar `Paths de produção` no manifesto, ativar CI bloqueante depois de sprint em warning, integrar hooks com o harness escolhido, etc.).
- [ ] **A11**: Dado que existe pelo menos 1 teste automatizado por script, quando os testes rodam num CI ou local, então eles verificam pelo menos: `--dry-run` produz output esperado com todos os componentes; execução real em repo temporário cria os artefatos declarados; segunda execução (idempotência) não modifica nada.

## Contrato arquitetural

- [ ] **C1**: Os dois scripts (PS + bash) **compartilham o mesmo modelo mental de argumentos** — cada flag em um tem correspondente direto no outro, com nomes idiomáticos da plataforma. Falsificação: existe uma tabela de mapeamento no cabeçalho de cada script, e um teste que verifica que `install.ps1 -Help` e `install.sh --help` produzem descrições paritárias dos componentes.
- [ ] **C2**: Cada script **não tem dependências externas** além do que já vem com a plataforma (PowerShell/bash) + Python 3.11+ opcional para componentes que dependem dele. Nada de `curl` para script remoto, `npm`, `pip install`, `apt install`. Falsificação: teste que roda o script num container/VM limpa (só PowerShell/bash + Python) e completa `--dry-run` sem erros.
- [ ] **C3**: O script é **estruturado em funções pequenas com responsabilidade única** — cada uma delas responsável por um verbo do fluxo (parseArgs, detectSourceRoot, installSkills, installCi, installHooks, generateSetupGuide, printSummary). Falsificação: teste que roda `Get-Command` (PS) ou `declare -F` (bash) e verifica presença dessas funções nomeadas.
- [ ] **C4**: Escrita em disco usa **padrão staging → commit** — cada operação primeiro escreve num caminho temporário, verifica sucesso, e só então move para o destino final. Isso protege contra estado inconsistente em caso de falha no meio. Falsificação: teste que simula falha (destino read-only) e verifica que o destino final não é criado nem modificado parcialmente.
- [ ] **C5**: O script **emite exit codes semânticos**: `0` sucesso; `1` falha esperada com mensagem clara (Python ausente pedindo componente que precisa, target-repo inválido); `2` erro de invocação (arg desconhecido); `3` erro inesperado com stack. Falsificação: teste-tabela mapeando cenário → exit code esperado.
- [ ] **C6**: O guia gerado em `SLE-SETUP.md` (A6) **não é template estático** — inclui o path absoluto do target repo, os componentes que foram instalados, os artefatos criados, e a data. Falsificação: geração do arquivo em dois targets diferentes produz dois arquivos com paths e listas diferentes.

## Casos de borda considerados

- **E1**: Script executado fora de um clone de `echo-skills` (usuário baixou só o `install.ps1` solto). → Script detecta ausência dos artefatos-fonte, informa que precisa rodar dentro de um clone do repositório, aponta URL. **Não** faz clone automático — clone remoto teria implicações de segurança e complexidade fora do escopo v1.
- **E2**: `<target>/.claude/skills/designer/` já existe. → Sem `--force`: pergunta em modo interativo, aborta em não-interativo com exit 1 e instrução clara. Com `--force`: substitui.
- **E3**: `<target>` não é git repository. → Skills instalam OK. CI/hooks avisam ("target não é git repo — workflows e hooks fazem menos sentido, mas prosseguindo"), continuam.
- **E4**: Windows sem PowerShell 7 (só 5.1). → Script funciona; evita sintaxe exclusiva de 7+ (`ForEach-Object -Parallel`, `??`, ternário `? :`).
- **E5**: `.gitignore` do target já contém `.sle/.active-role`. → Detecta linha existente, não duplica.
- **E6**: `.sle/manifesto.md` do target já existe. → Preserva; imprime aviso sugerindo revisão dos campos que o instalador teria preenchido.
- **E7**: Usuário roda o script como root em Linux (via `sudo`). → Aviso claro ("skills em `~/.claude/skills/` vão para `/root/.claude/skills/` — foi intencional?"), segue se confirmado.

## O que fica de fora

- Configuração automática de `.claude/settings.json` / `.cursor/hooks.json` — o formato varia por versão do harness. `SLE-SETUP.md` inclui exemplos, mas o usuário aplica manualmente.
- Wrapper de invocação (Estratégia C da conversa anterior) — fora do escopo v1.
- Publicação como pacote (`brew install`, `winget install`, npm, pip) — v2+.
- Uninstaller — v2+.
- Configuração automática de `.editorconfig` / `STYLE.md` / referências de linter no manifesto — usuário preenche `## Padrão de código local` manualmente.
- Suporte a shells alternativos (fish, zsh específico, cmd.exe puro) — bash e PowerShell cobrem >95% dos casos e ambos são de disponibilidade praticamente garantida nas plataformas-alvo.

## Restrições não-funcionais

- **Legibilidade acima de brevidade:** cada script pode ter até ~600 linhas se isso torna as funções mais claras.
- **Feedback contínuo:** cada operação produz uma linha de output com forma `[ação] artefato → destino` (ou `[ação] artefato → destino (skipped/dry-run/forced)`).
- **Failure atomicity:** falha no meio deixa o repositório num estado ou não-modificado (staging não foi promovido) ou completo (staging foi promovido). Nunca meio-modificado.
- **Idempotência real, não superficial:** segundo run com mesmos args produz o mesmo estado final que o primeiro. Verificado por teste.

## Domínios envolvidos

Consulta ao `.sle/manifesto.md`: domínios ativos deste repositório são `plataforma` e `integração`.

| item | classificação |
| --- | --- |
| A1, A2 (execução por plataforma) | `plataforma` |
| A3 (modo interativo) | `experiência` (inativo) → **miolo** |
| A4 (skills copiadas) | `plataforma` |
| A5 (CI copiado com warning) | `plataforma` + `integração` (interface com GitHub Actions) |
| A6 (hooks + marker + setup guide) | `plataforma` + `integração` (interface com harnesses) |
| A7, A8, A9 (idempotência, dry-run, degradação por dep faltando) | miolo |
| A10, A11 (output e testes) | miolo |
| C1..C6 | miolo |
| E1..E7 | miolo |

**Predominância:** miolo (regras do próprio instalador) + `plataforma`/`integração` (superfície). Não fatia por domínio — a tarefa é mono-domínio na prática (`plataforma` é onde tudo vive).

## Ambiente/destino

- Origem (o próprio repositório `echo-skills`): scripts vivem em `scripts/install.ps1` e `scripts/install.sh`. Testes em `scripts/tests/`.
- Destino padrão skills: `~/.claude/skills/` (Windows: `$env:USERPROFILE\.claude\skills\`; Linux/macOS: `$HOME/.claude/skills/`).
- Destino padrão CI/hooks: raiz do repositório-target (default CWD, override por `--target-repo`).

## `tdd-aplicavel` desta tarefa

**`parcial`.** Lógica de argumentos, idempotência, `--dry-run` e detecção de artefatos são automatizáveis (testes automatizados em pytest + shell test framework). Interatividade de prompts, comportamento real em `.claude/skills/` do usuário, e integração com harnesses reais pedem plano de validação manual — que será criado em `docs/specs/instaladores-sle-manual-validation.md` na Fase T.

## Testes vinculados

- `scripts/tests/test_install_ps1.py` (pytest + subprocess chamando pwsh)
- `scripts/tests/test_install_sh.py` (pytest + subprocess chamando bash)
- `docs/specs/instaladores-sle-manual-validation.md` (a criar na Fase T)

## Observações para a Fase O (Observar)

Esta spec **fecha parcialmente a lacuna "role sem produtor"** identificada na conversa anterior:

- Ao instalar hooks (A6), o instalador adiciona `.sle/.active-role` ao `.gitignore` e emite `SLE-SETUP.md` com instruções de como setar o marker-file no início de cada sessão. Isso torna a Estratégia B (marker-file) o padrão do repositório consumidor.
- Não fecha a lacuna completamente porque a criação do marker-file segue sendo instrução para o modelo (SETUP.md → primeira instrução da sessão). Fechamento completo exigiria um wrapper de invocação (fora do escopo v1).
- Após implementação, adicionar entrada em `.sle/pressao-metodo.md` do tipo "método → ajuste" descrevendo essa mitigação parcial.
