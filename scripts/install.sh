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
#     --components skills|ci|all        -Components skills|ci|all
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
    skills   Copy the 5 skills: the 4 of the cycle (especificar, codificar,
             verificar, homologar) + the accessory prototipar-frontend
    ci       Copy workflows + CI scripts to the target repository
    all      skills + ci

OPTIONS:
    --components <list>    Comma-separated list: skills,ci,all
    --scope <value>        Skills scope: global (default, ~/.claude/skills/)
                           or local (<target>/.claude/skills/)
    --target-repo <path>   Target repository for CI (default: CWD)
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
    # Cada candidato e testado ate um responder versao valida, em vez de parar no
    # primeiro que existe no PATH: no Windows, 'python3' costuma ser o atalho da
    # Microsoft Store, que esta no PATH, nao roda, e imprime instrucao de
    # instalacao. Parar nele desabilitava o 'ci' com um Python 3.12 ao lado.
    local py_bin version_output major minor
    for py_bin in python3 python; do
        command -v "$py_bin" >/dev/null 2>&1 || continue
        version_output=$("$py_bin" --version 2>&1) || continue
        if [[ ! "$version_output" =~ Python\ ([0-9]+)\.([0-9]+) ]]; then
            continue
        fi
        major="${BASH_REMATCH[1]}"
        minor="${BASH_REMATCH[2]}"
        if (( major > 3 )) || { (( major == 3 )) && (( minor >= 11 )); }; then
            return 0
        fi
    done
    return 1
}

read_interactive_components() {
    echo ""
    echo "SLE Installer - interactive mode"
    echo "Choose what to install:"
    echo "  1) skills only (the 5 SLE skills)"
    echo "  2) skills + CI (recommended for first repository)"
    echo "  3) skills + CI (full setup)"
    echo "  4) ci only"
    read -r -p "Your choice [3]: " choice
    choice="${choice:-3}"
    case "$choice" in
        1) ARG_COMPONENTS=(skills) ;;
        2) ARG_COMPONENTS=(skills ci) ;;
        3) ARG_COMPONENTS=(skills ci) ;;
        4) ARG_COMPONENTS=(ci) ;;
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
    read -r -p "Target repository for CI [$default_target]: " answer
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
            [[ "$c" == 'ci' ]] && needs_target='true'
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
                expanded+=(skills ci)
            else
                case "$c" in
                    skills|ci) expanded+=("$c") ;;
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
        'especificar/SKILL.md'
        'codificar/SKILL.md'
        'verificar/SKILL.md'
        'homologar/SKILL.md'
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

get_skills_destination() {
    if [[ "$ARG_SCOPE" == 'global' ]]; then
        printf '%s\n' "$HOME/.claude/skills"
    else
        printf '%s\n' "$ARG_TARGET_REPO/.claude/skills"
    fi
}

copy_skill_folder() {
    local skill_name="$1"
    local source_dir="$2"
    local dest_root="$3"
    local src_skill="$source_dir/$skill_name"
    local dst_skill="$dest_root/$skill_name"

    if [[ ! -d "$src_skill" ]]; then
        write_step error "source skill missing: $src_skill"
        return 1
    fi

    if [[ -e "$dst_skill" && "$ARG_FORCE" != 'true' ]]; then
        write_step skipped "skill '$skill_name' already at $dst_skill (use --force to overwrite)"
        return 0
    fi

    if [[ "$ARG_DRY_RUN" == 'true' ]]; then
        write_step dryrun "would copy $src_skill -> $dst_skill"
        return 0
    fi

    local staging="$dst_skill.sle-staging"
    [[ -e "$staging" ]] && rm -rf "$staging"

    mkdir -p "$dest_root"
    cp -R "$src_skill" "$staging"

    [[ -e "$dst_skill" ]] && rm -rf "$dst_skill"
    mv "$staging" "$dst_skill"

    write_step action "installed skill '$skill_name' -> $dst_skill"
    ARTIFACTS_CREATED+=("$dst_skill")
    return 0
}

install_skills() {
    local destination
    destination=$(get_skills_destination)
    write_step info "installing skills to: $destination (scope=$ARG_SCOPE)"

    # the four cycle skills, then the accessories - accessories run before the
    # cycle and are installed the same way, so one list covers both
    local skills=(especificar codificar verificar homologar prototipar-frontend)
    for skill in "${skills[@]}"; do
        if ! copy_skill_folder "$skill" "$SOURCE_ROOT" "$destination"; then
            write_step error "failed to install skill '$skill' - aborting skills phase"
            exit 1
        fi
    done
}

apply_warning_mode() {
    local input_file="$1"
    awk '
        BEGIN { pending_indent = ""; pending = 0 }
        {
            if (pending) {
                if ($0 ~ /^[[:space:]]*continue-on-error[[:space:]]*:[[:space:]]*true/) {
                    pending = 0
                } else if ($0 ~ /^[[:space:]]*-[[:space:]]/) {
                    print pending_indent "  continue-on-error: true"
                    pending = 0
                } else if ($0 !~ /^[[:space:]]/ || $0 ~ /^[[:space:]]*$/) {
                    pending = 0
                } else {
                    # continue accumulating within same step
                    if (match($0, /^[[:space:]]+/)) {
                        cur_indent_len = RLENGTH
                        pending_indent_len = length(pending_indent)
                        if (cur_indent_len <= pending_indent_len) {
                            print pending_indent "  continue-on-error: true"
                            pending = 0
                        }
                    }
                }
            }

            print $0

            if (match($0, /^([[:space:]]+)-[[:space:]]+(name|uses):/, arr)) {
                pending_indent = arr[1]
                pending = 1
            }
        }
        END {
            if (pending) {
                print pending_indent "  continue-on-error: true"
            }
        }
    ' "$input_file"
}

copy_text_file() {
    local dest_path="$1"
    local content="$2"

    if [[ -e "$dest_path" && "$ARG_FORCE" != 'true' ]]; then
        write_step skipped "target file exists (skipped): $dest_path"
        return 0
    fi

    if [[ "$ARG_DRY_RUN" == 'true' ]]; then
        write_step dryrun "would write $dest_path"
        return 0
    fi

    local parent
    parent=$(dirname "$dest_path")
    mkdir -p "$parent"

    local staging="$dest_path.sle-staging"
    printf '%s' "$content" > "$staging"

    [[ -e "$dest_path" ]] && rm -f "$dest_path"
    mv "$staging" "$dest_path"

    write_step action "wrote $dest_path"
    ARTIFACTS_CREATED+=("$dest_path")
}

copy_directory_tree() {
    local source_dir="$1"
    local dest_dir="$2"

    if [[ ! -d "$source_dir" ]]; then
        write_step error "source directory missing: $source_dir"
        return 1
    fi

    if [[ -e "$dest_dir" && "$ARG_FORCE" != 'true' ]]; then
        write_step skipped "directory exists (skipped): $dest_dir"
        return 0
    fi

    if [[ "$ARG_DRY_RUN" == 'true' ]]; then
        write_step dryrun "would copy tree $source_dir -> $dest_dir"
        return 0
    fi

    local staging="$dest_dir.sle-staging"
    [[ -e "$staging" ]] && rm -rf "$staging"

    mkdir -p "$(dirname "$dest_dir")"
    cp -R "$source_dir" "$staging"

    [[ -e "$dest_dir" ]] && rm -rf "$dest_dir"
    mv "$staging" "$dest_dir"

    write_step action "installed tree $source_dir -> $dest_dir"
    ARTIFACTS_CREATED+=("$dest_dir")
}

create_manifesto_skeleton() {
    local manifesto_path="$ARG_TARGET_REPO/.sle/manifesto.md"
    if [[ -e "$manifesto_path" ]]; then
        write_step skipped "manifest already exists (preserved): $manifesto_path"
        return 0
    fi

    local template_path="$SOURCE_ROOT/scripts/templates/manifesto-esqueleto.md"
    if [[ ! -e "$template_path" ]]; then
        write_step error "manifest template missing: $template_path"
        return 1
    fi

    if [[ "$ARG_DRY_RUN" == 'true' ]]; then
        write_step dryrun "would create $manifesto_path from skeleton"
        return 0
    fi

    mkdir -p "$ARG_TARGET_REPO/.sle"
    cp "$template_path" "$manifesto_path"
    write_step action "created $manifesto_path (fill <preencher: ...> placeholders)"
    ARTIFACTS_CREATED+=("$manifesto_path")
}

install_ci() {
    local source_ci="$SOURCE_ROOT/tooling/ci"
    local workflows_dir="$ARG_TARGET_REPO/.github/workflows"
    local target_ci_dir="$ARG_TARGET_REPO/tooling/ci"

    write_step info "installing CI workflows to: $workflows_dir (warning mode by default)"

    local yaml_file
    for yaml_file in "$source_ci"/*.yml; do
        [[ -e "$yaml_file" ]] || continue
        local name
        name=$(basename "$yaml_file")
        local dest_path="$workflows_dir/$name"
        local transformed
        transformed=$(apply_warning_mode "$yaml_file")
        copy_text_file "$dest_path" "$transformed"
    done

    for subdir in scripts tests; do
        copy_directory_tree "$source_ci/$subdir" "$target_ci_dir/$subdir"
    done

    create_manifesto_skeleton
}

add_gitignore_entry() {
    local entry="$1"
    local gitignore_path="$ARG_TARGET_REPO/.gitignore"

    if [[ -e "$gitignore_path" ]]; then
        while IFS= read -r line; do
            if [[ "${line// }" == "$entry" ]]; then
                write_step skipped ".gitignore already contains '$entry' (skipped)"
                return 0
            fi
        done < "$gitignore_path"
    fi

    if [[ "$ARG_DRY_RUN" == 'true' ]]; then
        write_step dryrun "would add '$entry' to $gitignore_path"
        return 0
    fi

    if [[ -e "$gitignore_path" ]]; then
        local last_char
        last_char=$(tail -c 1 "$gitignore_path" 2>/dev/null || printf '')
        if [[ "$last_char" != $'\n' ]]; then
            printf '\n' >> "$gitignore_path"
        fi
        printf '\n# SLE marker-file: role da sessao ativa (local, nao versionado)\n%s\n' "$entry" >> "$gitignore_path"
    else
        mkdir -p "$(dirname "$gitignore_path")"
        printf '# SLE marker-file: role da sessao ativa (local, nao versionado)\n%s\n' "$entry" > "$gitignore_path"
    fi

    write_step action "added '$entry' to $gitignore_path"
    ARTIFACTS_CREATED+=("$gitignore_path")
}

generate_setup_guide() {
    local template_path="$SOURCE_ROOT/scripts/templates/sle-setup.md.template"
    local dest_path="$ARG_TARGET_REPO/SLE-SETUP.md"

    if [[ ! -e "$template_path" ]]; then
        write_step error "setup template missing: $template_path"
        return 1
    fi

    if [[ -e "$dest_path" && "$ARG_FORCE" != 'true' ]]; then
        write_step skipped "SLE-SETUP.md already exists (preserved): $dest_path"
        return 0
    fi

    if [[ "$ARG_DRY_RUN" == 'true' ]]; then
        write_step dryrun "would generate $dest_path"
        return 0
    fi

    local install_date components ci_installed artifacts_list
    install_date=$(date '+%Y-%m-%d %H:%M:%S %z')
    components="${ARG_COMPONENTS[*]}"
    if _contains ci "${ARG_COMPONENTS[@]}"; then
        ci_installed='yes'
    else
        ci_installed='no'
    fi

    if [[ "${#ARTIFACTS_CREATED[@]}" -eq 0 ]]; then
        artifacts_list='- (none)'
    else
        artifacts_list=$(printf -- '- %s\n' "${ARTIFACTS_CREATED[@]}")
        artifacts_list="${artifacts_list%$'\n'}"
    fi

    local template
    template=$(cat "$template_path")

    template="${template//\{\{INSTALL_DATE\}\}/$install_date}"
    template="${template//\{\{TARGET_REPO\}\}/$ARG_TARGET_REPO}"
    template="${template//\{\{COMPONENTS\}\}/$components}"
    template="${template//\{\{CI_INSTALLED\}\}/$ci_installed}"
    template="${template//\{\{ARTIFACTS_LIST\}\}/$artifacts_list}"
    template="${template//\{\{UNINSTALL_LIST\}\}/$artifacts_list}"

    # O alvo pode nao existir ainda: instalar num repositorio que sera criado e
    # uso legitimo, e o install.ps1 ja aceitava. Sem isto o redirecionamento
    # abaixo falha com "No such file or directory" e o instalador sai com 1.
    mkdir -p "$ARG_TARGET_REPO"

    printf '%s\n' "$template" > "$dest_path"
    write_step action "generated $dest_path"
    ARTIFACTS_CREATED+=("$dest_path")
}

write_summary() {
    echo ""
    echo "---- Summary ----"
    echo "Components: ${ARG_COMPONENTS[*]}"
    if _contains skills "${ARG_COMPONENTS[@]}"; then
        echo "Skills scope: $ARG_SCOPE"
    fi
    if _contains ci "${ARG_COMPONENTS[@]}"; then
        echo "Target repo: $ARG_TARGET_REPO"
    fi
    if [[ "$ARG_DRY_RUN" == 'true' ]]; then
        echo "Mode: dry-run (nothing was modified)"
    else
        echo "Mode: real execution"
        echo "Artifacts created: ${#ARTIFACTS_CREATED[@]}"
    fi
    echo ""
    echo "Next steps:"
    local step=1

    if _contains ci "${ARG_COMPONENTS[@]}"; then
        echo "  $step. Review $ARG_TARGET_REPO/.sle/manifesto.md - replace <preencher: ...> placeholders."
        step=$((step + 1))
    fi
    echo "  $step. Start a demand with: /especificar"
    step=$((step + 1))
    if _contains ci "${ARG_COMPONENTS[@]}"; then
        echo "  $step. Run 'pytest tooling/' in the target repo to confirm CI scripts pass."
        step=$((step + 1))
        echo "  $step. After 1-2 sprints in warning mode, remove 'continue-on-error: true' from workflows."
        step=$((step + 1))
    fi
    if _contains skills "${ARG_COMPONENTS[@]}" && [[ "${#ARG_COMPONENTS[@]}" -eq 1 ]]; then
        echo "  $step. Skills installed. Read README.md and metodologia-sle.md at the source repo."
        step=$((step + 1))
    fi
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
        if _contains ci "${ARG_COMPONENTS[@]}"; then
            write_step warn "Python 3.11+ not found in PATH - the 'ci' component needs it."
            write_step warn "Skills will proceed normally; ci will be disabled."
        fi
    fi

    if _contains skills "${ARG_COMPONENTS[@]}"; then
        install_skills
    fi
    if _contains ci "${ARG_COMPONENTS[@]}" && [[ "$PYTHON_AVAILABLE" == 'true' ]]; then
        install_ci
    fi
    # O guia de setup nasce sempre que algo foi para o repositório alvo: é ele que explica
    # o ciclo das quatro skills e o que ainda precisa da mão do humano no manifesto.
    if _contains ci "${ARG_COMPONENTS[@]}"; then
        generate_setup_guide
    fi

    write_summary
    exit 0
}

trap 'write_step error "Unexpected error at line $LINENO"; exit 3' ERR

main "$@"
