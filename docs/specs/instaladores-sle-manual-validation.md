# Plano de validação manual — Instaladores SLE

> **Companion de** [`docs/specs/instaladores-sle.md`](./instaladores-sle.md). Este plano existe porque a spec declara `tdd-aplicavel: parcial` — parte dos critérios não é razoável de automatizar (interatividade real de terminal, integração com harnesses reais, execução em ambientes que a máquina local de desenvolvimento não tem).
>
> **Regra anti-fraude:** cada item abaixo tem ação concreta, evidência esperada e como anexar prova. Marcar um item como "verificado" sem anexar evidência é falseamento — reserve tempo real para executar cada bloco.

## Formato de cada item

```
- spec:AX (referência ao critério coberto)
  Ação: <passos concretos>
  Evidência esperada: <o que deve estar visível>
  Como anexar prova: <caminho do arquivo, print, log>
```

## Itens

### Modo interativo (A3)

- **spec:A3** — perguntas interativas de terminal

  Ação:
  1. Em terminal fresh (não IDE), rodar `.\scripts\install.ps1` (Windows) ou `./scripts/install.sh` (Linux/macOS) sem argumentos.
  2. Responder às 3 perguntas (o quê / escopo / target).
  3. Confirmar que o script prossegue com a escolha.

  Evidência esperada:
  - Prompt aparece com defaults entre `[colchetes]`.
  - Pressionar ENTER sem digitar usa o default.
  - Escolhas inválidas (`abc`) causam exit code 2 com mensagem clara.

  Como anexar prova:
  - Capturar terminal completo em `docs/specs/homologacao/instaladores-sle/interactive-<plataforma>.txt`.

### Integração real com harness (A6, complementar)

- **spec:A6** — hook integrado ao Claude Code

  Ação:
  1. Instalar SLE em um repositório real (`.\install.ps1 -Components all -Scope local -TargetRepo <path>`).
  2. Configurar `.claude/settings.json` com o snippet do `SLE-SETUP.md` gerado.
  3. Criar `.sle/.active-role` com `designer`.
  4. Iniciar sessão Claude Code no repositório.
  5. Pedir ao Claude: "escreva um arquivo `src/app.py`".

  Evidência esperada:
  - Hook `block-designer-writing-code` intercepta a tentativa de escrita.
  - Mensagem de bloqueio aparece no terminal do Claude Code.
  - `src/app.py` NÃO é criado.

  Como anexar prova:
  - Screenshot da sessão do Claude Code + `ls src/` mostrando que o arquivo não existe.
  - Anexar em `docs/specs/homologacao/instaladores-sle/hook-integration-claudecode.png`.

- **spec:A6** — mesmo teste com Cursor

  Análogo ao anterior, com `.cursor/hooks.json`. Anexar em `hook-integration-cursor.png`.

- **spec:A6** — fallback com git pre-commit

  Análogo, mas configurando `.git/hooks/pre-commit` (chmod +x no Linux/macOS). Testar com `git commit` real de arquivo em path de produção.

  Anexar em `hook-integration-precommit.txt`.

### Instalação global real (A4)

- **spec:A4** — skills em `~/.claude/skills/`

  Ação:
  1. Backup: `mv ~/.claude/skills ~/.claude/skills.bak` (se existir).
  2. Rodar `install.ps1 -Components skills -Scope global` (sem `-TargetRepo`, usa default).
  3. Verificar `Get-ChildItem ~/.claude/skills` (PS) ou `ls ~/.claude/skills/` (bash).
  4. Restaurar backup ao final.

  Evidência esperada:
  - 4 subpastas presentes: `designer/`, `validator/`, `executor/`, `observer/`.
  - Cada uma contém `SKILL.md`.

  Como anexar prova:
  - Output do `ls -R ~/.claude/skills/designer/` em arquivo.

### Comportamentos cross-platform que não dá para automatizar em uma só máquina

- **spec:A1 + C1** — paridade real Windows/Linux

  Ação:
  1. Em Windows, rodar `install.ps1 -Components all -TargetRepo C:\tmp\a`.
  2. Em Linux (ou WSL, ou macOS), rodar `install.sh --components all --target-repo /tmp/a`.
  3. Comparar as duas árvores geradas (`diff -r` recursivo).

  Evidência esperada:
  - Estrutura de diretórios idêntica.
  - Conteúdo dos workflows YAML idêntico (fora do path do template).
  - `SLE-SETUP.md` idêntico exceto pelo `{{INSTALL_DATE}}` e `{{TARGET_REPO}}`.

  Como anexar prova:
  - Output do `diff` em `crossplat-parity.txt`.

- **spec:C2** — dependência mínima (containers limpos)

  Ação:
  1. Container Linux limpo (só bash + Python 3.11+): rodar `install.sh --components all --target-repo /tmp/x --dry-run`.
  2. Container Windows limpo (só PS 5.1 + Python 3.11+): rodar `install.ps1 -Components all -TargetRepo C:\tmp\x -DryRun`.

  Evidência esperada:
  - Nenhum erro de dependência ausente.
  - `--dry-run` completa em <2 segundos em ambos.

  Como anexar prova:
  - Anexar Dockerfile mínimo usado + log do run em `containers/`.

### Compatibilidade de versão do shell (E4)

- **spec:E4** — PowerShell 5.1 (não 7+)

  Ação:
  1. Em máquina com apenas PS 5.1 (Windows nativo, sem PS Core), rodar o script.
  2. Alternativamente, forçar PS 5.1 via `powershell.exe -Version 5.1`.

  Evidência esperada:
  - Nenhum erro de sintaxe.
  - Todas as fases completam (skills + ci + hooks + summary).

  Como anexar prova:
  - Output completo do run em `ps51-compat.txt`.

- **spec:E4** — bash 4 (não 5)

  Ação análoga em ambiente com bash 4 (`bash --version`). Se não tem, rodar em macOS default (que ainda é bash 3.x em algumas versões — se falhar aqui, é bug legítimo a corrigir).

  Anexar em `bash4-compat.txt`.

### Comportamento "sem Python" (A9)

- **spec:A9** — Python ausente no PATH

  Ação:
  1. Em terminal fresh, temporariamente remover Python do PATH (`$env:PATH = ($env:PATH -split ';' | Where-Object { $_ -notmatch 'python' }) -join ';'` em PS, análogo em bash).
  2. Rodar `install.ps1 -Components ci -TargetRepo C:\tmp\test`.

  Evidência esperada:
  - Warning explícito: "Python 3.11+ not found in PATH".
  - Componente `ci` é pulado.
  - Se `--components skills ci` foi passado, skills instalam OK e ci é pulado com aviso.

  Como anexar prova:
  - Log do run em `python-missing.txt`.

## Trilha de auditoria consolidada

Ao concluir esta homologação, criar `docs/specs/homologacao/instaladores-sle/README.md` listando:

- Data e nome do homologador
- Cada item acima com status `passou` / `falhou` / `pulado` (justificar) / `bloqueado`
- Link para as evidências anexadas
- Bugs encontrados durante a validação manual → registrar em `.sle/pressao-metodo.md` como pressão do tipo "método → ajuste"

O log de homologação da spec inteira consolida os resultados automatizados (`pytest scripts/tests/`) com os manuais acima. Sem essa consolidação, a Fase H não é considerada concluída.

## Não fica pronto sem

- Pelo menos **um** teste de integração real com harness (spec:A6 com pelo menos Claude Code OU Cursor OU pre-commit).
- Pelo menos **um** teste em Linux/macOS real (não apenas WSL — o comportamento de path e `readarray` do bash 4 é sensível).
- Cross-platform parity (`diff -r` do output em ambas plataformas).

Sem esses três, a spec permanece em `homologação parcial` e não pode ser considerada entregue para uso em produção externa.
