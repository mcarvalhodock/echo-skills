# Plano: Instaladores automatizados do SLE

> Plano de implementação para a spec em [`docs/specs/instaladores-sle.md`](../specs/instaladores-sle.md). Ordem, dependências e mapeamento explícito para critérios de aceite (A1..A11) e cláusulas do contrato arquitetural (C1..C6).

## Premissas confirmadas

- CI é instalado em modo warning por default (`continue-on-error: true` injetado nos steps).
- Skills default: escopo global (`~/.claude/skills/`).
- Fora do clone: script aborta e instrui usuário a clonar o repositório primeiro.

## Estrutura de arquivos a criar

```
scripts/
├── install.ps1              # entry point Windows
├── install.sh               # entry point Linux/macOS
├── _lib/                    # partes compartilhadas conceituais (não código shared — cada script é autocontido, mas segue o mesmo layout mental)
├── templates/
│   ├── manifesto-esqueleto.md   # base para .sle/manifesto.md gerado
│   └── sle-setup.md.template    # base para SLE-SETUP.md gerado (com placeholders substituídos)
└── tests/
    ├── conftest.py
    ├── test_install_ps1.py
    └── test_install_sh.py

docs/specs/instaladores-sle-manual-validation.md   # plano de validação manual (v3: tdd=parcial)
```

## Passos ordenados

### Passo 1 — Templates compartilhados

Criar `scripts/templates/manifesto-esqueleto.md` e `scripts/templates/sle-setup.md.template` com placeholders para substituição.

**Cobre:** C6 (guia não é estático — placeholders para path, componentes, data).
**Depende de:** nada.
**Risco:** baixo. Só markdown.

### Passo 2 — Esqueleto dos scripts (funções nomeadas, sem lógica ainda)

Criar `install.ps1` e `install.sh` com as funções vazias que C3 exige: `parseArgs`, `detectSourceRoot`, `installSkills`, `installCi`, `installHooks`, `generateSetupGuide`, `printSummary`. Tabela de mapeamento de args no cabeçalho de cada arquivo (C1).

**Cobre:** C1 (paridade de args), C3 (funções nomeadas), parcial de A3 (help texto).
**Depende de:** nada.
**Risco:** baixo. Estrutura pura.

### Passo 3 — parseArgs + help + validações de invocação

Implementar `parseArgs` em ambos, com suporte a `--components`, `--scope`, `--target-repo`, `--force`, `--dry-run`, `--help`. Modo interativo quando nenhum argumento é passado (A3 — máximo 3 perguntas). Validação de argumentos inválidos → exit code 2 (C5).

**Cobre:** A3, A8 (parse do flag; efeito real vem depois), A9 (parcial — detecção de Python aqui), C5 (exit codes).
**Depende de:** Passo 2.
**Risco:** médio. Interatividade cross-platform pede cuidado (PowerShell `Read-Host` vs bash `read`).

### Passo 4 — detectSourceRoot + guard de E1

Função que encontra a raiz do clone `echo-skills` a partir do caminho do próprio script. Valida presença de artefatos esperados (`designer/SKILL.md`, `tooling/hooks/`, `tooling/ci/`). Se ausente, aborta com mensagem clara + URL do repo (E1).

**Cobre:** E1.
**Depende de:** Passo 2.
**Risco:** baixo. Path arithmetic simples.

### Passo 5 — installSkills

Copia `designer/`, `validator/`, `executor/`, `observer/` para o destino (global ou local conforme scope). Idempotência (A7): detecta destino existente, pula sem `--force`, sobrescreve com. Staging (C4): escreve em `<dest>.tmp` e move.

**Cobre:** A4, A7 (parcial), C4.
**Depende de:** Passos 3, 4.
**Risco:** médio. Cross-platform file copy (PowerShell `Copy-Item` vs `cp -r`) tem edge cases (permissões, symlinks, `.gitkeep`).

### Passo 6 — installCi

Copia workflows para `<target>/.github/workflows/` **injetando `continue-on-error: true` em cada step** (default warning-mode confirmado). Copia scripts e testes. Cria `<target>/.sle/manifesto.md` esqueleto se não existe (E6 preserva se existe).

**Cobre:** A5, A9 (Python check para ci), E6.
**Depende de:** Passos 3, 4, templates do Passo 1.
**Risco:** médio. Manipulação de YAML — para não introduzir dependência de parser YAML, injeta `continue-on-error` via regex simples nos `.yml` do próprio repo (que têm formato conhecido e controlado).

### Passo 7 — installHooks + generateSetupGuide

Copia `tooling/hooks/` (código + tests + READMEs) para o target. Adiciona `.sle/.active-role` ao `<target>/.gitignore` (cria se ausente, não duplica se presente — E5). Gera `<target>/SLE-SETUP.md` a partir do template com placeholders substituídos (path absoluto, componentes instalados, timestamp — C6).

**Cobre:** A6, A9 (Python check para hooks), E5, C6.
**Depende de:** Passos 3, 4, templates do Passo 1.
**Risco:** médio-baixo. `SLE-SETUP.md` tem instruções específicas por harness; conteúdo direto da conversa anterior.

### Passo 8 — printSummary

Bloco final com o que foi instalado, onde, e no máximo 5 próximos passos acionáveis.

**Cobre:** A10.
**Depende de:** todos os passos anteriores.
**Risco:** baixo.

### Passo 9 — Plano de validação manual (v3)

Como `tdd-aplicavel` desta tarefa é `parcial`, criar `docs/specs/instaladores-sle-manual-validation.md` com itens que não dão para automatizar bem: comportamento real do modo interativo em terminal, comportamento em `~/.claude/skills/` do usuário real, integração real com um harness (Claude Code se disponível).

**Cobre:** parte de A11 (o que os testes automatizados não cobrem).
**Depende de:** Passos 5-8 completos (para saber o que exatamente validar manualmente).
**Risco:** baixo.

### Passo 10 — Testes automatizados

Criar `scripts/tests/test_install_ps1.py` e `test_install_sh.py`. Testes obrigatórios:

- `--dry-run` para cada valor de `--components` produz output esperado
- Execução real em repo temporário cria os artefatos declarados
- Segunda execução (idempotência) não modifica o disco (verificar mtimes)
- `--force` sobrescreve
- Python ausente + `--components ci` → exit 1 com mensagem específica
- E5 (`.gitignore` já contém `.sle/.active-role`) → não duplica

Rodam apenas se `pwsh` (para test_install_ps1) e `bash` (para test_install_sh) estiverem no PATH — caso contrário, `pytest.skip` com motivo.

**Cobre:** A11 e parte de A7, A8, A9, E5.
**Depende de:** Passos 5-8.
**Risco:** médio. Testes cross-platform em Windows PowerShell + Linux bash de um mesmo pytest têm pegadas específicas.

### Passo 11 — Entrada em .sle/pressao-metodo.md

Registrar em `.sle/pressao-metodo.md` uma entrada tipo "método → ajuste" descrevendo:
- A lacuna "role sem produtor" identificada na Fase O da conversa anterior
- Mitigação parcial pelo instalador (E6, Estratégia B como default)
- O que ainda falta (fechamento completo exige wrapper de invocação — fora do v1)

**Cobre:** Observação da spec na seção "Observações para a Fase O".
**Depende de:** Passos 5-8 (só depois de o instalador estar entregue).
**Risco:** baixo. Só documentação.

## Cadência de commits sugerida

Cinco commits, agrupados por marco funcional:

1. **Passos 1-4** — templates + esqueleto + parseArgs + detectSourceRoot (fundação — dois scripts respondem `--help` e `--dry-run`)
2. **Passo 5** — installSkills (o componente mais isolado e verificável)
3. **Passo 6** — installCi (workflows + warning-mode + manifesto esqueleto)
4. **Passo 7 + 8** — installHooks + `.gitignore` + `SLE-SETUP.md` + printSummary
5. **Passos 9-11** — testes automatizados + validação manual + entrada em pressao-metodo

## Mapeamento crítico → passo

| Critério | Passos que o cobrem |
| --- | --- |
| A1, A2 (execução por plataforma) | 1-8 (todo o script) |
| A3 (modo interativo) | 3 |
| A4 (skills) | 5 |
| A5 (CI com warning) | 6 |
| A6 (hooks + marker + setup) | 7 |
| A7 (idempotência) | 5, 6, 7 (staging + detecção) |
| A8 (dry-run) | 3, 5, 6, 7 |
| A9 (degrada sem Python) | 3 (detecção), 6, 7 (uso) |
| A10 (resumo) | 8 |
| A11 (testes) | 10 |
| C1 (paridade args) | 2, 3 |
| C2 (zero deps externas) | design de todos os passos |
| C3 (funções nomeadas) | 2 |
| C4 (staging → commit) | 5, 6, 7 |
| C5 (exit codes) | 3 (parse), demais passos (retorno) |
| C6 (SLE-SETUP.md dinâmico) | 1, 7 |
| E1 (fora do clone) | 4 |
| E2 (destino existe) | 5 |
| E3 (target não é git) | 6, 7 (avisos) |
| E4 (PS 5.1) | design de todos os PowerShell |
| E5 (.gitignore já tem linha) | 7 |
| E6 (manifesto já existe) | 6 |
| E7 (root em Linux) | 5 (aviso) |

## Riscos identificados

- **R1**: PowerShell 5.1 tem sintaxe restrita — algumas construções que funcionam em 7+ falham em 5.1. Mitigação: rodar teste em ambas versões se disponíveis; documentar restrições no cabeçalho do `.ps1`.
- **R2**: Injeção de `continue-on-error` via regex nos `.yml` do `tooling/ci/` depende do formato ser estável. Mitigação: os workflows são versionados no próprio repo `echo-skills`, formato é controlado por nós. Se algum dia mudar, ajusta script e teste.
- **R3**: Testes automatizados cross-platform em pytest exigem invocar `pwsh` e `bash` como subprocess. Ambiente CI precisa ter os dois. Mitigação: usar `pytest.mark.skipif` para pular quando o shell alvo não está disponível — não falha, sinaliza.
- **R4**: Idempotência real (segunda execução não modifica mtime) exige lógica cuidadosa em `Copy-Item` (que por default atualiza mtime). Mitigação: comparar hash antes de copiar; se igual, pular.

## Reversibilidade

- Falha no meio: staging (C4) garante que nada meio-modificado é promovido.
- Instalação completa mas problemática: usuário deleta artefatos manualmente. Como não há uninstaller no v1, `SLE-SETUP.md` gerado inclui bloco "Como desinstalar" com os paths exatos que o instalador criou (para o usuário poder apagar).
- Reversão desta implementação: `git revert` do commit correspondente. Os arquivos criados fora do repo (skills globais) precisam ser deletados manualmente conforme o SETUP guide.
