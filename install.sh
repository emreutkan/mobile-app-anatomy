#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-all}"
PROJECT_PATH="${2:-$PWD}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SOURCE="$ROOT/skills/mobile-app-anatomy"

copy_fresh() {
  local source="$1"
  local destination="$2"
  rm -rf "$destination"
  mkdir -p "$(dirname "$destination")"
  cp -R "$source" "$destination"
}

case "$TARGET" in
  claude|codex|cursor|all) ;;
  *) echo "Usage: $0 [claude|codex|cursor|all] [project-path]" >&2; exit 2 ;;
esac

if [[ "$TARGET" == "claude" || "$TARGET" == "all" ]]; then
  copy_fresh "$SKILL_SOURCE" "$HOME/.claude/skills/mobile-app-anatomy"
  echo "Installed Claude skill: $HOME/.claude/skills/mobile-app-anatomy"
fi

if [[ "$TARGET" == "codex" || "$TARGET" == "all" ]]; then
  copy_fresh "$SKILL_SOURCE" "$HOME/.agents/skills/mobile-app-anatomy"
  echo "Installed Codex skill: $HOME/.agents/skills/mobile-app-anatomy"
fi

if [[ "$TARGET" == "cursor" || "$TARGET" == "all" ]]; then
  copy_fresh "$SKILL_SOURCE" "$PROJECT_PATH/.cursor/skills/mobile-app-anatomy"
  mkdir -p "$PROJECT_PATH/.cursor/rules"
  cp "$ROOT/cursor/mobile-app-anatomy.mdc" "$PROJECT_PATH/.cursor/rules/mobile-app-anatomy.mdc"
  echo "Installed Cursor skill and rule under: $PROJECT_PATH/.cursor"
fi
