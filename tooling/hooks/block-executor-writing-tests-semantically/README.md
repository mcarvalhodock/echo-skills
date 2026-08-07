# Hook: block-executor-writing-tests-semantically

Enforça o **ajuste v4 do SLE**: Executor pode fazer *refactor não-semântico* em testes (DRY, fixtures, renomeações internas), mas não pode alterar semântica (adicionar/remover casos de teste, mudar assertion).

## O que faz

Trabalha em dois passos porque a decisão só existe entre "antes" e "depois":

1. **`snapshot`** — antes da modificação, coleta assinatura semântica dos testes em uma pasta (nomes de testes + hash agregado das assertions por arquivo). Salva em JSON.
2. **`check`** — depois da modificação, re-coleta a assinatura, compara com o snapshot antigo e bloqueia se detectar mudança semântica quando `--role executor`.

A comparação usa heurística textual — extrai nomes de testes e assertions via regex por linguagem (Python/pytest, JS/TS Jest+Vitest, Go). Não roda a suíte real, porque o hook não conhece as dependências do repositório consumidor.

## Fluxo de invocação

```powershell
# Antes de editar tests/:
python tooling/hooks/block-executor-writing-tests-semantically/hook.py snapshot `
  --tests-dir tests/ `
  --output .sle-hook-snapshot.json

# ... executor edita arquivos em tests/ ...

# Depois:
python tooling/hooks/block-executor-writing-tests-semantically/hook.py check `
  --tests-dir tests/ `
  --snapshot .sle-hook-snapshot.json `
  --role executor
```

Exit codes do `check`:

- `0`: nenhuma mudança semântica detectada (refactor OK, ou role != executor)
- `1`: mudança semântica bloqueada
- `3`: snapshot inexistente ou corrompido

## Ativação no harness

### Claude Code

Requer dois hooks encadeados. Exemplo de configuração conceitual:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|MultiEdit|Write",
        "condition": "path_matches_tests",
        "hooks": [
          {
            "type": "command",
            "command": "python tooling/hooks/block-executor-writing-tests-semantically/hook.py snapshot --tests-dir tests/ --output .sle-hook-snapshot.json"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|MultiEdit|Write",
        "condition": "path_matches_tests",
        "hooks": [
          {
            "type": "command",
            "command": "python tooling/hooks/block-executor-writing-tests-semantically/hook.py check --tests-dir tests/ --snapshot .sle-hook-snapshot.json --role ${SLE_ACTIVE_ROLE}"
          }
        ]
      }
    ]
  }
}
```

`PreToolUse` e `PostToolUse` reais do Claude Code podem exigir sintaxe ligeiramente diferente. Confirme a versão do harness no repositório consumidor antes de habilitar.

### Cursor

Análogo — eventos `beforeFileWrite` (snapshot) e `afterFileWrite` (check) apontando para o mesmo comando.

### Fallback (pre-commit hook)

Não funciona bem como pre-commit puro porque snapshot precisa ser tirado ANTES da edição — a alternativa é comparar `HEAD` com index:

```bash
#!/usr/bin/env bash
role="${SLE_ACTIVE_ROLE:-}"
[ "$role" != "executor" ] && exit 0

git stash push --keep-index --include-untracked
python tooling/hooks/block-executor-writing-tests-semantically/hook.py snapshot \
  --tests-dir tests/ --output .sle-hook-snapshot.json
git stash pop
python tooling/hooks/block-executor-writing-tests-semantically/hook.py check \
  --tests-dir tests/ --snapshot .sle-hook-snapshot.json --role executor
```

## O que a heurística detecta

- **Adição de teste novo** (`test_foo` que não existia)
- **Remoção de teste** (`test_bar` sumiu)
- **Mudança em assertions** (hash agregado das assertions do arquivo diverge)
- **Arquivos de teste novos ou removidos**

## O que NÃO detecta

- Bugs sutis dentro de uma assertion que preservam contagem e hash (ex.: trocar `assert x == 1` por `assert y == 1` mantendo forma). Isso é limite fundamental de heurística textual sem execução da suíte.
- Refactor que mova assertions entre arquivos (contagem por arquivo muda; a heurística vai sinalizar mesmo sendo, na intenção, não-semântico). Nesse caso, humano avalia.
- Extensão para linguagens fora do trio Python/JS/TS/Go (Ruby, Java, Kotlin, etc.). Padrões default cobrem os casos mais comuns — outros pedem extensão de `TEST_NAME_PATTERNS` e `ASSERTION_PATTERNS`.

Falso-positivo (bloqueio quando não deveria) é preferível a falso-negativo (permitir alteração ilegal), dado o contexto do SLE.

## Testes

```powershell
pytest tooling/hooks/tests/test_block_executor.py -v
```
