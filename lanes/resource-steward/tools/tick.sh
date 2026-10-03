#!/usr/bin/env bash
# One resource-steward tick (no secrets). Exit 0: every metric under its watermark and no new resource alert note; the turn
# ends silently. Exit 1: lines on stdout to act on: a breach whose kind wasn't seen in the last 6 h (numbers ignored, GPU index
# kept), any HARD stop, a failed probe, or a new alert note. Known breaches print under "known:" and exit 0.
# 1. the probe (infra/nebius tools/research/src/research/pods/nebius/resource_probe.py, deployed at ~/resource-steward/bin/)
#    on each node at nice 19; node 2 is probed only while fill/status.txt says `timed False` (a missing or unreadable
#    status, as during a cutover, skips it).
# 2. new *alert* notes in lanes/{infra,node2-ops,resource-steward}/ since the last tick: every one in resource-steward/, and
#    the others only when their name is about disk, RAM, inodes, OOM or space.
# 3. node 1's Lean audit gate (to 08:00Z 4 Oct): one line when its inodes pass 70% and one when back under 65%.
K=~/.ssh/research_key; rc=0; S=~/resource-steward; mkdir -p $S
out=""
probe() {  # host node precheck
  local o r
  o=$(timeout 60 ssh -i $K -o BatchMode=yes -o ConnectTimeout=15 research@$1 "$3 nice -n 19 ionice -c3 python3 ~/resource-steward/bin/resource_probe.py --node $2" 2>&1); r=$?
  [ -n "$o" ] && out+="$o"$'\n'
  [ $r -gt 1 ] && { out+="$2: FAILED probe rc=$r"$'\n'; }
}
probe 81.85.2.165 n1 ""
probe 81.85.2.121 n2 'if ! grep -qs "timed False" /workspace/pouw/fill/status.txt; then grep -qs "timed True" /workspace/pouw/fill/status.txt && echo "n2: timed window, probe skipped" || echo "n2: fill/status.txt does not say timed False, probe skipped"; exit 0; fi;'
key() { sed -E 's/^n1:/NODE_A:/; s/^n2:/NODE_B:/; s/GPU ([0-9]+)/GPU<\1>/; s/(^|[^<0-9])[0-9][0-9.,]*/\1#/g'; }
touch $S/breaches.seen; now=$(date +%s); : > $S/breaches.new
while IFS= read -r l; do
  [ -z "$l" ] && continue; k=$(printf %s "$l" | key); echo "$now $k" >> $S/breaches.new
  if awk -v k="$k" -v t=$((now - 21600)) '{ s=$1; $1=""; sub(/^ /,""); if ($0==k && s>=t) f=1 } END { exit !f }' $S/breaches.seen \
     && ! printf %s "$l" | grep -qE 'HARD|FAILED'; then echo "known: $l"; else echo "$l"; rc=1; fi
done <<< "$out"
awk -v t=$((now - 21600)) '$1>=t' $S/breaches.seen $S/breaches.new > $S/breaches.tmp; mv $S/breaches.tmp $S/breaches.seen
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
# Node 1's Lean audit gate (infra, #agent-coordination thread 1791010653.061919, 16:25Z 3 Oct, until 08:00Z 4 Oct): past
# 70% inodes, new audits on both sides wait; back under 65%, they resume. The steward posts each change in that thread.
G=$S/audit-gate
if [ $now -lt $(date -d 2026-10-04T08:00Z +%s) ]; then
  ip=$(timeout 30 ssh -i $K -o BatchMode=yes -o ConnectTimeout=15 research@81.85.2.165 'df --output=iused,itotal /workspace | tail -1' 2>/dev/null \
       | awk 'NF==2 && $2>0 {printf "%.2f", 100*$1/$2}')
  if [ -z "$ip" ]; then echo "n1: FAILED audit-gate inode read"; rc=1
  elif [ ! -f $G ] && awk -v p=$ip 'BEGIN{exit !(p>70)}'; then touch $G; rc=1
    echo "n1: AUDIT GATE closed: /workspace inodes $ip% > 70%; post the wait line in the audit thread"
  elif [ -f $G ] && awk -v p=$ip 'BEGIN{exit !(p<65)}'; then rm -f $G; rc=1
    echo "n1: AUDIT GATE open: /workspace inodes $ip% < 65%; post the resume line in the audit thread"
  fi
fi
exit $rc
