#!/usr/bin/env bash
# One resource-steward tick (no secrets). Exit 0: every metric under its watermark and no new resource alert note; the turn
# ends silently. Exit 1: lines on stdout to act on: a breach whose kind wasn't in the last tick (numbers ignored, GPU index
# kept), any HARD stop, a failed probe, or a new alert note. Known breaches print under "known:" and exit 0.
# 1. the probe (infra/nebius tools/research/src/research/pods/nebius/resource_probe.py, deployed at ~/resource-steward/bin/)
#    on each node at nice 19; node 2 is skipped while fill/status.txt says `timed True`.
# 2. new *alert* notes in lanes/{infra,node2-ops,resource-steward}/ since the last tick: every one in resource-steward/, and
#    the others only when their name is about disk, RAM, inodes, OOM or space.
K=~/.ssh/research_key; rc=0; S=~/resource-steward; mkdir -p $S
out=""
probe() {  # host node precheck
  local o r
  o=$(timeout 60 ssh -i $K -o BatchMode=yes -o ConnectTimeout=15 research@$1 "$3 nice -n 19 ionice -c3 python3 ~/resource-steward/bin/resource_probe.py --node $2" 2>&1); r=$?
  [ -n "$o" ] && out+="$o"$'\n'
  [ $r -gt 1 ] && { out+="$2: FAILED probe rc=$r"$'\n'; }
}
probe 81.85.2.165 n1 ""
probe 81.85.2.121 n2 'if grep -q "timed True" /workspace/pouw/fill/status.txt; then echo "n2: timed window, probe skipped"; exit 0; fi;'
key() { sed -E 's/^n1:/NODE_A:/; s/^n2:/NODE_B:/; s/GPU ([0-9]+)/GPU_\1/; s/[0-9][0-9.,]*/#/g'; }
touch $S/breaches.last; : > $S/breaches.now
while IFS= read -r l; do
  [ -z "$l" ] && continue; k=$(printf %s "$l" | key); echo "$k" >> $S/breaches.now
  if grep -qxF "$k" $S/breaches.last && ! printf %s "$l" | grep -qE 'HARD|FAILED'; then echo "known: $l"; else echo "$l"; rc=1; fi
done <<< "$out"
mv $S/breaches.now $S/breaches.last
N=~/.research/notes
git -C $N -c credential.helper= pull -q --rebase --autostash https://github.com/danielreuter/research-notes.git main >/dev/null 2>&1
W=$S/alerts.seen; touch $W
for f in $N/lanes/resource-steward/*alert* $N/lanes/infra/*alert* $N/lanes/node2-ops/*alert*; do
  [ -f "$f" ] || continue; b=$(basename "$f")
  grep -qxF "$b" $W && continue
  echo "$b" >> $W
  case "$f" in */resource-steward/*) ;; *) echo "$b" | grep -qiE 'disk|ram|mem|inode|oom|space|cache' || continue;; esac
  echo "alert note: ${f#$N/}"; rc=1
done
exit $rc
