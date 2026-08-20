# plugin-cursor — validação manual

Dois critérios de `docs/specs/plugin-cursor.md` só existem depois que o Cursor
carrega o pacote e desenha o painel. Nenhum teste deste repositório vê esse
painel, e é por isso que eles entram aqui em vez de virarem asserção.

## Como o pacote foi carregado

Junção de diretório apontando `~/.cursor/plugins/local/sle` para a raiz do
repositório — e não cópia, porque a spec exige fonte única e uma cópia em
`~/.cursor/` seria a segunda cópia dos seis `SKILL.md`.

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.cursor\plugins\local\sle" `
         -Target "C:\dock-codes\echo-skills"
```

Depois disso, `~/.cursor/plugins/local/sle/.cursor-plugin/plugin.json` existe e
é legível pelo processo do Cursor.

## Como observar

1. Recarregar o Cursor (**Developer: Reload Window**, ou reabrir o app): a
   varredura de `plugins/local` acontece no load, não por watch.
2. Abrir **Customize** na barra lateral.
3. **Skills** para M14, **Agents** para M15.

Evidência de apoio, em `%APPDATA%\Cursor\logs\<sessão>\window*\exthost\anysphere.cursor-agent-exec\Cursor Plugins.log`:
a linha `loadAllPlugins completed ... (claude=true, userLocal=<bool>, ... total=<n> plugins ...)`.
Com o pacote carregado, `userLocal` passa a `true` e `total` cresce em 1. Antes
do reload ela ainda diz `userLocal=false, total=0` — é o estado de quem nunca
teve plugin local, não uma reprovação.

## Critérios

- **spec:M14** — as seis skills (`especificar`, `codificar`, `verificar`,
  `homologar`, `orquestrar`, `prototipar-frontend`) aparecem em
  **Customize → Skills** vindas do plugin `sle`.
  **Estado: pendente de observação humana.** O carregamento foi feito; o
  painel, não foi visto. Seis presentes aprova; menos que seis reprova — e
  reprovar aqui é o resultado da medição que a spec pediu, não licença para
  mover as pastas.

- **spec:M15** — as três definições de agente (`sle-codificar`,
  `sle-verificar`, `sle-homologar`) aparecem em **Customize → Agents** vindas
  do plugin `sle`.
  **Estado: pendente de observação humana.** Mesmo raciocínio de M14: três
  presentes aprova, menos que três reprova.
