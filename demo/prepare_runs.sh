#!/usr/bin/env bash
# Creates two clean, independent copies of the baseline service for the live demo:
#
#   <dest>/run-a-one-line   code only (no CLAUDE.md, no docs/, no demo/)
#   <dest>/run-b-4d         code + CLAUDE.md + docs/ (still no demo/)
#
# Each copy is its own git repo with one "Baseline" commit, so you can diff the result afterwards.
# The demo/ folder is never copied, because the scorecard reveals the hidden rules.
#
# Usage: demo/prepare_runs.sh <destination-folder>
set -euo pipefail

dest="${1:?usage: demo/prepare_runs.sh <destination-folder>}"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

for run in run-a-one-line run-b-4d; do
  if [ -e "$dest/$run" ]; then
    echo "Refusing to overwrite existing folder: $dest/$run" >&2
    exit 1
  fi
done

for run in run-a-one-line run-b-4d; do
  target="$dest/$run"
  mkdir -p "$target"
  cp -R "$repo_root/app" "$repo_root/tests" "$repo_root/requirements.txt" "$repo_root/.gitignore" "$target/"
done

# Only Run B gets the guideline files.
cp "$repo_root/CLAUDE.md" "$dest/run-b-4d/"
cp -R "$repo_root/docs" "$dest/run-b-4d/"

for run in run-a-one-line run-b-4d; do
  target="$dest/$run"
  find "$target" -name "__pycache__" -type d -prune -exec rm -rf {} +
  (
    cd "$target"
    git init -q
    git add -A
    git -c user.name="demo" -c user.email="demo@example.com" commit -q -m "Baseline"
  )
  echo "Prepared $target"
done

echo
echo "Next: cd into each folder, run 'pip install -r requirements.txt && pytest', then open it in Claude Code."
