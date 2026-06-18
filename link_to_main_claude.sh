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

echo "=== Linking global CLAUDE.md ==="
# The personal global config lives in global_config/CLAUDE.md and is linked to
# ~/.claude/CLAUDE.md. The repo root CLAUDE.md is the repo's own guide, not this.
GLOBAL_MD_SRC="$SCRIPT_DIR/global_config/CLAUDE.md"
GLOBAL_MD_TGT="$CLAUDE_DIR/CLAUDE.md"
if [ ! -f "$GLOBAL_MD_SRC" ]; then
    echo "[SKIP] CLAUDE.md — source $GLOBAL_MD_SRC does not exist"
elif [ -L "$GLOBAL_MD_TGT" ]; then
    # Existing symlink (possibly dangling after a move) — repoint it.
    ln -sf "$GLOBAL_MD_SRC" "$GLOBAL_MD_TGT"
    echo "[RELINKED] CLAUDE.md → $GLOBAL_MD_TGT"
elif [ -e "$GLOBAL_MD_TGT" ]; then
    echo "[SKIP] CLAUDE.md — already exists as a real file (not a symlink, leaving it alone)"
else
    ln -s "$GLOBAL_MD_SRC" "$GLOBAL_MD_TGT"
    echo "[LINKED] CLAUDE.md → $GLOBAL_MD_TGT"
fi

echo ""
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
