# SLE — Hooks de enforcement

Três hooks determinísticos que enforçam as invariantes de separação de papéis do SLE no momento em que agentes tentam violá-las (antes do commit, dentro da sessão do agente). Complementam os workflows de CI em `tooling/ci/`, que operam no nível do repositório.

## Hooks disponíveis

| Hook | Invariante | Ação |
| --- | --- | --- |
| [`block-designer-writing-code`](./block-designer-writing-code/) | Designer ≠ Executor | Bloqueia Designer escrevendo código de produção |
| [`block-validator-writing-code`](./block-validator-writing-code/) | Executor ≠ Validator | Bloqueia Validator escrevendo código de produção |
| [`block-executor-writing-tests-semantically`](./block-executor-writing-tests-semantically/) | Executor pode refactor não-semântico em testes; não pode alterar semântica (v4) | Detecta mudança semântica via snapshot antes/depois |

Cada hook tem seu próprio `README.md` explicando invocação e ativação.

## Testes

```powershell
pytest tooling/hooks/tests/ -v
```

35 testes cobrem os dois cenários exigidos pelo passo 11 do plano de refatoração: bloqueio efetivo em cada invariante e não-interferência nas operações permitidas.

## Estratégia de invocação

Os hooks são **scripts CLI autocontidos** (Python 3.11+, sem dependências além da stdlib). O contrato é uniforme:

- **Input:** argumentos de linha de comando (`--role`, `--path`, `--action`, etc.).
- **Output:** exit code (0 = permitido, 1 = bloqueado, 2/3 = erro) + mensagem em stdout.

Isso permite plugar em qualquer harness que suporte executar comandos externos em ganchos do ciclo de vida:

- **Claude Code:** `PreToolUse` / `PostToolUse` em `.claude/settings.json`
- **Cursor:** `beforeFileWrite` / `afterFileWrite` em `.cursor/hooks.json`
- **Git puro:** `.git/hooks/pre-commit`
- **CI:** invocação direta em pipeline

Cada `README.md` de hook detalha a receita para cada harness.

## Limitações estruturais

Ver `docs/specs/refatoracao-para-spec-loop-engineering.md` — edge case E1 (harness sem hooks reais → CI compensa parcialmente) e risco R1 do plano (granularidade de hooks do harness em 2026 é incerta).

Os hooks assumem que a **identidade da skill ativa** (variável `--role`) é fornecida honestamente pelo harness. Se um humano ou agente pode falsificar essa variável, o enforcement se degrada para uma checagem probabilística e a segunda camada (CI) passa a ser o único enforcement duro.
