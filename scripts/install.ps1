<#
.SYNOPSIS
    Installs Spec Loop Engineering (SLE) - skills and CI - into a
    consumer repository.

.DESCRIPTION
    Idempotent installer for SLE components. Works with Windows PowerShell
    5.1+ and PowerShell Core 7+.

    With no arguments, runs in interactive mode (max 3 questions).
    With arguments, runs non-interactively.

    Argument parity with install.sh (Linux/macOS):

        PowerShell (this)              bash (install.sh)
        ------------------             ------------------
        -Components skills|ci|all --components skills|ci|all
        -Scope global|local            --scope global|local
        -TargetRepo <path>             --target-repo <path>
        -Force                         --force
        -DryRun                        --dry-run
        -Help                          --help

    Exit codes:
        0 = success
        1 = expected failure with clear message (Python missing, invalid target)
        2 = invocation error (unknown argument)
        3 = unexpected error

.EXAMPLE
    .\install.ps1
    Interactive mode - asks what to install.

.EXAMPLE
    .\install.ps1 -Components all -TargetRepo C:\my\project
    Installs everything (global skills + CI) into the given repo.

.EXAMPLE
    .\install.ps1 -Components skills -Scope local -TargetRepo C:\my\project -DryRun
    Simulates installing skills in local scope, no disk changes.

.NOTES
    Source: echo-skills repository. This script must run from within a clone
    of the source repository (validated by Confirm-SourceRoot).
    ASCII-only content: robust across Windows PS 5.1 (Windows-1252 default)
    and modern shells that default to UTF-8.
#>

[CmdletBinding()]
param(
    [ValidateSet('skills', 'ci', 'all')]
    [string[]]$Components,

    [ValidateSet('global', 'local')]
    [string]$Scope = 'global',

    [string]$TargetRepo,

    [switch]$Force,

    [switch]$DryRun,

    [switch]$Help
)

$ErrorActionPreference = 'Stop'

$Script:SLE_VERSION = '1.0.0'
$Script:SOURCE_ROOT = $null
$Script:PYTHON_AVAILABLE = $false
$Script:ARTIFACTS_CREATED = @()

function Write-Step {
    param([string]$Message, [string]$Kind = 'action')
    $prefix = switch ($Kind) {
        'action'  { '[ok]      ' }
        'dryrun'  { '[dry-run] ' }
        'skipped' { '[skip]    ' }
        'warn'    { '[warn]    ' }
        'error'   { '[error]   ' }
        default   { '[info]    ' }
    }
    Write-Host "$prefix$Message"
}

function Show-Help {
    $v = $Script:SLE_VERSION
    Write-Host "install.ps1 - Spec Loop Engineering (SLE) installer v$v"
    Write-Host ""
    Write-Host "USAGE:"
    Write-Host "    .\install.ps1                                    (interactive mode)"
    Write-Host "    .\install.ps1 -Components <list> [options]       (non-interactive)"
    Write-Host ""
    Write-Host "COMPONENTS:"
    Write-Host "    skills   Copy the 4 skills (especificar, codificar, verificar, homologar)"
    Write-Host "    ci       Copy workflows + CI scripts to the target repository"
    Write-Host "    all      skills + ci"
    Write-Host ""
    Write-Host "OPTIONS:"
    Write-Host "    -Components <list>   One or more components: skills, ci, all"
    Write-Host "    -Scope <value>       Skills scope: global (default, ~/.claude/skills/)"
    Write-Host "                         or local (<target>/.claude/skills/)"
    Write-Host "    -TargetRepo <path>   Target repository for CI (default: CWD)"
    Write-Host "    -Force               Overwrite existing artifacts without asking"
    Write-Host "    -DryRun              Simulate without touching disk"
    Write-Host "    -Help                Show this help"
    Write-Host ""
    Write-Host "EXIT CODES:"
    Write-Host "    0 success"
    Write-Host "    1 expected failure with clear message"
    Write-Host "    2 invocation error"
    Write-Host "    3 unexpected error"
    Write-Host ""
    Write-Host "Full docs: docs/specs/instaladores-sle.md in echo-skills."
}

function Test-PythonAvailable {
    try {
        $version = & python --version 2>&1
        if ($LASTEXITCODE -ne 0) { return $false }
        if ($version -match 'Python (\d+)\.(\d+)') {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            return ($major -gt 3 -or ($major -eq 3 -and $minor -ge 11))
        }
        return $false
    } catch {
        return $false
    }
}

function Read-InteractiveComponents {
    Write-Host ""
    Write-Host "SLE Installer - interactive mode"
    Write-Host "Choose what to install:"
    Write-Host "  1) skills only (the 5 SLE skills)"
    Write-Host "  2) skills + CI (recommended for first repository)"
    Write-Host "  3) skills + CI (full setup)"
    Write-Host "  4) ci only"
    $choice = Read-Host "Your choice [3]"
    if ([string]::IsNullOrWhiteSpace($choice)) { $choice = '3' }
    switch ($choice) {
        '1' { return ,@('skills') }
        '2' { return ,@('skills', 'ci') }
        '3' { return ,@('skills', 'ci') }
        '4' { return ,@('ci') }
        default {
            Write-Step "Invalid choice: '$choice'" 'error'
            exit 2
        }
    }
}

function Read-InteractiveScope {
    Write-Host ""
    Write-Host "Skills scope:"
    Write-Host "  1) global - ~/.claude/skills/ (available in all projects)"
    Write-Host "  2) local  - <target>/.claude/skills/ (only in this project)"
    $choice = Read-Host "Your choice [1]"
    if ([string]::IsNullOrWhiteSpace($choice)) { $choice = '1' }
    switch ($choice) {
        '1' { return 'global' }
        '2' { return 'local' }
        default {
            Write-Step "Invalid choice: '$choice'" 'error'
            exit 2
        }
    }
}

function Read-InteractiveTargetRepo {
    Write-Host ""
    $default = (Get-Location).Path
    $answer = Read-Host "Target repository for CI [$default]"
    if ([string]::IsNullOrWhiteSpace($answer)) { return $default }
    return $answer
}

function Resolve-Arguments {
    param([hashtable]$Ctx)

    $isInteractive = ($null -eq $Components) -or ($Components.Count -eq 0)

    if ($isInteractive) {
        $Ctx.Components = Read-InteractiveComponents
        $needsScope = 'skills' -in $Ctx.Components
        $needsTarget = 'ci' -in $Ctx.Components

        if ($needsScope) {
            $Ctx.Scope = Read-InteractiveScope
        } else {
            $Ctx.Scope = $Scope
        }

        if ($needsTarget) {
            $Ctx.TargetRepo = Read-InteractiveTargetRepo
        } else {
            if ($TargetRepo) { $Ctx.TargetRepo = $TargetRepo } else { $Ctx.TargetRepo = (Get-Location).Path }
        }
    } else {
        $expanded = @()
        foreach ($c in $Components) {
            if ($c -eq 'all') {
                $expanded += @('skills', 'ci')
            } else {
                $expanded += $c
            }
        }
        $Ctx.Components = @($expanded | Select-Object -Unique)
        $Ctx.Scope = $Scope
        if ($TargetRepo) { $Ctx.TargetRepo = $TargetRepo } else { $Ctx.TargetRepo = (Get-Location).Path }
    }

    $Ctx.Force = $Force.IsPresent
    $Ctx.DryRun = $DryRun.IsPresent
}

function Find-SourceRoot {
    $candidate = $PSScriptRoot
    if (-not $candidate) { $candidate = (Get-Location).Path }
    $current = (Resolve-Path $candidate).Path

    $requiredMarkers = @(
        'especificar\SKILL.md',
        'codificar\SKILL.md',
        'verificar\SKILL.md',
        'homologar\SKILL.md',
        'tooling\ci'
    )

    while ($true) {
        $allPresent = $true
        foreach ($marker in $requiredMarkers) {
            $full = Join-Path $current $marker
            if (-not (Test-Path $full)) {
                $allPresent = $false
                break
            }
        }
        if ($allPresent) { return $current }

        $parent = Split-Path -Parent $current
        if (-not $parent -or $parent -eq $current) { return $null }
        $current = $parent
    }
}

function Confirm-SourceRoot {
    $Script:SOURCE_ROOT = Find-SourceRoot
    if (-not $Script:SOURCE_ROOT) {
        Write-Step "SLE source artifacts not found." 'error'
        Write-Step "This script must run from within a clone of the 'echo-skills' repository." 'error'
        Write-Step "Clone the repository first and run the script from inside it." 'error'
        exit 1
    }
    Write-Step "SLE source detected: $Script:SOURCE_ROOT" 'info'
}

function Get-SkillsDestination {
    param([hashtable]$Ctx)
    if ($Ctx.Scope -eq 'global') {
        return (Join-Path $env:USERPROFILE '.claude\skills')
    }
    return (Join-Path $Ctx.TargetRepo '.claude\skills')
}

function Copy-SkillFolder {
    param(
        [string]$SkillName,
        [string]$SourceDir,
        [string]$DestRoot,
        [hashtable]$Ctx
    )
    $srcSkill = Join-Path $SourceDir $SkillName
    $dstSkill = Join-Path $DestRoot $SkillName

    if (-not (Test-Path $srcSkill)) {
        Write-Step "source skill missing: $srcSkill" 'error'
        return $false
    }

    if ((Test-Path $dstSkill) -and -not $Ctx.Force) {
        Write-Step "skill '$SkillName' already at $dstSkill (use -Force to overwrite)" 'skipped'
        return $true
    }

    if ($Ctx.DryRun) {
        Write-Step "would copy $srcSkill -> $dstSkill" 'dryrun'
        return $true
    }

    $staging = "$dstSkill.sle-staging"
    if (Test-Path $staging) {
        Remove-Item -Path $staging -Recurse -Force
    }

    New-Item -ItemType Directory -Path $DestRoot -Force | Out-Null
    Copy-Item -Path $srcSkill -Destination $staging -Recurse -Force

    if (Test-Path $dstSkill) {
        Remove-Item -Path $dstSkill -Recurse -Force
    }
    Move-Item -Path $staging -Destination $dstSkill

    Write-Step "installed skill '$SkillName' -> $dstSkill" 'action'
    $Script:ARTIFACTS_CREATED += $dstSkill
    return $true
}

function Install-Skills {
    param([hashtable]$Ctx)

    $destination = Get-SkillsDestination -Ctx $Ctx
    Write-Step "installing skills to: $destination (scope=$($Ctx.Scope))" 'info'

    $skills = @('especificar', 'codificar', 'verificar', 'homologar')
    foreach ($skill in $skills) {
        $ok = Copy-SkillFolder -SkillName $skill -SourceDir $Script:SOURCE_ROOT `
            -DestRoot $destination -Ctx $Ctx
        if (-not $ok) {
            Write-Step "failed to install skill '$skill' - aborting skills phase" 'error'
            exit 1
        }
    }
}

function ConvertTo-WarningModeYaml {
    param([string[]]$Lines)

    $out = New-Object System.Collections.Generic.List[string]
    $stepPattern = '^(\s+)-\s+(name|uses):'

    for ($i = 0; $i -lt $Lines.Count; $i++) {
        $line = $Lines[$i]
        $out.Add($line)

        if ($line -match $stepPattern) {
            $indent = $Matches[1]
            $insertion = "$indent  continue-on-error: true"

            $alreadyPresent = $false
            for ($j = $i + 1; $j -lt $Lines.Count; $j++) {
                $next = $Lines[$j]
                if ([string]::IsNullOrWhiteSpace($next)) { continue }
                if ($next -match '^\s*-\s') { break }
                if ($next.TrimStart() -notmatch '^-') {
                    $nextIndent = ($next -replace '\S.*$', '')
                    if ($nextIndent.Length -le $indent.Length) { break }
                    if ($next -match '^\s+continue-on-error\s*:\s*true') {
                        $alreadyPresent = $true
                        break
                    }
                }
            }

            if (-not $alreadyPresent) {
                $out.Add($insertion)
            }
        }
    }

    return $out.ToArray()
}

function Copy-TextFile {
    param(
        [string]$SourcePath,
        [string]$DestPath,
        [hashtable]$Ctx,
        [string[]]$TransformedContent
    )

    if ((Test-Path $DestPath) -and -not $Ctx.Force) {
        Write-Step "target file exists (skipped): $DestPath" 'skipped'
        return
    }

    if ($Ctx.DryRun) {
        Write-Step "would write $DestPath" 'dryrun'
        return
    }

    $parent = Split-Path -Parent $DestPath
    New-Item -ItemType Directory -Path $parent -Force | Out-Null

    $staging = "$DestPath.sle-staging"
    if ($TransformedContent) {
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllLines($staging, $TransformedContent, $utf8NoBom)
    } else {
        Copy-Item -Path $SourcePath -Destination $staging -Force
    }

    if (Test-Path $DestPath) {
        Remove-Item -Path $DestPath -Force
    }
    Move-Item -Path $staging -Destination $DestPath

    Write-Step "wrote $DestPath" 'action'
    $Script:ARTIFACTS_CREATED += $DestPath
}

function Copy-DirectoryTree {
    param(
        [string]$SourceDir,
        [string]$DestDir,
        [hashtable]$Ctx
    )

    if (-not (Test-Path $SourceDir)) {
        Write-Step "source directory missing: $SourceDir" 'error'
        return $false
    }

    if ((Test-Path $DestDir) -and -not $Ctx.Force) {
        Write-Step "directory exists (skipped): $DestDir" 'skipped'
        return $true
    }

    if ($Ctx.DryRun) {
        Write-Step "would copy tree $SourceDir -> $DestDir" 'dryrun'
        return $true
    }

    $staging = "$DestDir.sle-staging"
    if (Test-Path $staging) { Remove-Item -Path $staging -Recurse -Force }

    New-Item -ItemType Directory -Path (Split-Path -Parent $DestDir) -Force | Out-Null
    Copy-Item -Path $SourceDir -Destination $staging -Recurse -Force

    if (Test-Path $DestDir) { Remove-Item -Path $DestDir -Recurse -Force }
    Move-Item -Path $staging -Destination $DestDir

    Write-Step "installed tree $SourceDir -> $DestDir" 'action'
    $Script:ARTIFACTS_CREATED += $DestDir
    return $true
}

function New-ManifestoSkeleton {
    param([hashtable]$Ctx)

    $manifestoPath = Join-Path $Ctx.TargetRepo '.sle\manifesto.md'
    if (Test-Path $manifestoPath) {
        Write-Step "manifest already exists (preserved): $manifestoPath" 'skipped'
        return
    }

    $templatePath = Join-Path $Script:SOURCE_ROOT 'scripts\templates\manifesto-esqueleto.md'
    if (-not (Test-Path $templatePath)) {
        Write-Step "manifest template missing: $templatePath" 'error'
        return
    }

    if ($Ctx.DryRun) {
        Write-Step "would create $manifestoPath from skeleton" 'dryrun'
        return
    }

    $sleDir = Join-Path $Ctx.TargetRepo '.sle'
    New-Item -ItemType Directory -Path $sleDir -Force | Out-Null
    Copy-Item -Path $templatePath -Destination $manifestoPath -Force
    Write-Step "created $manifestoPath (fill <preencher: ...> placeholders)" 'action'
    $Script:ARTIFACTS_CREATED += $manifestoPath
}

function Install-Ci {
    param([hashtable]$Ctx)

    $sourceCi = Join-Path $Script:SOURCE_ROOT 'tooling\ci'
    $workflowsDir = Join-Path $Ctx.TargetRepo '.github\workflows'
    $targetCiDir = Join-Path $Ctx.TargetRepo 'tooling\ci'

    Write-Step "installing CI workflows to: $workflowsDir (warning mode by default)" 'info'

    $yamlFiles = Get-ChildItem -Path $sourceCi -Filter '*.yml' -File
    foreach ($yamlFile in $yamlFiles) {
        $destPath = Join-Path $workflowsDir $yamlFile.Name
        $lines = Get-Content -Path $yamlFile.FullName -Encoding UTF8
        $transformed = ConvertTo-WarningModeYaml -Lines $lines
        Copy-TextFile -SourcePath $yamlFile.FullName -DestPath $destPath `
            -Ctx $Ctx -TransformedContent $transformed
    }

    foreach ($subdir in @('scripts', 'tests')) {
        $srcSub = Join-Path $sourceCi $subdir
        $dstSub = Join-Path $targetCiDir $subdir
        Copy-DirectoryTree -SourceDir $srcSub -DestDir $dstSub -Ctx $Ctx | Out-Null
    }

    New-ManifestoSkeleton -Ctx $Ctx
}

function Add-GitignoreEntry {
    param([hashtable]$Ctx, [string]$Entry)

    $gitignorePath = Join-Path $Ctx.TargetRepo '.gitignore'

    if ((Test-Path $gitignorePath)) {
        $content = Get-Content -Path $gitignorePath -Encoding UTF8
        $normalized = $content | ForEach-Object { $_.Trim() }
        if ($normalized -contains $Entry) {
            Write-Step ".gitignore already contains '$Entry' (skipped)" 'skipped'
            return
        }
    } else {
        $content = @()
    }

    if ($Ctx.DryRun) {
        Write-Step "would add '$Entry' to $gitignorePath" 'dryrun'
        return
    }

    $updated = @()
    $updated += $content
    if ($content -and $content[-1].Trim() -ne '') {
        $updated += ''
    }
    $updated += "# SLE marker-file: role da sessao ativa (local, nao versionado)"
    $updated += $Entry

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllLines($gitignorePath, $updated, $utf8NoBom)
    Write-Step "added '$Entry' to $gitignorePath" 'action'
    $Script:ARTIFACTS_CREATED += $gitignorePath
}

function New-SetupGuide {
    param([hashtable]$Ctx)

    $templatePath = Join-Path $Script:SOURCE_ROOT 'scripts\templates\sle-setup.md.template'
    $destPath = Join-Path $Ctx.TargetRepo 'SLE-SETUP.md'

    if (-not (Test-Path $templatePath)) {
        Write-Step "setup template missing: $templatePath" 'error'
        return
    }

    if ((Test-Path $destPath) -and -not $Ctx.Force) {
        Write-Step "SLE-SETUP.md already exists (preserved): $destPath" 'skipped'
        return
    }

    if ($Ctx.DryRun) {
        Write-Step "would generate $destPath" 'dryrun'
        return
    }

    $template = Get-Content -Path $templatePath -Encoding UTF8 -Raw

    $installDate = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss zzz')
    $components = ($Ctx.Components -join ', ')
    $ciInstalled = if ('ci' -in $Ctx.Components) { 'yes' } else { 'no' }

    $artifactsList = ($Script:ARTIFACTS_CREATED | ForEach-Object { "- $_" }) -join "`n"
    if ([string]::IsNullOrWhiteSpace($artifactsList)) {
        $artifactsList = "- (none)"
    }
    $uninstallList = $artifactsList

    $rendered = $template `
        -replace '\{\{INSTALL_DATE\}\}', $installDate `
        -replace '\{\{TARGET_REPO\}\}', $Ctx.TargetRepo `
        -replace '\{\{COMPONENTS\}\}', $components `
        -replace '\{\{ARTIFACTS_LIST\}\}', $artifactsList `
        -replace '\{\{CI_INSTALLED\}\}', $ciInstalled `
        -replace '\{\{UNINSTALL_LIST\}\}', $uninstallList

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($destPath, $rendered, $utf8NoBom)
    Write-Step "generated $destPath" 'action'
    $Script:ARTIFACTS_CREATED += $destPath
}

function Write-Summary {
    param([hashtable]$Ctx)
    Write-Host ""
    Write-Host "---- Summary ----"
    Write-Host "Components: $($Ctx.Components -join ', ')"
    if ('skills' -in $Ctx.Components) {
        Write-Host "Skills scope: $($Ctx.Scope)"
    }
    if ('ci' -in $Ctx.Components) {
        Write-Host "Target repo: $($Ctx.TargetRepo)"
    }
    if ($Ctx.DryRun) {
        Write-Host "Mode: dry-run (nothing was modified)"
    } else {
        Write-Host "Mode: real execution"
        Write-Host "Artifacts created: $($Script:ARTIFACTS_CREATED.Count)"
    }
    Write-Host ""
    Write-Host "Next steps:"
    $step = 1

    if ('ci' -in $Ctx.Components) {
        Write-Host "  $step. Review $($Ctx.TargetRepo)\.sle\manifesto.md - replace <preencher: ...> placeholders."
        $step++
    }
    Write-Host "  $step. Start a demand with: /especificar"
    $step++
    if ('ci' -in $Ctx.Components) {
        Write-Host "  $step. Run 'pytest tooling/' in the target repo to confirm CI scripts pass."
        $step++
        Write-Host "  $step. After 1-2 sprints in warning mode, remove 'continue-on-error: true' from workflows."
        $step++
    }
    if ('skills' -in $Ctx.Components -and $Ctx.Components.Count -eq 1) {
        Write-Host "  $step. Skills installed. Read README.md and metodologia-sle.md at the source repo."
        $step++
    }
    Write-Host "-----------------"
}

function Invoke-Main {
    if ($Help.IsPresent) {
        Show-Help
        exit 0
    }

    $ctx = @{
        Components = @()
        Scope = $Scope
        TargetRepo = $null
        Force = $false
        DryRun = $false
    }

    Resolve-Arguments -Ctx $ctx
    Confirm-SourceRoot

    $Script:PYTHON_AVAILABLE = Test-PythonAvailable
    if (-not $Script:PYTHON_AVAILABLE -and ('ci' -in $ctx.Components)) {
        Write-Step "Python 3.11+ not found in PATH - the 'ci' component needs it." 'warn'
        Write-Step "Skills will proceed normally; ci will be disabled." 'warn'
    }

    if ('skills' -in $ctx.Components) {
        Install-Skills -Ctx $ctx
    }
    if (('ci' -in $ctx.Components) -and $Script:PYTHON_AVAILABLE) {
        Install-Ci -Ctx $ctx
    }
    # O guia de setup nasce sempre que algo foi para o repositório alvo.
    if ('ci' -in $ctx.Components) {
        New-SetupGuide -Ctx $ctx
    }

    Write-Summary -Ctx $ctx
    exit 0
}

try {
    Invoke-Main
} catch {
    Write-Step "Unexpected error: $($_.Exception.Message)" 'error'
    Write-Host $_.ScriptStackTrace
    exit 3
}
