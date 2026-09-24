#!/bin/bash
# register2.sh POD TAG RUN_FILES_ART : laptop bench-result/v1 of evidence/results/POD/TAG.json (pulled from the pod), ref run_files ->
# the pod-side run-files/v1 pack (pack_all.sh / put_pack.sh, already PRESERVED from the pod), --preserve, vocabulary labels by v3-scout-2.
# Prints "TAG result=art:... run_files=art:... t.total=... rust=...".
set -euo pipefail
POD=$1; TAG=$2; RF=$3
E=~/.research/notes/lanes/v3-scout-2/evidence
PY=~/projects/verity-main-wt/main/.venv/bin/python
cd ~/projects/verity-main-wt/v3-scout-2
set -a; source ~/.config/verity/r2.env; set +a
export PYTHONPATH=~/projects/verity-main-wt/qol/tools/research/src
research() { $PY -m research "$@"; }
case $POD in h100) HW="NVIDIA H100 80GB HBM3 (RunPod x2b0ahxr8g7k0s, EPYC 9554)";; a100) HW="NVIDIA A100-SXM4-80GB (RunPod u3nsufkequsg76, EPYC 7742)";; esac
read REL L P TT RUST < <($PY - $E/results/$POD/$TAG.json $E/results/$POD/${TAG}_rust.json <<'EOF'
import json, sys
d = json.load(open(sys.argv[1])); wf = d["workload_fingerprint"]; m = {x["name"]: x["value"] for x in d["measurements"]}
name = wf["software"]["backend"]["name"]
rel = name.split(",")[1].split()[0] if "," in name else "bf16-vu.py"
try:
    r = json.load(open(sys.argv[2])); rust = f"{r['accepted']}/{r['n']}{'-pinned' if r['system_pinned'] else '-UNPINNED'}"
except Exception:
    rust = "none"
print(rel, wf["security"]["rs_l"], wf["software"]["backend"].get("pipeline") or 1, f"{m['t.total']:.4f}", rust)
EOF
)
META=$(printf '{"lane":"v3-scout","by":"v3-scout-2","tag":"%s","relation":"%s","batch":%s,"pipeline":%s,"total_vus":4096,"zk":true,"mode":"local-coins","hardware":"%s","tree":"5e6b3e3","rust":"%s","run_files":"%s"}' "$TAG" "$REL" "$L" "$P" "$HW" "$RUST" "$RF")
RES=$(research data put --kind bench-result/v1 --file $E/results/$POD/$TAG.json --meta "$META" --ref run_files=$RF --preserve --json | $PY -c 'import json,sys; d=json.load(sys.stdin); print(d["id"] if "id" in d else d["push"]["id"])')
lab() { research data label "$RES" "$1" "$2" --by v3-scout-2 >/dev/null; }
lab candidate B-Ligero; lab mode interactive; lab zk true; lab scope vu; lab relation "$REL"; lab hardware "$HW"
lab authentication excluded; lab track scout; lab B 4096; lab pipeline "$P"; lab source "lane/v3-scout@5e6b3e3"
lab campaign relaunch-20260923T2100Z; lab sweep "relation x pipeline x l"; lab arm "$REL p$P l$L ($TAG)"
lab note "local coins (interactive protocol, in-process verifier coins): drill-down, not a live-verified cell; run by lane v3-scout, registered by v3-scout-2"
lab label "$REL --pipeline $P --batch $L, 4096 VUs, int-ZK local coins: t.total $TT s; Rust $RUST"
echo "$TAG result=$RES run_files=$RF t.total=$TT rust=$RUST"
