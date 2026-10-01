#!/usr/bin/env bash
# proofs-n2-hill custody, run from an agent VM with a configured research CLI (node 2 has none, and no credentials go to a node).
# Node 2's loop (n2h.py) rsyncs each finished attempt's run dir to vy-nebius-1 /workspace/jobs/proofs-n2-hill/runs/<id>/ (with its
# n2.json); this puts each one not yet in node 1's custody.tsv into the evidence store as a run-record/v1 artifact, preserved on
# the remote, and appends `<id> <art> <utc> <phase> <lane>` there.
set -euo pipefail
export PATH=/workspace/.venv/bin:$PATH RESEARCH_NOTES=$HOME/.research/notes RESEARCH_MACHINES_D=$HOME/.research/notes/machines.d
N=/workspace/jobs/proofs-n2-hill
S=$(mktemp -d)
trap 'rm -rf $S' EXIT
ssh1() { research pods ssh vy-nebius-1 -- "$@"; }
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
  ssh1 "printf '%s\t%s\t%s\t%s\t%s\n' $id $art $(date -u +%FT%TZ) $phase >> $N/custody.tsv"
  echo "$id $art $phase"
  new=$((new + 1))
done
total=$(grep -c . <<<"$ids" || true)
echo "custody: $new new, $total shipped to node 1"
