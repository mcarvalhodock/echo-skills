# SLE — CI enforcement

Dois verificadores independentes, no nível do pipeline. Cada um é um script Python autocontido (`tooling/ci/scripts/`) invocado por um workflow GitHub Actions (`tooling/ci/*.yml`). O script é portável — GitLab CI, CircleCI, Jenkins ou pre-push local funcionam trocando só o wrapper.

## Componentes

### 1. `criterion_coverage.py` + `criterion-coverage.yml`

**Pergunta:** cada critério de aceite (`A1`, `C2`, `L3`, …) aparece em pelo menos um teste?

**Convenção:** o script lê os dois formatos que convivem no repositório —

```markdown
- **A1**: descrição                          (v2)
- [ ] **C1** `[miolo]` — descrição            (v3)
```

Testes marcam cobertura com o texto `spec:C1` em qualquer lugar do arquivo — comentário, nome de teste, tag:

```python
def test_criterio_c1_valida_input():
    # spec:C1
    ...
```

Para itens não-automatizáveis (TDD parcial ou manual), a marca aparece em `<spec>-manual-validation.md`:

```markdown
- **spec:A1** — verificado manualmente na tela X clicando em Y.
```

**Não são specs** e ficam de fora da varredura: `*-log.md`, `*-fidelidade.md`, `*-manual-validation.md` e `*-veredito.md` (inclusive `-veredito-1.md`, `-2.md`, …). O veredito lista os mesmos identificadores em bullets; lido como spec, exigiria teste para os critérios sobre os quais ele já é o parecer.

### 2. `pr_spec_diff.py` + `pr-spec-diff.yml`

**Pergunta:** alteração em código de produção veio acompanhada de alteração em spec?

Falha o PR se algum arquivo em paths de produção (declarados em `.sle/manifesto.md`, seção `## Paths de produção`, ou defaults `src/`, `lib/`, `app/`, `internal/`, `pkg/`, `cmd/`) foi tocado sem que nenhum arquivo em `docs/specs/` tenha mudado no mesmo PR.

## O que foi aposentado

**`spec_test_parity`** — exigia que a spec declarasse uma seção `## Testes vinculados`. O formato v3 não tem essa seção, e o vínculo critério↔teste já é feito pelo marcador `spec:<ID>`, que é mais forte: ele amarra por critério, não por arquivo. Mantê-lo exigiria inchar o formato da spec para sustentar a checagem mais fraca das duas.

## Ativação em outros CIs

```yaml
# GitLab CI
sle-criterion-coverage:
  image: python:3.11
  script:
    - python tooling/ci/scripts/criterion_coverage.py
```

```bash
# pre-push local
#!/usr/bin/env bash
python tooling/ci/scripts/criterion_coverage.py || exit 1
```

## Testes

```powershell
pytest tooling/ci/tests/ -v
```

15 testes cobrem: extração de critérios nos dois formatos, cobertura completa e parcial, exclusão de veredito, classificação de paths, três cenários de PR diff e o pacote do plugin do Cursor como path de produção deste repositório.

## Limitações conhecidas

1. **Convenções textuais.** O enforcement depende de o consumidor seguir as convenções — marcador `spec:<ID>`, sufixos de arquivo. Repositório que as ignora passa nos checkers sem estar em conformidade real. Foi assim que o padrão v2 sobreviveu à v3 lendo zero critérios e reportando sucesso: **zero critérios lidos vira zero critérios sem cobertura.** Se você mudar o formato da spec, este script é o primeiro lugar a conferir.
2. **`pr_spec_diff` depende de `git diff` funcional.** Requer histórico do base ref no ambiente CI (`fetch-depth: 0` no checkout).
3. **`criterion_coverage` não verifica se o teste realmente valida o critério.** Só que o marcador existe. É decisão consciente: verificação profunda é a leitura limpa de `verificar`, e julgamento é humano em `homologar`.
