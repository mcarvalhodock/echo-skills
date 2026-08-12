# Migração ECHO → SLE

Guia para repositórios que já tinham o ECHO instalado (skills `especificar`/`planejar`/`homologar`, pasta `.echo/`) e agora querem adotar o SLE (`designer`/`validator`/`executor`/`observer`, pasta `.sle/`, hooks e CI de enforcement).

Este documento existe porque a refatoração introduz mudanças estruturais que **não são compatíveis por acidente** — precisam ser feitas com intenção. Mas também não são bloqueantes: os dois métodos podem conviver em transição, e o downgrade de volta ao ECHO é sempre possível.

## Você usa ECHO ou SLE?

Verifique estes três sinais:

| Sinal | ECHO (v1) | SLE (v2) |
| --- | --- | --- |
| Manifesto no repositório | `.echo/manifesto.md` | `.sle/manifesto.md` (com `.echo/manifesto.md` opcionalmente como alias legado) |
| Skills instaladas | `especificar`, `planejar`, `homologar` (3) | `especificar`, `codificar`, `verificar`, `homologar` (4) |
| Enforcement de invariantes | Nenhum (probabilístico) | Sessão limpa por fase + workflows em `tooling/ci/` |

> **Nota v3.** Este guia foi escrito quando o SLE tinha cinco skills (`designer`, `validator`, `executor`, `observer`, `specifier`) e três hooks de enforcement de papel. A v3 removeu todos eles. A tabela acima já reflete o estado atual; o passo 3 abaixo virou histórico.

Se você tem qualquer sinal do ECHO, este guia é para você.

## Compatibilidade preservada

O SLE foi desenhado para não invalidar o que você já tem:

- **Specs escritas no formato ECHO continuam válidas.** O template do SLE (`template-especificacao.md`) é uma extensão do formato ECHO — as seções antigas seguem lá, novas seções (contrato arquitetural, artefatos de fidelidade, testes vinculados) são opcionais em N1 e obrigatórias em N2/N3.
- **`.echo/manifesto.md` continua sendo lido como fallback.** Se o repositório não tem `.sle/manifesto.md`, as skills consultam `.echo/`. Você pode migrar quando quiser.
- **Domínios do catálogo (`dominios.md`) não mudaram.** Só o vocabulário circundante — `manifesto ECHO` virou `manifesto SLE`, `skill echo` virou `skill sle`. A classificação por domínios é idêntica.
- **Pressão-catálogo (`.echo/pressao-catalogo.md`) continua sendo lida.** SLE introduz `.sle/pressao-metodo.md` como log adicional (pressão sobre o próprio método, não sobre o catálogo de domínios); os dois convivem.

## Ordem sugerida de migração

Você não precisa fazer tudo de uma vez. Faça na ordem abaixo — cada passo é independente e reversível:

### Passo 1 (baixo custo): instalar as skills novas em paralelo

```bash
cp -r designer validator executor observer ~/.claude/skills/
```

As skills antigas continuam instaladas — nada quebra. Você começa a usar as novas em tarefas onde faz sentido, gradualmente. Se preferir isolar por projeto, use `.claude/skills/` local em vez de global.

### Passo 2 (baixo custo): criar `.sle/manifesto.md` no repositório

Copie `.echo/manifesto.md` para `.sle/manifesto.md` e adicione os campos novos:

- `## Padrão de código local` — referência ao STYLE.md/linter do projeto (opcional; ausência degrada, não bloqueia)
- `## Paths de produção` — lista de padrões de path que o CI deve tratar como código de produção. Se não declarar, defaults (`src/`, `lib/`, `app/`, `internal/`, `pkg/`, `cmd/`) são usados.
- `## tdd-aplicavel` — `ortodoxo` (default), `parcial`, ou `manual`. Reflete honestamente o que a codebase suporta.
- `## CI templates ativos` — lista dos workflows ativados.

O `.echo/manifesto.md` original pode ficar como alias legado (adicione um cabeçalho apontando para `.sle/`) ou ser removido — as skills toleram os dois estados.

### Passo 3 — removido na v3: hooks in-session

**Não há hooks.** Os três hooks de enforcement de papel foram removidos: custaram mais do que protegiam, e a versão blindada por eles produziu um "verde ponta a ponta" com sete critérios não atendidos.

O que substitui: **cada fase roda em sessão limpa** — `codificar` não vê o raciocínio de `verificar`, e vice-versa. É isolamento de contexto, não de escrita: nada impede uma fase de tocar arquivo que não é dela. Se você quiser essa fronteira, ela é um hook seu, no seu harness, e não do método.

O passo 4 (CI) faz enforcement em nível de PR.

### Passo 4 (custo médio): habilitar CI workflows

Copie os arquivos de `tooling/ci/*.yml` para `.github/workflows/` (ou o equivalente no seu CI). Cada workflow chama um script Python em `tooling/ci/scripts/` — os scripts são portáveis para GitLab CI, CircleCI, Jenkins, mudando apenas o wrapper.

Antes de ativar em modo bloqueante:

1. Rode em modo warning (`continue-on-error: true` no GitHub Actions) por 1-2 sprints
2. Ajuste `## Paths de produção` no manifesto conforme os falsos-positivos aparecerem
3. Marque os critérios das specs existentes com `spec:<ID>` nos testes conforme o `criterion_coverage` reclamar

Só ative em bloqueante quando a suíte de específicações estiver 100% verde em modo warning.

### Passo 5 (custo alto — só quando tiver tempo): retro-conversão de specs

Specs antigas ECHO continuam válidas, mas você pode enriquecê-las com os campos novos do SLE:

- Marcar critérios com `# spec:A1` nos testes que os cobrem (para `criterion-coverage`)
- Em N2/N3, retro-preencher o contrato arquitetural (mesmo que seja documentando o que já foi implementado)

Isso é opcional e não bloqueia. Faça em specs que você precisa revisitar de qualquer forma.

## Downgrade — voltar ao ECHO

Se em qualquer momento o SLE mostrar-se overkill para o seu contexto, o caminho de volta é:

1. Remover ou deixar de invocar as skills SLE (`designer` etc.) — as skills antigas ECHO continuam instaladas e funcionais.
2. Deletar `.sle/` ou renomear para `.sle.bak/` — as skills antigas leem `.echo/manifesto.md` normalmente.
3. Desabilitar os hooks (remover do `.claude/settings.json` ou do `.git/hooks/`).
4. Desabilitar os workflows CI (remover de `.github/workflows/` ou marcar como `if: false`).

Nenhuma dessas operações destrói dado — todas são reversíveis.

## Mapeamento rápido de conceitos

| ECHO | SLE | Nota |
| --- | --- | --- |
| Especificar (Fase E) | Definir (Fase D) | Mesma coisa; renomeada para reservar "Especificar" ao macro-conceito |
| — | Desenhar (Fase D2) | Nova fase, só em N2/N3 (contrato arquitetural + protótipo N3) |
| Codificar / planejar (Fase C) | Traduzir + Implementar (Fases T + I) | Separação: Validator escreve testes primeiro, Executor implementa depois |
| Homologar (Fase H) | Homologar (Fase H) | Mesma; agora com plano manual estruturado quando TDD é parcial/manual |
| Observar (Fase O — manual) | Observar (Fase O — skill própria) | Ganhou skill `observer`, dois modos (event-driven / cadence-driven) |
| skill `especificar` | skill `designer` | Cobre Definir + Desenhar |
| skill `planejar` | skill `executor` (parte) + `validator` (parte) | O planejamento em si vira responsabilidade compartilhada — o Validator planeja os testes, o Executor planeja a implementação |
| skill `homologar` | skill `validator` (fase H) | Mesma pessoa que traduziu para testes valida o resultado — a invariante Executor ≠ Validator é preservada porque o Executor é outra skill |
| `.echo/manifesto.md` | `.sle/manifesto.md` | Fallback do `.echo/` preservado |
| `.echo/pressao-catalogo.md` | `.sle/pressao-catalogo.md` + `.sle/pressao-metodo.md` | Pressão sobre o catálogo (mesma coisa) + pressão sobre o método (novo) |

## FAQ

**Preciso migrar tudo agora?**

Não. Os cinco passos são independentes. Comece pelo passo 1 (instalar skills em paralelo) e vá adicionando o resto conforme fizer sentido no seu contexto.

**Vai quebrar minhas specs antigas?**

Não. Elas continuam válidas como estão. Enriquecimento com os campos novos do SLE é opcional (mas o CI `criterion-coverage` só reclama de specs SLE — as antigas ficam de fora).

**Posso usar as skills antigas e as novas juntas?**

Tecnicamente sim, mas não é recomendado — as invariantes do SLE só valem quando você usa as quatro skills novas de forma coerente. Rodar `especificar` (antiga) + `executor` (nova) confunde os hooks e degrada o enforcement.

**Qual é o esforço realista de migração de um repositório?**

Passos 1 e 2 (instalar skills + criar manifesto): 30 minutos. Passos 3 e 4 (hooks + CI): meio dia por harness/CI que você usa. Passo 5 (retro-conversão de specs): fica pronto sozinho conforme você revisita specs.

**Onde reportar problemas ou perguntas?**

Este repositório é experimento pessoal. Se você tem feedback e conhece o autor, converse. Se está descobrindo o método por fork, adapte livremente — não há canal formal de suporte.

---

*Este documento é vivo. Quando um passo de migração se mostrar difícil ou o mapeamento estiver errado, registre em `.sle/pressao-metodo.md` e volte aqui para refinar.*
