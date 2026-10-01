#!/bin/bash
# The resource steward's delete-without-asking sweep, run ON a node as root (`sudo nice -n 19 ionice -c3 node-sweep.sh`).
# Usage: node-sweep.sh [--dry-run] [--src-age-h H]. Per the policy in lanes/resource-steward/*-report-resource-steward.md:
#  - /workspace/research/src/<sha> trees whose directory is older than H h (default 24), unless something live names the sha
#    (REFS_PY: a request not yet finished or refused whose runner is alive or not yet launched, a Kueue workload or pod not finished, a
#    fill job queued or running, any process's cwd, root, open files, maps, argv or environment), and unless the tree holds
#    files outside its commit (EXTRA_PY), which may be a run's output. The trees that pass are renamed into src/.trash/ (one
#    rename each, so the launcher never sees a half-deleted READY tree), scanned once more together, put back if anything
#    names them now, and deleted;
#  - src/.trash/ entries an interrupted sweep left (decided already; nothing executes from there);
#  - check scratch untouched for 2 h and not held open: /tmp/pytest-of-research/pytest-*, <verity-check cache>/lean-audit-scratch-*.
# Prints "deleted PATH files=N mb=M age=Xh" or "kept PATH: why" per candidate, each line first appended, stamped, to $LOG (not
# in a dry run), and goes on to the end when its ssh drops (SIGPIPE ignored), so $LOG is the record of what it did.
# Exit 0, or 2 if not root or already running. Patterns go through files, so no scanner process carries one in its argv or
# environment.
[ "$(id -u)" = 0 ] || { echo "node-sweep: needs root to read every process" >&2; exit 2; }
exec 9>/run/lock/resource-steward-sweep.lock; flock -n 9 || { echo "node-sweep: another sweep is running" >&2; exit 2; }
DRY=0; AGE_H=24
while [ $# -gt 0 ]; do case $1 in --dry-run) DRY=1;; --src-age-h) AGE_H=$2; shift;; *) echo "unknown $1" >&2; exit 2;; esac; shift; done
R=/workspace/research; SRC=$R/src; TRASH=$SRC/.trash; now=$(date +%s); T=$(mktemp -d); trap 'rm -rf $T' EXIT; trap '' PIPE
LOG=/home/research/resource-steward/node-sweep.log
say() { [ $DRY = 1 ] || printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" >> $LOG; echo "$*" 2>/dev/null; return 0; }
age_h() { echo $(( (now - $(stat -c %Y "$1")) / 3600 )); }

REFS_PY='
import glob, json, os, re, subprocess, sys
pats = open(sys.argv[1]).read().split(); R = "/workspace/research"; me = {str(os.getpid()), str(os.getppid())}
TERMINAL = {"done", "failed", "cancelled", "exited", "timeout", "timed_out", "refused"}
# a path names itself or what is under it (pytest-1 is not pytest-12); a sha names any path that carries it
rx = {p: re.compile(re.escape(p) + r"(?![^/\s])") for p in pats if p.startswith("/")}
def hit(text, ref):
    for p in pats:
        if (rx[p].search(text) if p in rx else p in text): print(p, ref)
def load(path):
    try: return json.load(open(path))
    except Exception: return {}
def read(path):
    try: return open(path, errors="replace").read()
    except Exception: return ""
for q in sorted(glob.glob(R + "/requests/r2*")):
    rid = os.path.basename(q); run = f"{R}/runs/{rid}"
    # a refused request never runs: relaunching its id returns the same refusal
    if load(run + "/status.json").get("state", "") in TERMINAL or os.path.exists(run + "/refused.json"): continue
    if os.path.exists(run + "/launch.json"):
        pid = str(load(run + "/launch.json").get("runner_pid") or "")
        if not pid or not os.path.exists("/proc/" + pid): continue
    hit("".join(read(f) for f in [*glob.glob(q + "/*"), run + "/launch.json", run + "/job.json"]), "request:" + rid)
if subprocess.run(["sh", "-c", "command -v k3s"], capture_output=True).returncode == 0:
    for kind in ("pods", "workloads.kueue.x-k8s.io"):
        out = subprocess.run(["k3s", "kubectl", "get", kind, "-A", "-o", "json"], capture_output=True, text=True)
        if out.returncode: print("FAILED", "kubectl get " + kind); continue
        for o in json.loads(out.stdout).get("items", []):
            st = o.get("status", {})
            if st.get("phase") in ("Succeeded", "Failed"): continue
            if any(c.get("type") == "Finished" and c.get("status") == "True" for c in st.get("conditions", [])): continue
            hit(json.dumps(o.get("spec", {})), kind.split(".")[0] + ":" + o["metadata"]["name"])
for f in glob.glob("/workspace/pouw/fill/queue/*") + glob.glob("/workspace/pouw/fill/running/*"):
    hit(read(f), "fill:" + f.split("/workspace/pouw/fill/")[1])
for p in os.listdir("/proc"):
    if not p.isdigit() or p in me: continue
    d = "/proc/" + p; parts = []
    for link in ("cwd", "root"):
        try: parts.append(os.readlink(f"{d}/{link}"))
        except OSError: pass
    try: parts += [os.readlink(f"{d}/fd/{fd}") for fd in os.listdir(d + "/fd")]
    except OSError: pass
    for f in ("maps", "cmdline", "environ"):
        try: parts.append(open(f"{d}/{f}", "rb").read().decode(errors="replace").replace("\0", " "))
        except OSError: pass
    comm = read(d + "/comm").strip()
    hit("\n".join(parts), f"proc:{p}({comm})")
'
held() { python3 -c "$REFS_PY" $1 | awk '{a[$1]=a[$1]" "$2} END{for (k in a) print k a[k]}'; }  # PATTERNS_FILE -> "<pattern> <refs...>"
named() { awk -v s="$1" '$1==s{$1=""; print substr($0,2)}' $2; }

# A tree that holds anything besides its commit's files, build caches and registered fixtures (fixtures/artifacts.json, files
# or directories, which fetch-fixtures restores) may hold a run's output, so it is kept: untracked or ignored files
# (.gitignore also hides results/, outputs/ and the like), modified tracked files, or, in a tree shipped without .git, files
# the bare repo's commit lacks or files changed after READY.json. Exit 1 with a reason when it holds any, or when it can't tell.
EXTRA_PY='
import json, os, re, subprocess, sys
tree = sys.argv[1]; bare = "/workspace/research/git/verity.git"
CACHE = re.compile(r"(^|/)(\.venv|\.lake|__pycache__|\.pytest_cache|\.ruff_cache|\.mypy_cache|\.hypothesis|node_modules|target|[^/]*\.egg-info)(/|$)|\.pyc$|^READY\.json$|^integrations/vllm/verity_vllm/program/kernels/cpp/build(/|$)")
try: reg = {v for k, v in json.load(open(os.path.join(tree, "fixtures/artifacts.json"))).items() if k.startswith("art:") and isinstance(v, str)}
except FileNotFoundError: reg = set()
extra = []
def files(rel):
    p = os.path.join(tree, rel)
    if not os.path.isdir(p) or os.path.islink(p): yield rel; return
    for dp, dns, fns in os.walk(p):
        r = os.path.relpath(dp, tree)
        dns[:] = [d for d in dns if not CACHE.search(os.path.normpath(os.path.join(r, d)) + "/")]
        for f in fns: yield os.path.normpath(os.path.join(r, f))
def keep(rel): return not CACHE.search(rel) and not any(rel == r or rel.startswith(r.rstrip("/") + "/") for r in reg)
if os.path.isdir(os.path.join(tree, ".git")):
    st = subprocess.run(["git", "-C", tree, "status", "--porcelain", "--ignored", "-z", "--untracked-files=normal"], capture_output=True)
    if st.returncode: print("git status failed"); sys.exit(1)
    for e in st.stdout.split(b"\0"):
        if not e: continue
        code, rel = e[:2].decode(), os.path.normpath(e[3:].decode(errors="replace"))
        if code in ("??", "!!"):
            if not CACHE.search(rel + "/"): extra += [f for f in files(rel) if keep(f)]
        else: extra.append(code.strip() + " " + rel)
else:
    ls = subprocess.run(["git", "--git-dir", bare, "ls-tree", "-r", "--name-only", "-z", os.path.basename(tree)], capture_output=True)
    if ls.returncode: print("no .git, and the bare repo lacks the commit"); sys.exit(1)
    tracked = {x.decode() for x in ls.stdout.split(b"\0") if x}
    try: shipped = os.stat(os.path.join(tree, "READY.json")).st_mtime + 60
    except OSError: print("no READY.json"); sys.exit(1)
    for f in files("."):
        if f in tracked:
            if os.lstat(os.path.join(tree, f)).st_mtime > shipped: extra.append("changed " + f)
        elif keep(f): extra.append(f)
if extra: print(f"{len(extra)} file(s) outside the commit: " + ", ".join(extra[:3])); sys.exit(1)
'
gone() { local p=$1 n m; n=$(find "$p" -xdev 2>/dev/null | wc -l); m=$(du -sm --one-file-system "$p" 2>/dev/null | cut -f1)
  if [ $DRY = 1 ]; then say "would delete $3 files=$n mb=$m age=${2}h"; else rm -rf --one-file-system -- "$p" && say "deleted $3 files=$n mb=$m age=${2}h"; fi; }

# what an interrupted sweep left in src/.trash
[ $DRY = 0 ] && for t in $TRASH/*; do [ -d "$t" ] || continue; gone "$t" $(age_h "$t") "$t (left by an interrupted sweep)"; done

# source trees
: > $T/src
for d in $SRC/*/; do d=${d%/}; s=${d##*/}
  [[ $s =~ ^[0-9a-f]{40}$ ]] || continue
  [ $(age_h $d) -ge $AGE_H ] && echo $s >> $T/src
done
if [ -s $T/src ]; then
  held $T/src > $T/held
  grep -q '^FAILED' $T/held && { echo "node-sweep: $(grep '^FAILED' $T/held | head -1); no source tree deleted" >&2; exit 2; }
  : > $T/moved
  for s in $(cat $T/src); do
    r=$(named $s $T/held); [ -n "$r" ] && { say "kept $SRC/$s: $r"; continue; }
    x=$(cd /tmp && GIT_OPTIONAL_LOCKS=0 runuser -u research -- python3 -c "$EXTRA_PY" $SRC/$s 2>&1) || { say "kept $SRC/$s: ${x:-could not inspect}"; continue; }
    a=$(age_h $SRC/$s)
    [ $DRY = 1 ] && { gone $SRC/$s $a $SRC/$s; continue; }
    mkdir -p $TRASH; mv -T $SRC/$s $TRASH/$s-$now && echo "$s $a" >> $T/moved || say "kept $SRC/$s: rename failed"
  done
  if [ -s $T/moved ]; then
    cut -d' ' -f1 $T/moved > $T/pats; held $T/pats > $T/held2
    while read s a; do t=$TRASH/$s-$now; r=$(named $s $T/held2)
      if [ -n "$r" ] || grep -q '^FAILED' $T/held2; then
        mv -T $t $SRC/$s && say "kept $SRC/$s: named after rename: ${r:-scan failed}" || say "STUCK $t: named after rename (${r:-scan failed}) and could not be put back"
        continue
      fi
      gone $t $a $SRC/$s
    done < $T/moved
  fi
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
    r=$(named "$d" $T/held); [ -n "$r" ] && { say "kept $d: $r"; continue; }
    gone "$d" $(age_h "$d") "$d"
  done
fi
exit 0
