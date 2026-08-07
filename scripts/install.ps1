<#
.SYNOPSIS
    Installs Spec Loop Engineering (SLE) - skills, CI and hooks - into a
    consumer repository.

.DESCRIPTION
    Idempotent installer for SLE components. Works with Windows PowerShell
    5.1+ and PowerShell Core 7+.

    With no arguments, runs in interactive mode (max 3 questions).
    With arguments, runs non-interactively.

    Argument parity with install.sh (Linux/macOS):

        PowerShell (this)              bash (install.sh)
        ------------------             ------------------
        -Components skills|ci|hooks|all --components skills|ci|hooks|all
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
    Installs everything (global skills + CI + hooks) into the given repo.

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
    [ValidateSet('skills', 'ci', 'hooks', 'all')]
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
    Write-Host "    skills   Copy the 4 skills (designer, validator, executor, observer)"
    Write-Host "    ci       Copy workflows + CI scripts to the target repository"
    Write-Host "    hooks    Copy in-session hooks to the target repository"
    Write-Host "    all      skills + ci + hooks"
    Write-Host ""
    Write-Host "OPTIONS:"
    Write-Host "    -Components <list>   One or more components: skills, ci, hooks, all"
    Write-Host "    -Scope <value>       Skills scope: global (default, ~/.claude/skills/)"
    Write-Host "                         or local (<target>/.claude/skills/)"
    Write-Host "    -TargetRepo <path>   Target repository for CI/hooks (default: CWD)"
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
    Write-Host "  1) skills only (the 4 SLE skills)"
    Write-Host "  2) skills + CI (recommended for first repository)"
    Write-Host "  3) skills + CI + hooks (full setup)"
    Write-Host "  4) ci only"
    Write-Host "  5) hooks only"
    $choice = Read-Host "Your choice [3]"
    if ([string]::IsNullOrWhiteSpace($choice)) { $choice = '3' }
    switch ($choice) {
        '1' { return ,@('skills') }
        '2' { return ,@('skills', 'ci') }
        '3' { return ,@('skills', 'ci', 'hooks') }
        '4' { return ,@('ci') }
        '5' { return ,@('hooks') }
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
    $answer = Read-Host "Target repository for CI/hooks [$default]"
    if ([string]::IsNullOrWhiteSpace($answer)) { return $default }
    return $answer
}

function Resolve-Arguments {
    param([hashtable]$Ctx)

    $isInteractive = ($null -eq $Components) -or ($Components.Count -eq 0)

    if ($isInteractive) {
        $Ctx.Components = Read-InteractiveComponents
        $needsScope = 'skills' -in $Ctx.Components
        $needsTarget = ('ci' -in $Ctx.Components) -or ('hooks' -in $Ctx.Components)

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
                $expanded += @('skills', 'ci', 'hooks')
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
        'designer\SKILL.md',
        'validator\SKILL.md',
        'executor\SKILL.md',
        'observer\SKILL.md',
        'tooling\hooks',
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

function Install-Skills {
    param([hashtable]$Ctx)
    Write-Step "installSkills: to be implemented in the next commit (Plan step 5)" 'warn'
    if ($Ctx.DryRun) {
        Write-Step "  - would copy designer/, validator/, executor/, observer/ to [$($Ctx.Scope)] destination" 'dryrun'
    }
}

function Install-Ci {
    param([hashtable]$Ctx)
    Write-Step "installCi: to be implemented in commit 3 (Plan step 6)" 'warn'
    if ($Ctx.DryRun) {
        Write-Step "  - would copy tooling/ci/*.yml to $($Ctx.TargetRepo)/.github/workflows/ (warning mode)" 'dryrun'
        Write-Step "  - would copy tooling/ci/scripts/ and tests/ to $($Ctx.TargetRepo)/tooling/ci/" 'dryrun'
        Write-Step "  - would create $($Ctx.TargetRepo)/.sle/manifesto.md from skeleton (if absent)" 'dryrun'
    }
}

function Install-Hooks {
    param([hashtable]$Ctx)
    Write-Step "installHooks: to be implemented in commit 4 (Plan steps 7-8)" 'warn'
    if ($Ctx.DryRun) {
        Write-Step "  - would copy tooling/hooks/ to $($Ctx.TargetRepo)/tooling/hooks/" 'dryrun'
        Write-Step "  - would add .sle/.active-role to .gitignore" 'dryrun'
        Write-Step "  - would generate SLE-SETUP.md in target" 'dryrun'
    }
}

function New-SetupGuide {
    param([hashtable]$Ctx)
    Write-Step "generateSetupGuide: to be implemented in commit 4 (Plan step 7)" 'warn'
}

function Write-Summary {
    param([hashtable]$Ctx)
    Write-Host ""
    Write-Host "---- Summary ----"
    Write-Host "Components: $($Ctx.Components -join ', ')"
    if ('skills' -in $Ctx.Components) {
        Write-Host "Skills scope: $($Ctx.Scope)"
    }
    if (('ci' -in $Ctx.Components) -or ('hooks' -in $Ctx.Components)) {
        Write-Host "Target repo: $($Ctx.TargetRepo)"
    }
    if ($Ctx.DryRun) {
        Write-Host "Mode: dry-run (nothing was modified)"
    } else {
        Write-Host "Mode: real execution"
    }
    Write-Host ""
    Write-Host "Next steps will be listed here after full implementation."
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
    if (-not $Script:PYTHON_AVAILABLE -and (('ci' -in $ctx.Components) -or ('hooks' -in $ctx.Components))) {
        Write-Step "Python 3.11+ not found in PATH - 'ci' and 'hooks' components need it." 'warn'
        Write-Step "Skills will proceed normally; ci/hooks will be disabled." 'warn'
    }

    if ('skills' -in $ctx.Components) {
        Install-Skills -Ctx $ctx
    }
    if (('ci' -in $ctx.Components) -and $Script:PYTHON_AVAILABLE) {
        Install-Ci -Ctx $ctx
    }
    if (('hooks' -in $ctx.Components) -and $Script:PYTHON_AVAILABLE) {
        Install-Hooks -Ctx $ctx
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
