#!/usr/bin/env bash
# fill-dc A100: after the live rounds, two local-coin rounds of the two chosen configs with rep-1 dumps (alternative Table 2
# candidates for a Rust reverify by verify-night, beside the live-accepted runs).
cd /workspace/fill-dc
while pgrep -f "scripts/30-live.sh" >/dev/null; do sleep 5; done
DUMP=1 PREFIX=dump ROUNDS="1 2" bash scripts/12-rounds.sh D-ab-v3p8:bf16-ampere-v3:16384:8 D-ah-v1p8:bf16-ampere:16384:8:--auth,included-hash
