#!/bin/bash
# register.sh POD TAG HARDWARE : pod-side run-files/v1 pack (put_pack.sh, PRESERVED from the pod) + a laptop bench-result/v1 of the
# result json (ref run_files -> the pack), --preserve, labels by v3-scout.  Prints "TAG result=art:... run_files=art:...".
set -euo pipefail
POD=$1; TAG=$2; HW=$3
E=~/.research/notes/lanes/v3-scout/evidence
cd ~/projects/verity-main-wt/v3-scout
set -a; source ~/.config/verity/r2.env; set +a
export PYTHONPATH=~/projects/verity-main-wt/qol/tools/research/src
research() { ~/projects/verity-main-wt/main/.venv/bin/python -m research "$@"; }
PODNAME=vy-v3-scout-$POD
RF=$($E/ssh_$POD.sh "bash /workspace/put_pack.sh $TAG $PODNAME" | ~/projects/verity-main-wt/main/.venv/bin/python -c 'import json,sys; d=json.load(sys.stdin); print(d["id"] if "id" in d else d["push"]["id"]) ' 2>/dev/null || true)
[ -n "$RF" ] || { echo "$TAG: pod-side put failed"; exit 1; }
mkdir -p $E/results/$POD
$E/ssh_$POD.sh "cat /workspace/v3s/results/$TAG.json" > $E/results/$POD/$TAG.json
$E/ssh_$POD.sh "cat /workspace/v3s/results/${TAG}_rust.json 2>/dev/null" > $E/results/$POD/${TAG}_rust.json || true
read REL L P TT RUST < <(~/projects/verity-main-wt/main/.venv/bin/python - $E/results/$POD/$TAG.json $E/results/$POD/${TAG}_rust.json <<'EOF'
import json, sys
d = json.load(open(sys.argv[1])); wf = d["workload_fingerprint"]; m = {x["name"]: x["value"] for x in d["measurements"]}
rel = wf["software"]["backend"]["name"].split(",")[1].split()[0]
try:
    r = json.load(open(sys.argv[2])); rust = f"{r['accepted']}/{r['n']}{'-pinned' if r['system_pinned'] else '-UNPINNED'}"
except Exception:
    rust = "none"
print(rel, wf["security"]["rs_l"], wf["software"]["backend"]["pipeline"], f"{m['t.total']:.4f}", rust)
EOF
)
META=$(printf '{"lane":"v3-scout","by":"v3-scout","tag":"%s","relation":"%s","batch":%s,"pipeline":%s,"total_vus":4096,"zk":true,"mode":"local-coins","hardware":"%s","tree":"5e6b3e3","rust":"%s","run_files":"%s"}' "$TAG" "$REL" "$L" "$P" "$HW" "$RUST" "$RF")
RES=$(research data put --kind bench-result/v1 --file $E/results/$POD/$TAG.json --meta "$META" --ref run_files=$RF --preserve --json | ~/projects/verity-main-wt/main/.venv/bin/python -c 'import json,sys; d=json.load(sys.stdin); print(d["id"] if "id" in d else d["push"]["id"])')
lab() { research data label "$RES" "$1" "$2" --by v3-scout >/dev/null; }
lab candidate B-Ligero; lab mode interactive; lab zk true; lab scope vu; lab relation "$REL"; lab hardware "$HW"
lab authentication excluded; lab track scout; lab B 4096; lab pipeline "$P"; lab lane v3-scout
lab campaign relaunch-20260923T2100Z; lab sweep "relation x pipeline x l"; lab arm "$REL p$P l$L"
lab note "local coins (interactive protocol, in-process verifier coins): drill-down, not a live-verified cell; tree lane/v3-scout 5e6b3e3"
lab label "$REL --pipeline $P --batch $L, 4096 VUs, int-ZK local coins: t.total $TT s; Rust $RUST"
echo "$TAG result=$RES run_files=$RF t.total=$TT rust=$RUST"
