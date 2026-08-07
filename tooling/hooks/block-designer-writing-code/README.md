# Hook: block-designer-writing-code

Enforça a **primeira invariante do SLE**: Designer ≠ Executor.

## O que faz

Bloqueia operações de escrita/edição/deleção quando a skill ativa é `designer` e o caminho alvo bate com padrões de código de produção declarados no manifesto (ou padrões default: `src/`, `lib/`, `app/`, `internal/`, `pkg/`, `cmd/`).

Permite:

- Escrita em `docs/specs/` (spec, contrato arquitetural, artefatos de fidelidade)
- Escrita em `docs/plans/` (plano de implementação)
- Escrita em `.sle/` (manifesto, pressão-método) e `.echo/` (legado)
- Protótipos em N3 dentro de `docs/specs/<nome-tarefa>-prototipo/` (subpath permitido)

## Invocação direta

```powershell
python tooling/hooks/block-designer-writing-code/hook.py `
  --role designer `
  --path src/app.ts `
  --action write

# Exit code 1: BLOQUEADO
```

```powershell
python tooling/hooks/block-designer-writing-code/hook.py `
  --role designer `
  --path docs/specs/nova-feature.md `
  --action write

# Exit code 0: permitido
```

## Configuração no manifesto

Se o repositório consumidor declara `Paths de produção` em `.sle/manifesto.md`, esses padrões substituem os defaults:

```markdown
## Paths de produção

- `frontend/src/`
- `backend/app/`
- `packages/*/src/`
```

Padrões são regex ancorados no início. Ausência da seção → defaults são usados.

## Ativação no harness

O contrato do hook é agnóstico: entra por args de CLI, sai por exit code + stdout. Cada harness precisa de um adaptador fino.

### Claude Code (`~/.claude/settings.json` ou `.claude/settings.json`)

Registrar como `PreToolUse` para ferramentas de escrita (`Write`, `Edit`, `MultiEdit`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python tooling/hooks/block-designer-writing-code/hook.py --role ${SLE_ACTIVE_ROLE} --path ${TOOL_INPUT_FILE_PATH} --action write --project-root ${CLAUDE_PROJECT_DIR}"
          }
        ]
      }
    ]
  }
}
```

`SLE_ACTIVE_ROLE` é uma variável de ambiente exportada ao invocar a skill (por convenção do repositório consumidor). O harness precisa expor o caminho do arquivo alvo via variável — o nome exato depende da versão do Claude Code.

### Cursor (`.cursor/hooks.json`)

Formato análogo — mapear evento `beforeFileWrite` para o mesmo comando. Confirme sintaxe corrente do Cursor no repositório consumidor antes de habilitar.

### Fallback (harness sem hooks reais)

Rodar como pre-commit hook do git (`.git/hooks/pre-commit`) inspecionando arquivos staged:

```bash
#!/usr/bin/env bash
role="${SLE_ACTIVE_ROLE:-}"
[ -z "$role" ] && exit 0
for f in $(git diff --cached --name-only --diff-filter=ACM); do
  python tooling/hooks/block-designer-writing-code/hook.py \
    --role "$role" --path "$f" --action write || exit 1
done
```

## Testes

Ver `tooling/hooks/tests/test_block_designer.py`. Rodar com:

```powershell
pytest tooling/hooks/tests/test_block_designer.py -v
```

## Limitações conhecidas

1. **Detecção de identidade da skill ativa depende do harness.** O hook confia no valor de `--role` — falsificar isso derrota a proteção. Enforcement completo exige que o harness controle essa variável.
2. **Padrões de path são heurísticos.** Repositórios com layout atípico precisam declarar `Paths de produção` no manifesto.
3. **Não detecta código embutido em arquivos permitidos** (ex.: bloco de código de produção dentro de spec em Markdown). Isso é responsabilidade do Validator/humano na revisão.
