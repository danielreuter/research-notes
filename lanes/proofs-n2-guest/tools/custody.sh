#!/usr/bin/env bash
# proofs-n2-guest custody, run from an agent VM with a configured research CLI (node 2 has none, and no credentials go to a node).
# Node 2's refill loop rsyncs each verified job (its run dir and done/<id>.json) to vy-nebius-1 /workspace/jobs/proofs-n2-guest/; this
# puts each one not yet in node 1's custody.tsv as a run-record/v1 artifact, preserved on the remote, and appends `<id> <art> <utc>`.
set -euo pipefail
export PATH=/workspace/.venv/bin:$PATH RESEARCH_NOTES=$HOME/.research/notes RESEARCH_MACHINES_D=$HOME/.research/notes/machines.d
N=/workspace/jobs/proofs-n2-guest
S=$(mktemp -d)
trap 'rm -rf $S' EXIT
ssh1() { research pods ssh vy-nebius-1 -- "$@"; }
have=$(ssh1 "mkdir -p $N/done && touch $N/custody.tsv && cut -f1 $N/custody.tsv")
ids=$(ssh1 "ls $N/done | sed -n 's/\.json\$//p'")
new=0
for id in $ids; do
  grep -qx "$id" <<<"$have" && continue
  mkdir -p $S/$id
  ssh1 "tar czf - -C $N runs/$id done/$id.json" | tar xzf - -C $S/$id
  meta=$(python3 -c 'import json, sys
d = json.load(open(sys.argv[1]))
print(json.dumps({k: d.get(k) for k in ("id", "kind", "row", "shape", "shape_index", "start", "count", "end", "gate", "node", "gpu", "label",
                                         "job_s", "t_start", "t_end", "e2e_s_per_statement", "lane", "owner", "question", "env_check")}))' \
    $S/$id/done/$id.json)
  art=$(research data put --kind run-record/v1 --tree $S/$id --meta "$meta" --preserve | grep -o 'art:[0-9A-Za-z_-]*' | head -1)
  [ -n "$art" ] || { echo "$id: put failed"; exit 1; }
  ssh1 "printf '%s\t%s\t%s\n' $id $art $(date -u +%FT%TZ) >> $N/custody.tsv"
  echo "$id $art"
  new=$((new + 1))
done
total=$(grep -c . <<<"$ids" || true)
echo "custody: $new new, $total verified on node 1"
