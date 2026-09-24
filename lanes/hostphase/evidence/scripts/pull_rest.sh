#!/bin/bash
cd /Users/danielreuter/projects/verity-main-wt/hostphase
set -a; source ~/.config/verity/r2.env; set +a
for r in r20260923-031744-b10b r20260923-031830-65d9 r20260923-031855-bef9 r20260923-031920-d2ae r20260923-031046-9e90 r20260923-023702-98f2 r20260923-030652-a174 r20260923-032053-03b5; do
  echo "=== pull $r $(date -u +%H:%M:%S) free=$(df -h / | tail -1 | awk '{print $4}')"
  uv run research data pull $r --from vy-hostphase --project verity 2>&1 | grep -v -E '^(Uninstalled|Installed)' | tail -8
done
echo PULLS_DONE
