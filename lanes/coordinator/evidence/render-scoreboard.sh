#!/bin/bash
# Render the six tables (kb/TABLES.md) from the cli worktree and assemble the Project scoreboard doc.
# usage: render-scoreboard.sh CHANGED_LIST_MD   (the "changed since last digest" bullets, written by the coordinator)
set -euo pipefail
S=~/projects/verity-main-wt/cli
P=~/projects/verity-main-wt/main/.venv/bin/python
DOC="$HOME/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/files/docs/proof-optimization-tables.md"
R=~/.research/notes/campaigns/afternoon/render
T=$(date -u +%H%MZ); W=/tmp/coord-render; mkdir -p $W
export PYTHONPATH=$S/backends/numerical/python:$S/tools/research/src:$S
$P -m verity_numerical.bench.tables --root ~/.research/store --format md > $W/tables.md
$P -m verity_numerical.bench.drilldown --root ~/.research/store --format md > $W/drill.md
cp $W/tables.md $R/$T-tables.md; cp $W/drill.md $R/$T-drilldown.md
{
  echo "# Proof optimization tables"
  echo
  echo "Last render: $(TZ=America/Los_Angeles date '+%a %b %-d, %-I:%M %p PT') · main \`$(git -C $S rev-parse --short HEAD)\`"
  echo
  echo "## Changed since last digest"
  echo
  cat "$1"
  echo
  $P ~/.research/notes/lanes/coordinator/evidence/marked-cells.py $W/tables.md
  cat $W/tables.md
  echo
  cat $W/drill.md
} > "$DOC.tmp" && mv "$DOC.tmp" "$DOC"
echo "$DOC ($T)"
