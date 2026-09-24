#!/usr/bin/env bash
# register.sh TAG ARM: copy /workspace/sp1-tcdot/runs/TAG from the pod, put the run files (run-files/v1: result,
# measurements, prove/verify/negatives json, host + prover logs, statement.bin, every proof dump) and the result
# (bench-result/v1, --ref run_files), both --preserve, then the producer's labels.  Prints "TAG result=art:... run_files=art:...".
set -euo pipefail
TAG=$1; ARM=${2:-$1}
R=~/.research/bin/research
D=/tmp/sp1tcdot/runs/$TAG
rm -rf $D && mkdir -p $D
/tmp/sp1tcdot/pssh "cd /workspace/sp1-tcdot/runs/$TAG && tar -cf - ." | tar -xf - -C $D
test -s $D/result.json
read -r TT STATUS SRC NAME < <(python3 - $D/result.json <<'EOF'
import json, sys
d = json.load(open(sys.argv[1])); fp = d["workload_fingerprint"]; m = {x["name"]: x["value"] for x in d["measurements"]}
print(f"{m['t.total']:.3f}", d["validation"]["status"], fp["software"]["backend"]["commit"], fp["software"]["backend"]["name"].replace(" ", "_"))
EOF
)
[ "$STATUS" = passed ] || { echo "$TAG: validation $STATUS -- not registering"; exit 1; }
META=$(printf '{"lane":"sp1-tcdot","by":"sp1-tcdot","tag":"%s","arm":"%s","candidate":"SP1","label":"modified SP1 (TC_DOT chip)","target":"A100 BF16","B":4096,"hardware":"NVIDIA A100-SXM4-80GB","source":"lane/sp1-tcdot@%s"}' "$TAG" "$ARM" "$SRC")
RF=$($R data put --kind run-files/v1 --tree $D --meta "$META" --preserve --json | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["id"] if "id" in d else d["push"]["id"])')
RES=$($R data put --kind bench-result/v1 --file $D/result.json --meta "$META" --ref run_files=$RF --preserve --json | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["id"] if "id" in d else d["push"]["id"])')
lab() { $R data label "$RES" "$1" "$2" --by sp1-tcdot >/dev/null; }
lab candidate SP1; lab proof_class NON_ZK_PROOF; lab K 1536; lab B 4096; lab hardware "NVIDIA A100-SXM4-80GB (prover, CUDA)"
lab authentication excluded; lab campaign morning-tables; lab relation bf16-ampere-k1536; lab zk false; lab scope vu
lab track baseline; lab lane sp1-tcdot; lab soundness "SP1 100-bit target per STARK proof, union-bounded over the core proof's shards (< 2^-128)"
lab source "lane/sp1-tcdot@$SRC"; lab sweep "vu_software_threshold x vus_per_read"; lab arm "$ARM"
lab label "modified SP1 (TC_DOT chip), relation-bare/v2 bf16-ampere, 4096 VUs, A100 core STARK: t.total $TT s"
lab note "modified SP1: fork of SP1 6.4.0 + TC_DOT_BF16 precompile (FORK_HEAD in backends/sp1/tcdot); core proofs only; security 100-bit (drill-down, not a 2^-128 cell)"
echo "$TAG result=$RES run_files=$RF t.total=$TT"
