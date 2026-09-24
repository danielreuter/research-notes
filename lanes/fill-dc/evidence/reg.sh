#!/usr/bin/env bash
# fill-dc (laptop): register one pod run dir.   reg.sh POD TAG "LABEL" [tree]
#   POD = h100 | a100.  tree: the pod puts runs/TAG (result.json, log, meta.txt, proofs/) as run-files/v1 --preserve, with a
#   short-lived bucket-scoped credential it reads from ssh STDIN ($FDC_CREDS, `research data mint-credential --env` output held
#   in the laptop shell only; never a file). Always: bench-result/v1 = runs/TAG/result.json UNCHANGED (run_id kept) + {label,
#   lane, tag, pod}, ref run_files=<tree> when there is one, --preserve, from the laptop. Appends a line to registered.txt.
set -uo pipefail
pod=$1 tag=$2 label=$3 tree=${4:-}
R=~/.research/bin/research
OUT=~/.research/notes/lanes/fill-dc/evidence/registered.txt
K=(-i /Users/danielreuter/.runpod/ssh/runpodctl-ssh-key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/Users/danielreuter/.runpod/ssh/veritor-campaign-known_hosts -o ServerAliveInterval=30 -o LogLevel=ERROR -o ConnectTimeout=15)
case $pod in
  h100) S=(ssh "${K[@]}" -p 10179 root@91.199.227.82); PODNAME="vy-fill-dc-h100 (H100 80GB HBM3, EU-NL-1)" ;;
  a100) S=(ssh "${K[@]}" -p 16369 root@157.157.221.29); PODNAME="vy-fill-dc-a100 (A100-SXM4-80GB, EUR-IS-1)" ;;
  *) echo "pod h100|a100"; exit 2 ;;
esac
set -a; source ~/.config/verity/r2.env; set +a
W=/tmp/fdc-reg; mkdir -p $W
"${S[@]}" "cat /workspace/fill-dc/runs/$tag/result.json" > $W/$tag.result.json || { echo "$tag: no result.json"; exit 1; }
refs=(); tid=""
if [ "$tree" = tree ]; then
  [ -n "${FDC_CREDS:-}" ] || { echo "FDC_CREDS unset (mint-credential --env in this shell)"; exit 2; }
  meta=$(python3 -c 'import json,sys; print(json.dumps({"lane": "fill-dc", "tag": sys.argv[1], "label": "fill-dc " + sys.argv[2], "pod": sys.argv[3], "listed": ["proofs"]}))' "$tag" "$label" "$PODNAME")
  tid=$(printf '%s\n' "$FDC_CREDS" | "${S[@]}" "set -a; eval \"\$(cat)\"; set +a; source /workspace/env.sh; cd /workspace/fill-dc/runs/$tag &&
      RESEARCH_STORE=/workspace/store RESEARCH_STORE_CONFIG=/workspace/src/tools/research/store.pod.toml \
      \$PY -m research data put --kind run-files/v1 --tree . --meta '$meta' --preserve --json" 2>$W/$tag.tree.err \
      | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["id"] if (d.get("preserve") or {}).get("preserved") else "")' 2>/dev/null)
  [ -n "$tid" ] || { echo "$tag: tree put FAILED ($(tail -2 $W/$tag.tree.err | tr '\n' ' '))"; exit 1; }
  refs=(--ref run_files=$tid)
fi
python3 - $W/$tag.result.json "$label" "$tag" "$PODNAME" > $W/$tag.meta.json <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
m.update(label="fill-dc " + sys.argv[2], lane="fill-dc", tag=sys.argv[3], pod=sys.argv[4])
print(json.dumps(m))
EOF
br=$($R data put --kind bench-result/v1 --meta @$W/$tag.meta.json ${refs[@]+"${refs[@]}"} --preserve --json 2>$W/$tag.br.err \
     | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["id"] if (d.get("preserve") or {}).get("preserved") else "")' 2>/dev/null)
[ -n "$br" ] || { echo "$tag: bench-result put FAILED ($(tail -2 $W/$tag.br.err | tr '\n' ' '))"; exit 1; }
tt=$(python3 -c 'import json,sys;m={d["name"]:d["value"] for d in json.load(open(sys.argv[1]))["measurements"]};print(" ".join("%s=%.4f"%(k,m[k]) for k in ("t.total","t.total_live") if k in m))' $W/$tag.result.json)
line="$(date -u +%H:%MZ) $pod $tag result=$br${tid:+ tree=$tid} $tt | $label"
echo "$line" | tee -a $OUT
rm -f $W/$tag.*
