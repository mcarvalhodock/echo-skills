#!/usr/bin/env bash
#
# install.sh - Spec Loop Engineering (SLE) installer for Linux/macOS.
#
# Idempotent, no external dependencies beyond bash 4+ and (optionally)
# Python 3.11+. Semantically mirrors scripts/install.ps1.
#
# Argument parity:
#
#     bash (this)                       PowerShell (install.ps1)
#     --------------                    -------------------------
#     --components skills|ci|hooks|all  -Components skills|ci|hooks|all
#     --scope global|local              -Scope global|local
#     --target-repo <path>              -TargetRepo <path>
#     --force                           -Force
#     --dry-run                         -DryRun
#     --help                            -Help
#
# Exit codes:
#     0 success
#     1 expected failure with clear message
#     2 invocation error
#     3 unexpected error
#
# Usage:
#     ./install.sh                                    (interactive mode)
#     ./install.sh --components all --target-repo /path
#     ./install.sh --components skills --scope local --target-repo /path --dry-run
#
# This script must run from within a clone of the 'echo-skills' repository
# (validated by confirm_source_root).
#
# ASCII-only content: safe across shells with different default encodings.

set -euo pipefail

readonly SLE_VERSION='1.0.0'

SOURCE_ROOT=''
PYTHON_AVAILABLE='false'
ARTIFACTS_CREATED=()

ARG_COMPONENTS=()
ARG_SCOPE='global'
ARG_TARGET_REPO=''
ARG_FORCE='false'
ARG_DRY_RUN='false'
ARG_HELP='false'

write_step() {
    local kind="${1}"; shift
    local msg="$*"
    local prefix
    case "$kind" in
        action)  prefix='[ok]      ' ;;
        dryrun)  prefix='[dry-run] ' ;;
        skipped) prefix='[skip]    ' ;;
        warn)    prefix='[warn]    ' ;;
        error)   prefix='[error]   ' ;;
        *)       prefix='[info]    ' ;;
    esac
    printf '%s%s\n' "$prefix" "$msg"
}

show_help() {
    cat <<EOF
install.sh - Spec Loop Engineering (SLE) installer v${SLE_VERSION}

USAGE:
    ./install.sh                                     (interactive mode)
    ./install.sh --components <list> [options]       (non-interactive)

COMPONENTS:
    skills   Copy the 4 skills (designer, validator, executor, observer)
    ci       Copy workflows + CI scripts to the target repository
    hooks    Copy in-session hooks to the target repository
    all      skills + ci + hooks

OPTIONS:
    --components <list>    Comma-separated list: skills,ci,hooks,all
    --scope <value>        Skills scope: global (default, ~/.claude/skills/)
                           or local (<target>/.claude/skills/)
    --target-repo <path>   Target repository for CI/hooks (default: CWD)
    --force                Overwrite existing artifacts without asking
    --dry-run              Simulate without touching disk
    --help                 Show this help

EXIT CODES:
    0 success
    1 expected failure with clear message
    2 invocation error
    3 unexpected error

Full docs: docs/specs/instaladores-sle.md in echo-skills.
EOF
}

test_python_available() {
    local py_bin=''
    if command -v python3 >/dev/null 2>&1; then
        py_bin='python3'
    elif command -v python >/dev/null 2>&1; then
        py_bin='python'
    else
        return 1
    fi
    local version_output
    version_output=$("$py_bin" --version 2>&1) || return 1
    if [[ ! "$version_output" =~ Python\ ([0-9]+)\.([0-9]+) ]]; then
        return 1
    fi
    local major="${BASH_REMATCH[1]}"
    local minor="${BASH_REMATCH[2]}"
    if (( major > 3 )) || { (( major == 3 )) && (( minor >= 11 )); }; then
        return 0
    fi
    return 1
}

read_interactive_components() {
    echo ""
    echo "SLE Installer - interactive mode"
    echo "Choose what to install:"
    echo "  1) skills only (the 4 SLE skills)"
    echo "  2) skills + CI (recommended for first repository)"
    echo "  3) skills + CI + hooks (full setup)"
    echo "  4) ci only"
    echo "  5) hooks only"
    read -r -p "Your choice [3]: " choice
    choice="${choice:-3}"
    case "$choice" in
        1) ARG_COMPONENTS=(skills) ;;
        2) ARG_COMPONENTS=(skills ci) ;;
        3) ARG_COMPONENTS=(skills ci hooks) ;;
        4) ARG_COMPONENTS=(ci) ;;
        5) ARG_COMPONENTS=(hooks) ;;
        *)
            write_step error "Invalid choice: '$choice'"
            exit 2
            ;;
    esac
}

read_interactive_scope() {
    echo ""
    echo "Skills scope:"
    echo "  1) global - ~/.claude/skills/ (available in all projects)"
    echo "  2) local  - <target>/.claude/skills/ (only in this project)"
    read -r -p "Your choice [1]: " choice
    choice="${choice:-1}"
    case "$choice" in
        1) ARG_SCOPE='global' ;;
        2) ARG_SCOPE='local' ;;
        *)
            write_step error "Invalid choice: '$choice'"
            exit 2
            ;;
    esac
}

read_interactive_target_repo() {
    echo ""
    local default_target
    default_target=$(pwd)
    read -r -p "Target repository for CI/hooks [$default_target]: " answer
    ARG_TARGET_REPO="${answer:-$default_target}"
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --components)
                shift
                if [[ -z "${1:-}" ]]; then
                    write_step error "--components requires a value"
                    exit 2
                fi
                IFS=',' read -r -a raw <<< "$1"
                ARG_COMPONENTS=("${raw[@]}")
                shift
                ;;
            --scope)
                shift
                if [[ "${1:-}" != 'global' && "${1:-}" != 'local' ]]; then
                    write_step error "--scope must be 'global' or 'local'"
                    exit 2
                fi
                ARG_SCOPE="$1"
                shift
                ;;
            --target-repo)
                shift
                if [[ -z "${1:-}" ]]; then
                    write_step error "--target-repo requires a value"
                    exit 2
                fi
                ARG_TARGET_REPO="$1"
                shift
                ;;
            --force)
                ARG_FORCE='true'
                shift
                ;;
            --dry-run)
                ARG_DRY_RUN='true'
                shift
                ;;
            --help|-h)
                ARG_HELP='true'
                shift
                ;;
            *)
                write_step error "Unknown argument: '$1'"
                echo ""
                show_help
                exit 2
                ;;
        esac
    done
}

resolve_arguments() {
    if [[ "${#ARG_COMPONENTS[@]}" -eq 0 ]]; then
        read_interactive_components
        local needs_scope='false'
        local needs_target='false'
        for c in "${ARG_COMPONENTS[@]}"; do
            [[ "$c" == 'skills' ]] && needs_scope='true'
            [[ "$c" == 'ci' || "$c" == 'hooks' ]] && needs_target='true'
        done
        if [[ "$needs_scope" == 'true' ]]; then
            read_interactive_scope
        fi
        if [[ "$needs_target" == 'true' ]]; then
            read_interactive_target_repo
        else
            ARG_TARGET_REPO="${ARG_TARGET_REPO:-$(pwd)}"
        fi
    else
        local expanded=()
        for c in "${ARG_COMPONENTS[@]}"; do
            if [[ "$c" == 'all' ]]; then
                expanded+=(skills ci hooks)
            else
                case "$c" in
                    skills|ci|hooks) expanded+=("$c") ;;
                    *)
                        write_step error "Invalid component: '$c'"
                        exit 2
                        ;;
                esac
            fi
        done
        readarray -t ARG_COMPONENTS < <(printf '%s\n' "${expanded[@]}" | awk '!seen[$0]++')
        ARG_TARGET_REPO="${ARG_TARGET_REPO:-$(pwd)}"
    fi
}

find_source_root() {
    local candidate
    candidate=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
    local current="$candidate"

    local required_markers=(
        'designer/SKILL.md'
        'validator/SKILL.md'
        'executor/SKILL.md'
        'observer/SKILL.md'
        'tooling/hooks'
        'tooling/ci'
    )

    while true; do
        local all_present='true'
        for marker in "${required_markers[@]}"; do
            if [[ ! -e "$current/$marker" ]]; then
                all_present='false'
                break
            fi
        done
        if [[ "$all_present" == 'true' ]]; then
            SOURCE_ROOT="$current"
            return 0
        fi

        local parent
        parent=$(dirname "$current")
        if [[ "$parent" == "$current" || -z "$parent" ]]; then
            return 1
        fi
        current="$parent"
    done
}

confirm_source_root() {
    if ! find_source_root; then
        write_step error "SLE source artifacts not found."
        write_step error "This script must run from within a clone of the 'echo-skills' repository."
        write_step error "Clone the repository first and run the script from inside it."
        exit 1
    fi
    write_step info "SLE source detected: $SOURCE_ROOT"
}

install_skills() {
    write_step warn "install_skills: to be implemented in the next commit (Plan step 5)"
    if [[ "$ARG_DRY_RUN" == 'true' ]]; then
        write_step dryrun "  - would copy designer/, validator/, executor/, observer/ to [$ARG_SCOPE] destination"
    fi
}

install_ci() {
    write_step warn "install_ci: to be implemented in commit 3 (Plan step 6)"
    if [[ "$ARG_DRY_RUN" == 'true' ]]; then
        write_step dryrun "  - would copy tooling/ci/*.yml to $ARG_TARGET_REPO/.github/workflows/ (warning mode)"
        write_step dryrun "  - would copy tooling/ci/scripts/ and tests/ to $ARG_TARGET_REPO/tooling/ci/"
        write_step dryrun "  - would create $ARG_TARGET_REPO/.sle/manifesto.md from skeleton (if absent)"
    fi
}

install_hooks() {
    write_step warn "install_hooks: to be implemented in commit 4 (Plan steps 7-8)"
    if [[ "$ARG_DRY_RUN" == 'true' ]]; then
        write_step dryrun "  - would copy tooling/hooks/ to $ARG_TARGET_REPO/tooling/hooks/"
        write_step dryrun "  - would add .sle/.active-role to .gitignore"
        write_step dryrun "  - would generate SLE-SETUP.md in target"
    fi
}

generate_setup_guide() {
    write_step warn "generate_setup_guide: to be implemented in commit 4 (Plan step 7)"
}

write_summary() {
    echo ""
    echo "---- Summary ----"
    echo "Components: ${ARG_COMPONENTS[*]}"
    if _contains skills "${ARG_COMPONENTS[@]}"; then
        echo "Skills scope: $ARG_SCOPE"
    fi
    if _contains ci "${ARG_COMPONENTS[@]}" || _contains hooks "${ARG_COMPONENTS[@]}"; then
        echo "Target repo: $ARG_TARGET_REPO"
    fi
    local mode
    if [[ "$ARG_DRY_RUN" == 'true' ]]; then
        mode='dry-run (nothing was modified)'
    else
        mode='real execution'
    fi
    echo "Mode: $mode"
    echo ""
    echo "Next steps will be listed here after full implementation."
    echo "-----------------"
}

_contains() {
    local needle="$1"
    shift
    for x in "$@"; do
        [[ "$x" == "$needle" ]] && return 0
    done
    return 1
}

main() {
    parse_args "$@"

    if [[ "$ARG_HELP" == 'true' ]]; then
        show_help
        exit 0
    fi

    resolve_arguments
    confirm_source_root

    if test_python_available; then
        PYTHON_AVAILABLE='true'
    else
        PYTHON_AVAILABLE='false'
        if _contains ci "${ARG_COMPONENTS[@]}" || _contains hooks "${ARG_COMPONENTS[@]}"; then
            write_step warn "Python 3.11+ not found in PATH - 'ci' and 'hooks' components need it."
            write_step warn "Skills will proceed normally; ci/hooks will be disabled."
        fi
    fi

    if _contains skills "${ARG_COMPONENTS[@]}"; then
        install_skills
    fi
    if _contains ci "${ARG_COMPONENTS[@]}" && [[ "$PYTHON_AVAILABLE" == 'true' ]]; then
        install_ci
    fi
    if _contains hooks "${ARG_COMPONENTS[@]}" && [[ "$PYTHON_AVAILABLE" == 'true' ]]; then
        install_hooks
        generate_setup_guide
    fi

    write_summary
    exit 0
}

trap 'write_step error "Unexpected error at line $LINENO"; exit 3' ERR

main "$@"
