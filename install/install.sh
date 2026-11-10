#!/usr/bin/env bash
# Install (or uninstall) the Jarvis OpenCode agents, commands and skills.
# macOS / Linux / WSL / Git Bash. Same behaviour as install.ps1.
#
#   install/install.sh --target ~/work/my-app [--with-templates]
#   install/install.sh --global [--config-dir DIR] [--only all|factory|skills]
#   install/install.sh --target DIR --uninstall
#
# Existing files are never overwritten unless --force. Uninstall removes only
# files identical to this package unless --force.
set -euo pipefail

usage() { sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; }

target="" global=0 config_dir="" only="all" with_templates=0 force=0 dry=0 uninstall=0
while [ $# -gt 0 ]; do
  case "$1" in
    --target) target="${2:?--target needs a folder}"; shift 2 ;;
    --global) global=1; shift ;;
    --config-dir) config_dir="${2:?--config-dir needs a folder}"; shift 2 ;;
    --only) only="${2:?--only needs all|factory|skills}"; shift 2 ;;
    --with-templates) with_templates=1; shift ;;
    --force) force=1; shift ;;
    --dry-run) dry=1; shift ;;
    --uninstall) uninstall=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$only" in all|factory|skills) ;; *) echo "--only must be all, factory or skills" >&2; exit 2 ;; esac
if [ "$global" = 1 ] && [ -n "$target" ]; then echo "use either --target or --global, not both" >&2; exit 2; fi
if [ "$global" = 0 ] && [ -z "$target" ]; then echo "specify --target <project folder> or --global" >&2; exit 2; fi
if [ "$with_templates" = 1 ] && [ "$global" = 1 ]; then echo "--with-templates only applies to --target" >&2; exit 2; fi

pkg="$(cd "$(dirname "$0")/.." && pwd)"
src="$pkg/.opencode"
[ -d "$src" ] || { echo "package folder not found: $src" >&2; exit 1; }

if [ "$global" = 1 ]; then
  dest="${config_dir:-$HOME/.config/opencode}"
  project=""
else
  [ -d "$target" ] || { echo "target folder not found: $target" >&2; exit 1; }
  project="$(cd "$target" && pwd)"
  dest="$project/.opencode"
fi

selected() {  # $1 = path relative to .opencode/
  case "$1" in agents/jarvis-*|commands/jarvis-*|skills/jarvis-*) f=1 ;; *) f=0 ;; esac
  case "$only" in
    factory) [ "$f" = 1 ] ;;
    skills) case "$1" in skills/*) [ "$f" = 0 ] ;; *) false ;; esac ;;
    *) true ;;
  esac
}

sha() { if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1; else shasum -a 256 "$1" | cut -d' ' -f1; fi; }

p=""; [ "$dry" = 1 ] && p="[dry-run] "
mode="install"; [ "$uninstall" = 1 ] && mode="uninstall"
rels=()
while IFS= read -r -d '' file; do
  rel="${file#"$src"/}"
  if selected "$rel"; then rels+=("$rel"); fi
done < <(find "$src" -type f -print0 | sort -z)
echo "${p}Jarvis OpenCode package: $mode ${#rels[@]} file(s) ($only) -> $dest"

done_n=0; skipped=(); kept=()
for rel in "${rels[@]}"; do
  to="$dest/$rel"
  if [ "$uninstall" = 1 ]; then
    [ -f "$to" ] || continue
    if [ "$force" = 0 ] && [ "$(sha "$to")" != "$(sha "$src/$rel")" ]; then kept+=("$rel"); continue; fi
    if [ "$dry" = 0 ]; then
      rm -f -- "$to"
      # prune only the folders this file lived in, upwards, while empty (never $dest itself)
      d="$(dirname "$to")"
      while [ "${#d}" -gt "${#dest}" ] && rmdir -- "$d" 2>/dev/null; do d="$(dirname "$d")"; done
    fi
    done_n=$((done_n + 1)); continue
  fi
  if [ -f "$to" ] && [ "$force" = 0 ]; then skipped+=("$rel"); continue; fi
  if [ "$dry" = 0 ]; then mkdir -p "$(dirname "$to")"; cp -- "$src/$rel" "$to"; fi
  done_n=$((done_n + 1))
done

if [ "$uninstall" = 1 ]; then
  echo "${p}removed: $done_n"
  if [ "${#kept[@]}" -gt 0 ]; then
    echo "kept (changed after install; use --force to remove): ${#kept[@]}"; printf '  %s\n' "${kept[@]}"
  fi
else
  echo "${p}copied: $done_n"
  if [ "${#skipped[@]}" -gt 0 ]; then
    echo "skipped (already exists; use --force to overwrite): ${#skipped[@]}"; printf '  %s\n' "${skipped[@]}"
  fi
fi

if [ "$with_templates" = 1 ] && [ "$uninstall" = 0 ]; then
  for name in opencode.json AGENTS.md; do
    if [ -e "$project/$name" ]; then
      echo "template $name: $project/$name already exists - merge templates/$name into it by hand"
    else
      [ "$dry" = 1 ] || cp -- "$pkg/templates/$name" "$project/$name"
      echo "${p}template $name: created $project/$name"
    fi
  done
fi

if [ "$uninstall" = 0 ]; then
  echo
  echo "Next steps:"
  if [ -n "$project" ]; then
    echo "  1. Add \".jarvis/\" to $project/.gitignore (task state and worktrees are local)."
    echo "  2. cd \"$project\" && opencode agent list   (expect jarvis-queen and five jarvis-* subagents)"
    echo "  3. Start opencode, press Tab to select jarvis-queen, then run /jarvis-analyze"
  else
    echo "  1. opencode agent list   (expect jarvis-queen and five jarvis-* subagents)"
    echo "  2. In a project: start opencode, press Tab to select jarvis-queen, then run /jarvis-analyze"
  fi
fi
