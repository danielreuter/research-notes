#!/usr/bin/env bash
# The resource steward's recurring sweep (no secrets): installs node-sweep.sh on each node and runs it as root at nice 19,
# node 2 only outside a timed window, and skips a node where a sweep is still running. Arguments pass through (--dry-run,
# --src-age-h H); --approved FILE (shas whose owners released their files outside the commit) is copied to each node, so no
# process's argv carries a sha. Every line is appended, stamped, to ~/resource-steward/deletions.log. A dropped ssh doesn't stop the node's
# sweep; its own record is the node's ~/resource-steward/node-sweep.log. Exit 0: nothing deleted; 1: something was deleted or
# is stuck (stdout lists it, for the report's Deletions section); 2: a node could not be swept, or its ssh dropped.
# Node 1 also sweeps infra's /workspace/jobs/src (--jobs-src), which Daniel approved on 2 Oct (report §5), and the Lean
# dependencies failed audits leave in its source trees (--lake, Daniel's card 23a10e51, 2 Oct).
# On node 1, a tree whose only change from its commit is the soundness lean-audit.json (proofs' audit trees; their option
# (b), 06:35Z 3 Oct, #agent-coordination 1791009304.937289) is approved only after that file is preserved in the store
# (one evidence/v1 artifact per sweep, named on stdout); node-sweep.sh's age and liveness checks still decide.
# The body is one function, called on the last line: bash parses all of it before running, so editing this file during a
# sweep cannot change what that sweep runs.
main() {
K=~/.ssh/research_key; S=~/resource-steward; H=$(dirname "$(readlink -f "$0")"); rc=0; mkdir -p $S
NS=$H/node-sweep.sh; [ -f $NS ] || NS=~/.research/notes/lanes/resource-steward/tools/node-sweep.sh
SSH=(ssh -i $K -o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=30 -o ServerAliveCountMax=20)
AP=/dev/null; ARGS=(); AGE=24; DRY=0
while [ $# -gt 0 ]; do case $1 in --approved) AP=$2; shift;; --src-age-h) AGE=$2; ARGS+=("$1" "$2"); shift;;
  --dry-run) DRY=1; ARGS+=("$1");; *) ARGS+=("$1");; esac; shift; done
[ -r $AP ] || { echo "sweep: cannot read $AP"; exit 2; }
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
LA=backends/flock/verifier/lean/soundness/lean-audit.json
la_save() {  # host node: writes $T/la.ok (shas whose lean-audit.json is preserved) and prints one line
  local d=$T/la out art n
  : > $T/la.ok
  timeout 900 "${SSH[@]}" research@$1 "bash -s $AGE $LA" > $T/la.shas <<'EOF' || { echo "$2: FAILED to list the lean-audit.json trees; none approved"; rc=2; return; }
now=$(date +%s)
for d in /workspace/research/src/*/; do d=${d%/}; s=${d##*/}
  [[ $s =~ ^[0-9a-f]{40}$ ]] || continue
  [ $(( (now - $(stat -c %Y $d)) / 3600 )) -ge $1 ] || continue
  [ "$(cd $d && GIT_OPTIONAL_LOCKS=0 git -c safe.directory='*' status --porcelain 2>/dev/null)" = " M $2" ] && echo $s
done
exit 0
EOF
  n=$(grep -c . $T/la.shas); [ $n = 0 ] && return
  [ $DRY = 1 ] && { cp $T/la.shas $T/la.ok; echo "$2: would save $n lean-audit.json files to the store, then approve their trees"; return; }
  mkdir -p $d
  sed "s|\$|/$LA|" $T/la.shas | timeout 600 "${SSH[@]}" research@$1 'cd /workspace/research/src && tar -cf - -T -' | tar -xf - -C $d
  [ $(find $d -name lean-audit.json | wc -l) = $n ] || { echo "$2: FAILED to copy $n lean-audit.json files; none approved"; rc=2; return; }
  python3 -c 'import json,sys; json.dump({"what": "modified soundness lean-audit.json of node 1 source trees, saved before the trees were deleted", "layout": "<sha>/'$LA'", "node": "'$2'", "trees": sys.argv[1:], "by": "resource-steward", "owner": "proofs", "ruling": "slack C0C5RCXL66N 1791009304.937289, option (b)"}, open("'$T/la.meta'", "w"))' $(cat $T/la.shas)
  out=$(cd ~/wt/slack && uv run --no-sync research data put --kind evidence/v1 --tree $d --meta @$T/la.meta --preserve --json 2>/dev/null)
  art=$(printf '%s' "$out" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["id"] if (d.get("preserve") or {}).get("preserved") else "")' 2>/dev/null)
  [ -n "$art" ] || { echo "$2: FAILED to preserve $n lean-audit.json files; none approved"; rc=2; return; }
  cp $T/la.shas $T/la.ok; echo "$2: saved $n lean-audit.json files as $art"
}
sweep() {  # host node args [approved file]
  local o r
  if [ $2 = n2 ] && ! timeout 60 "${SSH[@]}" research@$1 'grep -qs "timed False" /workspace/pouw/fill/status.txt'; then
    echo "$2: fill/status.txt does not say timed False (a timed window, a cutover, or no ssh), sweep skipped"; return; fi
  if timeout 60 "${SSH[@]}" research@$1 'pgrep -f "[n]ode-sweep.sh" >/dev/null'; then
    echo "$2: a sweep is already running there, skipped"; return; fi
  timeout 120 "${SSH[@]}" research@$1 \
    'mkdir -p ~/resource-steward/bin && cat > ~/resource-steward/bin/.node-sweep.sh.new && chmod 755 ~/resource-steward/bin/.node-sweep.sh.new && mv ~/resource-steward/bin/.node-sweep.sh.new ~/resource-steward/bin/node-sweep.sh' < $NS \
    || { echo "$2: FAILED to install node-sweep.sh"; rc=2; return; }
  timeout 60 "${SSH[@]}" research@$1 'cat > ~/resource-steward/approved.txt' < ${4:-$AP} || { echo "$2: FAILED to copy the approved list"; rc=2; return; }
  o=$(timeout 3600 "${SSH[@]}" research@$1 "sudo -n nice -n 19 ionice -c3 ~/resource-steward/bin/node-sweep.sh $3 --approved /home/research/resource-steward/approved.txt" 2>&1); r=$?
  printf '%s\n' "$o" | sed "/^$/d; s/^/$(date -u +%FT%TZ) $2 /" >> $S/deletions.log
  printf '%s\n' "$o" | sed "/^$/d; s/^/$2: /"
  [ $r = 255 ] && { echo "$2: FAILED, ssh dropped; the sweep goes on there and ~/resource-steward/node-sweep.log on the node records it"; rc=2; return; }
  [ $r -ne 0 ] && { echo "$2: FAILED node-sweep rc=$r"; rc=2; return; }
  printf '%s\n' "$o" | grep -qE '^(deleted|STUCK)' && [ $rc = 0 ] && rc=1
}
la_save 81.85.2.165 n1; { cat $AP; echo; cat $T/la.ok; } > $T/ap1
sweep 81.85.2.165 n1 "${ARGS[*]} --jobs-src --lake" $T/ap1
sweep 81.85.2.121 n2 "${ARGS[*]}"
exit $rc
}
main "$@"
