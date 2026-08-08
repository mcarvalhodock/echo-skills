# Hook: block-validator-writing-code

Enforça a **segunda invariante do SLE, na redação v5**: ninguém assina o que escreveu.

## O que mudou da v4 para a v5

A v4 dizia *"o Validator nunca escreve código de produção"*, e este hook bloqueava por path, sem exceção. O eixo estava errado: proibir **escrever** gerava cerimônia sem comprar segurança — recusar corrigir um bug de uma linha em nome da pureza de papel não protege ninguém, só devolve trabalho ao humano. O que sustenta o generator/evaluator separation é proibir **atestar**.

A v5 separa os dois atos, e o hook passa a enforçar a separação em vez do path:

| situação | v4 | v5 |
|---|---|---|
| Validator escreve em `src/` sem mais nada | bloqueado | **bloqueado** |
| Validator escreve em `src/` com emenda registrada | bloqueado | **permitido**, com lembrete |
| Validator escreve em `src/` com emenda **não** registrada | bloqueado | **bloqueado** |
| Validator escreve em `src/` na Fase Traduzir | bloqueado | **bloqueado**, incondicional |
| Validator escreve teste | permitido | permitido |

O que o hook consegue verificar é o **registro**; quem de fato assina é humano. Por isso a checagem é: existe, no log de pressão, uma linha que nomeie esta spec **e** a marque como atestação não-independente? Escrever é permitido; escrever calado não é.

## O que faz

Bloqueia operações de escrita/edição/deleção quando a skill ativa é `validator` e o caminho alvo bate com padrões de código de produção declarados no manifesto (ou padrões default) — **salvo emenda declarada e registrada**.

Permite sempre:

- Escrita em `tests/`, `test/`, `spec/`, `__tests__/` — testes automatizados (BDD, contrato arquitetural, fidelidade)
- Escrita em `docs/specs/*-log.md` — homologation log
- Escrita em `docs/specs/*-manual-validation.md` — plano de validação manual (v3: TDD parcial/manual)
- Escrita em `docs/specs/*-fidelidade.md` — testes de fidelidade (v2: N3)
- Escrita em `.sle/pressao-metodo.md` — pressão método
- Escrita em `.sle/pressao-catalogo.md` e `.echo/pressao-catalogo.md` — pressão catálogo (legado)

## Emenda: como declarar

Antes de invocar com `--emenda`, registre a dívida no log de pressão (`.sle/pressao-metodo.md`, ou `.echo/pressao-metodo.md` no alias legado), no formato da seção "Emenda" da skill `validator`:

```markdown
| data | spec | item | o que mudou | quem pediu | atestação |
|---|---|---|---|---|---|
| 2026-08-08 | spec-26 | @criterio:B1 | código | humano | não-independente |
```

O hook exige as duas coisas **na mesma linha**: o identificador da spec e a marca de não-independência. Uma emenda registrada para outra spec não autoriza esta, e uma linha que cita a spec sem admitir quem assina é menção, não declaração. O marcador vale com e sem acento.

## Invocação direta

```powershell
# Sem emenda: BLOQUEADO (exit 1)
python tooling/hooks/block-validator-writing-code/hook.py `
  --role validator `
  --path src/app.ts `
  --action edit
```

```powershell
# Com emenda registrada no log: PERMITIDO (exit 0)
python tooling/hooks/block-validator-writing-code/hook.py `
  --role validator `
  --path src/app.ts `
  --action edit `
  --emenda spec-26
```

```powershell
# Na Fase Traduzir nem emenda registrada libera: BLOQUEADO (exit 1)
# Nao ha codigo ainda, e implementar por conta propria destroi a suite
# que o Validator deveria estar derivando da spec.
python tooling/hooks/block-validator-writing-code/hook.py `
  --role validator `
  --path src/app.ts `
  --action edit `
  --emenda spec-26 `
  --fase traduzir
```

```powershell
python tooling/hooks/block-validator-writing-code/hook.py `
  --role validator `
  --path tests/app.test.ts `
  --action write

# Exit code 0: permitido
```

## Configuração no manifesto

Idem hook `block-designer-writing-code` — seção `Paths de produção` no `.sle/manifesto.md`.

## Ativação no harness

Idem hook `block-designer-writing-code` — registrar como `PreToolUse` (Claude Code) ou `beforeFileWrite` (Cursor) com a mesma estrutura. Fallback via pre-commit hook do git funciona igual.

## Testes

```powershell
pytest tooling/hooks/tests/test_block_validator.py -v
```

## Limitações conhecidas

1. **Detecção de identidade da skill ativa depende do harness.** Idem hook 1.
2. **Testes com nomes fora do convencional podem ser bloqueados.** Padrões default: `tests/`, `test/`, `spec/`, `__tests__/`. Repositórios com pasta de testes atípica precisam ajustar o hook (por enquanto, editar `ALLOWED_VALIDATOR_PATH_PATTERNS`; futuramente, ler do manifesto).
3. **Não distingue código embutido em arquivos permitidos.** Um `test.ts` que na prática exporta produção não é detectado — revisão humana continua responsável.
