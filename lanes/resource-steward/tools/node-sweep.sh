#!/bin/bash
# The resource steward's delete-without-asking sweep, run ON a node as root (`sudo nice -n 19 ionice -c3 node-sweep.sh`).
# Usage: node-sweep.sh [--dry-run] [--src-age-h H]. Per the policy in lanes/resource-steward/*-report-resource-steward.md:
#  - /workspace/research/src/<sha> trees whose directory is older than H h (default 24), unless something live names the sha:
#    a request not yet finished (no terminal status.json and a runner that is alive or not yet launched), a Kueue workload not
#    finished, a pod not finished, a fill job queued or running, or any process (cwd, root, open files, maps, argv, environment).
#    A tree is renamed into src/.trash/ first (one rename, so the launcher never sees a half-deleted READY tree), scanned again,
#    and put back if anything names it now;
#  - check scratch untouched for 2 h and not held open: /tmp/pytest-of-research/pytest-*, <verity-check cache>/lean-audit-scratch-*.
# Prints "deleted PATH files=N mb=M age=Xh" or "kept PATH: why" per candidate. Exit 0, or 2 if not root.
# Patterns go through files (grep -f), so no scanner process carries one in its argv or environment.
[ "$(id -u)" = 0 ] || { echo "node-sweep: needs root to read every process" >&2; exit 2; }
DRY=0; AGE_H=24
while [ $# -gt 0 ]; do case $1 in --dry-run) DRY=1;; --src-age-h) AGE_H=$2; shift;; *) echo "unknown $1" >&2; exit 2;; esac; shift; done
R=/workspace/research; SRC=$R/src; TRASH=$SRC/.trash; now=$(date +%s); T=$(mktemp -d); trap 'rm -rf $T' EXIT
age_h() { echo $(( (now - $(stat -c %Y "$1")) / 3600 )); }

refs() {  # PATTERNS_FILE -> "<pattern> <ref>" lines for every live reference
  local pf=$1 q id st pid d p
  for q in $R/requests/r2*; do id=${q##*/}
    st=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("state",""))' $R/runs/$id/status.json 2>/dev/null)
    case $st in done|failed|cancelled|exited|timeout|timed_out) continue;; esac
    pid=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("runner_pid",""))' $R/runs/$id/launch.json 2>/dev/null)
    [ -f $R/runs/$id/launch.json ] && ! { [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; } && continue
    cat "$q"/* $R/runs/$id/launch.json $R/runs/$id/job.json 2>/dev/null | grep -oF -f $pf | sort -u | sed "s|\$| request:$id|"
  done
  if command -v k3s >/dev/null; then
    for kind in pods workloads.kueue.x-k8s.io; do
      k3s kubectl get $kind -A -o json 2>/dev/null | python3 -c '
import json,sys
pats=open(sys.argv[1]).read().split(); kind=sys.argv[2]
for o in json.load(sys.stdin).get("items", []):
    st=o.get("status", {})
    if st.get("phase") in ("Succeeded", "Failed"): continue
    if any(c.get("type")=="Finished" and c.get("status")=="True" for c in st.get("conditions", [])): continue
    s=json.dumps(o.get("spec", {}))
    for p in pats:
        if p in s: print(p, kind.split(".")[0] + ":" + o["metadata"]["name"])' $pf $kind
    done
  fi
  for f in /workspace/pouw/fill/queue/* /workspace/pouw/fill/running/*; do
    [ -f "$f" ] && grep -oF -f $pf "$f" | sort -u | sed "s|\$| fill:${f#/workspace/pouw/fill/}|"
  done
  for d in /proc/[0-9]*; do p=${d#/proc/}; [ "$p" = $$ ] && continue
    { readlink $d/cwd; readlink $d/root; ls -l $d/fd; cat $d/maps; tr '\0' ' ' < $d/cmdline; echo; tr '\0' '\n' < $d/environ; } 2>/dev/null \
      | grep -oF -f $pf | sort -u | sed "s|\$| proc:$p($(cat $d/comm 2>/dev/null))|"
  done
}

held() { refs $1 | awk '{a[$1]=a[$1]" "$2} END{for (k in a) print k a[k]}'; }  # PATTERNS_FILE -> "<pattern> <refs...>"
gone() { local p=$1 n m a; n=$(find "$p" -xdev 2>/dev/null | wc -l); m=$(du -sm --one-file-system "$p" 2>/dev/null | cut -f1); a=$2
  if [ $DRY = 1 ]; then echo "would delete $3 files=$n mb=$m age=${a}h"; else rm -rf --one-file-system -- "$p" && echo "deleted $3 files=$n mb=$m age=${a}h"; fi; }

# source trees
: > $T/src
for d in $SRC/*/; do d=${d%/}; s=${d##*/}
  [[ $s =~ ^[0-9a-f]{40}$ ]] || continue
  [ $(age_h $d) -ge $AGE_H ] && echo $s >> $T/src
done
if [ -s $T/src ]; then
  held $T/src > $T/held
  for s in $(cat $T/src); do
    r=$(awk -v s=$s '$1==s{$1=""; print substr($0,2)}' $T/held)
    [ -n "$r" ] && { echo "kept $SRC/$s: $r"; continue; }
    a=$(age_h $SRC/$s)
    [ $DRY = 1 ] && { gone $SRC/$s $a $SRC/$s; continue; }
    mkdir -p $TRASH; t=$TRASH/$s-$now
    mv -T $SRC/$s $t || { echo "kept $SRC/$s: rename failed"; continue; }
    echo $s > $T/one; r=$(held $T/one | cut -d' ' -f2-)
    if [ -n "$r" ]; then mv -T $t $SRC/$s && echo "kept $SRC/$s: named after rename: $r" || echo "STUCK $t: named after rename ($r) and could not be put back"; continue; fi
    gone $t $a $SRC/$s
  done
fi

# check scratch
: > $T/scr
cache=$(readlink -f /home/research/.cache/verity-check)
for d in /tmp/pytest-of-research/pytest-[0-9]* $cache/lean-audit-scratch-*; do
  [ -d "$d" ] && [ ! -L "$d" ] || continue
  [ -z "$(find "$d" -xdev -newermt '-2 hours' -print -quit 2>/dev/null)" ] && echo "$d" >> $T/scr
done
if [ -s $T/scr ]; then
  held $T/scr > $T/held
  for d in $(cat $T/scr); do
    r=$(awk -v s="$d" '$1==s{$1=""; print substr($0,2)}' $T/held)
    [ -n "$r" ] && { echo "kept $d: $r"; continue; }
    gone "$d" $(age_h "$d") "$d"
  done
fi
exit 0
