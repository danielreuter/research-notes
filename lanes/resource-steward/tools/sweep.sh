#!/usr/bin/env bash
# The resource steward's recurring sweep (no secrets): installs node-sweep.sh on each node and runs it as root at nice 19,
# node 2 only outside a timed window, and skips a node where a sweep is still running. Arguments pass through (--dry-run,
# --src-age-h H); --approved FILE (shas whose owners released their files outside the commit) is copied to each node, so no
# process's argv carries a sha. Every line is appended, stamped, to ~/resource-steward/deletions.log. A dropped ssh doesn't stop the node's
# sweep; its own record is the node's ~/resource-steward/node-sweep.log. Exit 0: nothing deleted; 1: something was deleted or
# is stuck (stdout lists it, for the report's Deletions section); 2: a node could not be swept, or its ssh dropped.
K=~/.ssh/research_key; S=~/resource-steward; H=$(dirname "$(readlink -f "$0")"); rc=0; mkdir -p $S
NS=$H/node-sweep.sh; [ -f $NS ] || NS=~/.research/notes/lanes/resource-steward/tools/node-sweep.sh
SSH=(ssh -i $K -o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o ServerAliveCountMax=20)
AP=/dev/null; ARGS=()
while [ $# -gt 0 ]; do case $1 in --approved) AP=$2; shift;; *) ARGS+=("$1");; esac; shift; done
[ -r $AP ] || { echo "sweep: cannot read $AP"; exit 2; }
sweep() {  # host node
  local o r
  if [ $2 = n2 ] && timeout 60 "${SSH[@]}" research@$1 'grep -q "timed True" /workspace/pouw/fill/status.txt'; then
    echo "$2: timed window, sweep skipped"; return; fi
  if timeout 60 "${SSH[@]}" research@$1 'pgrep -f "[n]ode-sweep.sh" >/dev/null'; then
    echo "$2: a sweep is already running there, skipped"; return; fi
  timeout 120 "${SSH[@]}" research@$1 \
    'mkdir -p ~/resource-steward/bin && cat > ~/resource-steward/bin/.node-sweep.sh.new && chmod 755 ~/resource-steward/bin/.node-sweep.sh.new && mv ~/resource-steward/bin/.node-sweep.sh.new ~/resource-steward/bin/node-sweep.sh' < $NS \
    || { echo "$2: FAILED to install node-sweep.sh"; rc=2; return; }
  timeout 60 "${SSH[@]}" research@$1 'cat > ~/resource-steward/approved.txt' < $AP || { echo "$2: FAILED to copy the approved list"; rc=2; return; }
  o=$(timeout 3600 "${SSH[@]}" research@$1 "sudo -n nice -n 19 ionice -c3 ~/resource-steward/bin/node-sweep.sh $3 --approved /home/research/resource-steward/approved.txt" 2>&1); r=$?
  printf '%s\n' "$o" | sed "/^$/d; s/^/$(date -u +%FT%TZ) $2 /" >> $S/deletions.log
  printf '%s\n' "$o" | sed "/^$/d; s/^/$2: /"
  [ $r = 255 ] && { echo "$2: FAILED, ssh dropped; the sweep goes on there and ~/resource-steward/node-sweep.log on the node records it"; rc=2; return; }
  [ $r -ne 0 ] && { echo "$2: FAILED node-sweep rc=$r"; rc=2; return; }
  printf '%s\n' "$o" | grep -qE '^(deleted|STUCK)' && [ $rc = 0 ] && rc=1
}
sweep 81.85.2.165 n1 "${ARGS[*]}"
sweep 81.85.2.121 n2 "${ARGS[*]}"
exit $rc
