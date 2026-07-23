#!/usr/bin/env bash
set -euo pipefail

# Work Claude config installer.
#
# This is ADDITIVE: it links this repo's skills, agents, rules, and hooks into
# ~/.claude/ alongside whatever is already there (e.g. a separate personal
# config). Skills and agents are keyed by name, so work and personal entries
# coexist as long as their names don't collide.
#
# NOTE: The global ~/.claude/CLAUDE.md is NOT linked from this repo. That
# responsibility lives in the Personal Claude config repo, which owns
# global_config/CLAUDE.md and links it. A copy is kept here in
# global_config/CLAUDE.md for reference only — it is not linked.
#
# Aside from that (and this header comment), the machinery below is intended to
# be byte-identical to the Personal repo's link_to_main_claude.sh.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

RESET=0

usage() {
    cat <<'EOF'
Usage: link_to_main_claude.sh [--reset]

  (no args)   Create missing symlinks. Existing symlinks and real files are
              left untouched.
  --reset     Re-point existing symlinks. Any symlink at a target name is
              removed and re-created pointing at this repo. Use this after
              moving the repo, when stale symlinks point at the old path.
              Real (non-symlink) files are still never touched.
  -h, --help  Show this help.
EOF
}

for arg in "$@"; do
    case "$arg" in
        --reset|--force) RESET=1 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $arg" >&2; usage; exit 1 ;;
    esac
done

# Create a symlink src → tgt, honoring $RESET. Never clobbers a real file.
#   $1 src    absolute path to link source (this repo)
#   $2 tgt    absolute path of the symlink to create
#   $3 label  human-readable name for log output
make_link() {
    local src="$1" tgt="$2" label="$3"

    if [ -L "$tgt" ]; then
        if [ "$RESET" -eq 1 ]; then
            rm "$tgt"
            ln -s "$src" "$tgt"
            echo "[RELINKED] $label → $tgt"
        else
            echo "[SKIP] $label — symlink already exists (use --reset to re-point)"
        fi
    elif [ -e "$tgt" ]; then
        echo "[SKIP] $label — already exists (not a symlink, skipping to be safe)"
    else
        ln -s "$src" "$tgt"
        echo "[LINKED] $label → $tgt"
    fi
}

# Link each file in $category matching $pattern (default *.md) by name.
link_files() {
    local category="$1"
    local pattern="${2:-*.md}"
    local source_dir="$SCRIPT_DIR/$category"
    local target_dir="$CLAUDE_DIR/$category"

    if [ ! -d "$source_dir" ]; then
        echo "[SKIP] $category/ — source directory does not exist"
        return
    fi

    mkdir -p "$target_dir"

    local found=0
    for file in "$source_dir"/$pattern; do
        [ -f "$file" ] || continue
        found=1

        local name
        name="$(basename "$file")"
        make_link "$file" "$target_dir/$name" "$category/$name"
    done

    if [ "$found" -eq 0 ]; then
        echo "[SKIP] $category/ — no files matching '$pattern' found"
    fi
}

link_subdirs() {
    local category="$1"
    local source_dir="$SCRIPT_DIR/$category"
    local target_dir="$CLAUDE_DIR/$category"

    if [ ! -d "$source_dir" ]; then
        echo "[SKIP] $category/ — source directory does not exist"
        return
    fi

    mkdir -p "$target_dir"

    local found=0
    for dir in "$source_dir"/*/; do
        [ -d "$dir" ] || continue
        found=1

        local name
        name="$(basename "$dir")"
        make_link "$dir" "$target_dir/$name" "$category/$name"
    done

    if [ "$found" -eq 0 ]; then
        echo "[SKIP] $category/ — no subdirectories found"
    fi
}

link_skills() {
    local skills_source="$SCRIPT_DIR/skills"
    local skills_target="$CLAUDE_DIR/skills"

    if [ ! -d "$skills_source" ]; then
        echo "[SKIP] skills/ — source directory does not exist"
        return
    fi

    mkdir -p "$skills_target"

    # Link shared reference directory (no SKILL.md, so handled explicitly)
    for shared_name in shared; do
        local src="$skills_source/$shared_name"
        local tgt="$skills_target/$shared_name"
        if [ ! -d "$src" ]; then
            echo "[SKIP] skills/$shared_name — source does not exist"
        else
            make_link "$src" "$tgt" "skills/$shared_name"
        fi
    done

    # Recursively find all skill directories (identified by containing SKILL.md)
    while IFS= read -r -d '' skill_file; do
        local skill_dir name
        skill_dir="$(dirname "$skill_file")"
        name="$(basename "$skill_dir")"
        make_link "$skill_dir" "$skills_target/$name" "skills/$name"
    done < <(find "$skills_source" -name "SKILL.md" -print0)
}

# --- WORK-vs-PERSONAL DIFFERENCE: the Personal repo links global CLAUDE.md here;
# this repo intentionally does not (see header note above). ---

echo "=== Linking rules ==="
link_subdirs "rules"

echo ""
echo "=== Linking skills ==="
link_skills

echo ""
echo "=== Linking agents ==="
link_files "agents" "*.md"

echo ""
echo "=== Linking hooks ==="
link_files "hooks" "*"

echo ""
echo "Done."
