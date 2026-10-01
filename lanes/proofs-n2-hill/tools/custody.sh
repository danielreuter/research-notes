#!/usr/bin/env bash
# proofs-n2-hill custody, run from an agent VM with a configured research CLI (node 2 has none, and no credentials go to a node).
# Node 2's loop (n2h.py) rsyncs each finished attempt's run dir to vy-nebius-1 /workspace/jobs/proofs-n2-hill/runs/<id>/ (with its
# n2.json); this puts each one not yet in node 1's custody.tsv into the evidence store as a run-record/v1 artifact, preserved on
# the remote, and appends `<id> <art> <utc> <phase> <lane>` there.
set -euo pipefail
export PATH=/workspace/.venv/bin:$PATH RESEARCH_NOTES=$HOME/.research/notes RESEARCH_MACHINES_D=$HOME/.research/notes/machines.d
N=/workspace/jobs/proofs-n2-hill
# every GPU point's art gets a `note` (a node-2 point under proofs' offset rule, or node-2-only for FP4; its node, slice, GPU and socket
# neighbours) and a `hardware` label, both from n2label.py on node 1; `custody.sh relabel` rewrites them on every GPU point
S=$(mktemp -d)
trap 'rm -rf $S' EXIT
ssh1() { research pods ssh vy-nebius-1 -- "$@"; }
label_point() {  # RUN_ID ART
  local j
  j=$(ssh1 "python3 $N/bin/n2label.py $N/runs $1" < /dev/null)
  local ref note hw
  ref=$(python3 -c 'import json, sys; print(json.loads(sys.argv[1])["ref"])' "$j")
  note=$(python3 -c 'import json, sys; print(json.loads(sys.argv[1])["note"])' "$j")
  hw=$(python3 -c 'import json, sys; print(json.loads(sys.argv[1])["hardware"])' "$j")
  research data label $2 note "$note" --by proofs-n2-hill --ref $ref > /dev/null
  research data label $2 hardware "$hw" --by proofs-n2-hill --ref $ref > /dev/null
}
if [ "${1:-}" = relabel ]; then
  ssh1 "awk -F'\t' '\$4==\"gpu\"{print \$1, \$2}' $N/custody.tsv" | while read -r id art; do label_point $id $art; echo "$id $art relabelled"; done
  exit 0
fi
have=$(ssh1 "mkdir -p $N/runs && touch $N/custody.tsv && cut -f1 $N/custody.tsv")
ids=$(ssh1 "cd $N/runs && for d in n2h-*; do [ -f \$d/n2.json ] && echo \$d; done; true")
new=0
for id in $ids; do
  grep -qx "$id" <<<"$have" && continue
  mkdir -p $S/$id
  ssh1 "tar czf - -C $N/runs $id" | tar xzf - -C $S/$id --strip-components=1
  meta=$(python3 -c 'import json, sys
d = json.load(open(sys.argv[1]))
h = d.get("hillclimb") or {}
print(json.dumps({"run_id": d["run_id"], "schema": d["schema"], "phase": d["phase"], "host": d["host"], "lane": d["lane"], "item": d["item"],
                  "question": d["question"], "label": d.get("label"), "step": d.get("step"), "commit": (d.get("tree") or {}).get("commit"),
                  "cpuset": d["cpuset"], "gpu": (d.get("gpu") or {}).get("index") or (d.get("gpu") or {}).get("cuda_visible_devices"),
                  "rc": d["rc"], "t_start": d["t_start"], "t_end": d["t_end"], "subcircuit": (h.get("subcircuit") or {}).get("id"),
                  "overhead": h.get("overhead"), "flags": h.get("flags"), "cpu_slice_others": h.get("cpu_slice_others"),
                  "affinity_clean": ((d.get("affinity_check") or {}).get("before_slot") or {}).get("clean"), "parity": d.get("parity")}))' \
    $S/$id/n2.json)
  phase=$(python3 -c 'import json, sys; d = json.load(open(sys.argv[1])); print(d["phase"], d["lane"])' $S/$id/n2.json)
  art=$(research data put --kind run-record/v1 --tree $S/$id --meta "$meta" --preserve | grep -o 'art:[0-9A-Za-z_-]*' | head -1)
  [ -n "$art" ] || { echo "$id: put failed"; exit 1; }
  case $phase in gpu\ *) label_point $id $art ;; esac
  ssh1 "printf '%s\t%s\t%s\t%s\t%s\n' $id $art $(date -u +%FT%TZ) $phase >> $N/custody.tsv"
  echo "$id $art $phase"
  new=$((new + 1))
done
total=$(grep -c . <<<"$ids" || true)
echo "custody: $new new, $total shipped to node 1"
