#!/bin/sh
# private-recursion evidence: differential, negatives, gate-level check, swap, costs (ART = fetched art:d9837120, bd9f7efb, 04259cdd; MUT = redigest.py outputs)
set -e
cd /workspace
O=${OUT:-/tmp/pr/ev}
git rev-parse HEAD > $O/commit.txt
uv run python /tmp/pr/costs.py > $O/costs.json
uv run python /tmp/pr/swap.py > $O/swap.txt
uv run python /tmp/pr/run_many.py $(cat /tmp/pr/sessions.txt) > $O/differential.jsonl
uv run python /tmp/pr/negatives.py > $O/negatives.jsonl
uv run python /tmp/pr/gatecheck.py > $O/gatecheck.txt
echo done > $O/DONE
