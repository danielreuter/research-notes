#!/usr/bin/env bash
# The resource steward's recurring sweep (no secrets): installs node-sweep.sh on each node and runs it as root at nice 19,
# node 2 only outside a timed window. Arguments pass through (--dry-run, --src-age-h H). Every line is appended, stamped, to
# ~/resource-steward/deletions.log. Exit 0: nothing deleted; 1: something was deleted or is stuck (stdout lists it, for the
# report's Deletions section); 2: a node could not be swept.
K=~/.ssh/research_key; S=~/resource-steward; H=$(dirname "$(readlink -f "$0")"); rc=0; mkdir -p $S
NS=$H/node-sweep.sh; [ -f $NS ] || NS=~/.research/notes/lanes/resource-steward/tools/node-sweep.sh
sweep() {  # host node
  local o r
  if [ $2 = n2 ] && timeout 60 ssh -i $K -o BatchMode=yes -o ConnectTimeout=15 research@$1 'grep -q "timed True" /workspace/pouw/fill/status.txt'; then
    echo "$2: timed window, sweep skipped"; return; fi
  timeout 120 ssh -i $K -o BatchMode=yes -o ConnectTimeout=15 research@$1 \
    'mkdir -p ~/resource-steward/bin && cat > ~/resource-steward/bin/.node-sweep.sh.new && chmod 755 ~/resource-steward/bin/.node-sweep.sh.new && mv ~/resource-steward/bin/.node-sweep.sh.new ~/resource-steward/bin/node-sweep.sh' < $NS \
    || { echo "$2: FAILED to install node-sweep.sh"; rc=2; return; }
  o=$(timeout 3600 ssh -i $K -o BatchMode=yes -o ConnectTimeout=15 research@$1 "sudo -n nice -n 19 ionice -c3 ~/resource-steward/bin/node-sweep.sh $3" 2>&1); r=$?
  printf '%s\n' "$o" | sed "/^$/d; s/^/$(date -u +%FT%TZ) $2 /" >> $S/deletions.log
  printf '%s\n' "$o" | sed "/^$/d; s/^/$2: /"
  [ $r -ne 0 ] && { echo "$2: FAILED node-sweep rc=$r"; rc=2; return; }
  printf '%s\n' "$o" | grep -qE '^(deleted|STUCK)' && [ $rc = 0 ] && rc=1
}
sweep 81.85.2.165 n1 "$*"
sweep 81.85.2.121 n2 "$*"
exit $rc
