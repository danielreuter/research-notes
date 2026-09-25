#!/usr/bin/env bash
# b-ligero-sha256: put + preserve one fetched file or tree; appends "art:... <what>" to evidence/store_ids.txt.
#   put.sh KIND --file|--tree PATH RUN RELATION NOTE [EXTRA_JSON] [--ref name=art:...]
set -euo pipefail
KIND=$1 MODE=$2 P=$3 RUN=$4 REL=$5 NOTE=$6 X=${7:-"{}"}; shift 7 || shift $#
OUT=~/.research/notes/lanes/b-ligero-sha256/evidence/store_ids.txt
SRC=$(cd ~/projects/verity-main-wt/b-ligero-sha256 && git rev-parse --short=12 HEAD)
set -a; source ~/.config/verity/r2.env; set +a
META=$(python3 -c "import json,sys; d={'lane':'b-ligero-sha256','candidate':'B-Ligero','track':'B','run':sys.argv[1],'relation':sys.argv[2],
'note':sys.argv[3],'hardware':'H100 80GB HBM3 (vy-b-ligero-sha256 qmiq4rs1f0y4tr)','hash':'sha256','source':'lane/b-ligero-sha256@'+sys.argv[5]}
d.update(json.loads(sys.argv[4])); print(json.dumps(d))" "$RUN" "$REL" "$NOTE" "$X" "$SRC")
ID=$(research data put --kind "$KIND" "$MODE" "$P" --meta "$META" "$@" --preserve --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('id') or d.get('art') or d)")
echo "$ID $RUN $(basename "$P") -- $NOTE" | tee -a "$OUT"
