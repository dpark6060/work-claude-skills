#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

link_md_files() {
    local category="$1"
    local source_dir="$SCRIPT_DIR/$category"
    local target_dir="$CLAUDE_DIR/$category"

    if [ ! -d "$source_dir" ]; then
        echo "[SKIP] $category/ — source directory does not exist"
        return
    fi

    mkdir -p "$target_dir"

    local found=0
    for file in "$source_dir"/*.md; do
        [ -f "$file" ] || continue
        found=1

        local name
        name="$(basename "$file")"
        local target="$target_dir/$name"

        if [ -L "$target" ]; then
            echo "[SKIP] $category/$name — symlink already exists"
        elif [ -e "$target" ]; then
            echo "[SKIP] $category/$name — already exists (not a symlink, skipping to be safe)"
        else
            ln -s "$file" "$target"
            echo "[LINKED] $category/$name → $target"
        fi
    done

    if [ "$found" -eq 0 ]; then
        echo "[SKIP] $category/ — no .md files found"
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
        local target="$target_dir/$name"

        if [ -L "$target" ]; then
            echo "[SKIP] $category/$name — symlink already exists"
        elif [ -e "$target" ]; then
            echo "[SKIP] $category/$name — already exists (not a symlink, skipping to be safe)"
        else
            ln -s "$dir" "$target"
            echo "[LINKED] $category/$name → $target"
        fi
    done

    if [ "$found" -eq 0 ]; then
        echo "[SKIP] $category/ — no subdirectories found"
    fi
}

# NOTE: The global ~/.claude/CLAUDE.md is NO LONGER linked from this repo. That
# responsibility now lives in the Personal Claude config repo
# (~/Documents/Personal/Claude), which owns global_config/CLAUDE.md and links it.
# A copy is kept here in global_config/CLAUDE.md for reference only — it is not linked.

echo "=== Linking rules ==="
link_subdirs "rules"

echo ""
echo "=== Linking skills ==="
# Link shared reference directory (no SKILL.md, so handled explicitly)
SKILLS_SOURCE="$SCRIPT_DIR/skills"
SKILLS_TARGET="$CLAUDE_DIR/skills"
mkdir -p "$SKILLS_TARGET"
for shared_name in shared; do
    src="$SKILLS_SOURCE/$shared_name"
    tgt="$SKILLS_TARGET/$shared_name"
    if [ ! -d "$src" ]; then
        echo "[SKIP] skills/$shared_name — source does not exist"
    elif [ -L "$tgt" ]; then
        echo "[SKIP] skills/$shared_name — symlink already exists"
    elif [ -e "$tgt" ]; then
        echo "[SKIP] skills/$shared_name — already exists (not a symlink)"
    else
        ln -s "$src" "$tgt"
        echo "[LINKED] skills/$shared_name → $tgt"
    fi
done

# Recursively find all skill directories (identified by containing SKILL.md)
while IFS= read -r -d '' skill_file; do
    skill_dir="$(dirname "$skill_file")"
    name="$(basename "$skill_dir")"
    tgt="$SKILLS_TARGET/$name"

    if [ -L "$tgt" ]; then
        echo "[SKIP] skills/$name — symlink already exists"
    elif [ -e "$tgt" ]; then
        echo "[SKIP] skills/$name — already exists (not a symlink)"
    else
        ln -s "$skill_dir" "$tgt"
        echo "[LINKED] skills/$name → $tgt"
    fi
done < <(find "$SKILLS_SOURCE" -name "SKILL.md" -print0)

echo ""
echo "=== Linking agents ==="
link_md_files "agents"

echo ""
echo "Done."
