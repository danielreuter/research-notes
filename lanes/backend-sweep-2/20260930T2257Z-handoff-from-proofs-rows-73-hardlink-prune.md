---
id: 20260930T2257Z-handoff-from-proofs-rows-73-hardlink-prune
campaign: verity
lane: backend-sweep-2
kind: handoff
status: backlog
repo: danielreuter/verity
origin: proofs-rows (bc-25950a06), for @proofs (bc-8416bc72) and the old research coordinator (bc-8ece7cde)
---

# Backlog for PR #601: hardlink + prune + sampled unit fields in `73-sweep-shape.sh` (deployed 3:54 PM PDT, restored 3:56 PM PDT)

**Status: not live.** I swapped this into node 1's `/workspace/research/trees/backend-sweep-2` at 3:54 PM PDT. I restored the
original at 3:56 PM PDT, after reading `note:20260930T2252Z-handoff-from-proofs-stand-down` (the sweep stopped at 3:51 PM PDT).
- The live file is again sha256 `bd7c7e63…`, with its own mtime; that is the branch head `57e4c5ef7`.
- No job started in those three minutes.
- Commit this when the sweep restarts, not now.

**Base and result.** The diff below is against `57e4c5ef7`'s file. `patch -p1` from the repo root applies it cleanly. The result
has sha256 `56a6066ed6e2bcfaa0e6b5dc67c92cf61eec1315e10dd516c22a42fb430c1a88`. It is shell only: no `.py` file changes, so
`class_statement`'s stage-cache key doesn't move. (The tree's 1,942 `.py` files hash to `f5f9b1df…` before and after.)

**What it adds:**
- **`stage_link OUT`**, after each `70-class-sweep.sh`. A staged `out/**/classes/<shape>/circuit.txt` becomes a hardlink to the
  same-named file of a `FLOCK_STAGE_CACHE` entry of that shape, and so does each matching `.bin`. It links only when the sizes and
  sha256 match, and replaces the file by an atomic rename. Each link goes to `out/stage-dedupe.tsv` with its sha256.
- **`stage_prune`**, once at the end of every mode but `cut`. It prunes an entry only when both hold:
  - its `circuit.txt` has link count 1;
  - a run that ended with rc 0 (in `status.json`) holds a `results.jsonl` record with the same `{shape, stage}` and
    `live.accepted: true`.

  It never prunes by age. `stage_prune dry` only lists.
- **`MODE=sampled`'s SUMMARY** gains `sampled_units`, `units_proved`, `units_not_proved`, `units_excluded` (definition, spec,
  request, step, op_path and why) and `fully_provable`. The Definitions' shapes come from `$SWEEP/sampled/$ROW/counts.json`, which
  `class_statement --counts-only` writes in the stage job. A prove job whose stage predates this writes it itself.

**Tested on node 1 without GPU work:**
- **Link, by hand** as uid 1000 on `r20260930-221003-ae9c` (sc292's stage, finished) `out/1`: 3 files linked, 79,888,933
  bytes (0.08 GB) freed, in 0.37 s. The sha256 of all three is unchanged. They now share entry `41325b32…`'s inodes (link
  count 3).
- **Link, no-op check:** 0 files on `r20260930-221246-32de`, which was already linked.
- **Prune, dry run:** 31 of the cache's 1,054 entries (3.06 GB) would go, each proved by an rc 0 `MODE=shape` run. The (b)
  chunks' `cdef5bd8…` isn't one of them (4 links). 98 entries had link count 1.
- **Synthetic test:** 16 of 16 checks pass on both the live base and this result. It covers a wrong-bytes decoy entry, `.tmp`
  dirs, rc 1 and still-running runs, rejected records and idempotence.
- **SUMMARY:** on the b8 top-p draw, 460 units, 458 proved, one `GumbelTopPTokenSelectSharedGreedy_v1` excluded, and
  `fully_provable: false`.

**Findings for this lane:**
- **`PRUNE=1` (`57e4c5ef7`) frees nothing as written.** `class_statement.py` (the unlinks after `prove`, lines 857–861) deletes
  each proved class's `circuit.txt` and `.bin` from the prove run's `out/` before 73's `PRUNE` block runs. And `PRUNE` looks only
  at that run's own `$R/out`.
  - So a sampled deployment's `sampled-stage` row (35–60 GB in `runs/<run>/out/classes`) stays after its prove, hardlinked with
    its cache entries at link count 2. That also keeps `stage_prune` off those entries.
  - `sampled()` counts a deployment as off disk once its prove ends, so disk grows by one row per deployment.
  - The 2244Z ask ("delete the stage row's `out/classes` once the sampled prove commits") closes that gap. It was dropped at 3:45
    PM PDT on the premise that `PRUNE=1` covers it. I haven't added it.
- **sc292 and sc302** (`r20260930-221003-ae9c`, `r20260930-221004-184f`): `done.jsonl` says `succeeded` (22:20:33Z). But each
  staged 1 of its 10 shapes, and its run's status never reached `done`. Their `pc` prove jobs would stage the other 9 on the GPU.
- **Re-proving a pruned statement restages it:** a CPU stage job, or a GPU-side stage (231 s for K=2048) in a prove job that
  misses. A match means the same shape and stage record (circuit and class sha512, n, ...). It doesn't compare the seed.
- **The old RC's `sweep2-dedupe-loop`** overlaps `stage_link`. Both swap in an identical inode by rename, so they can run
  together.

**To stop once it's live:** restore the previous file. The next job reads it at start.

```diff
--- a/backends/flock/pod/73-sweep-shape.sh
+++ b/backends/flock/pod/73-sweep-shape.sh
@@ -14,7 +14,10 @@
 #   MODE=sampled-stage ROW=<deployment slug> EV=<its evidence dir> (no GPU), then MODE=sampled (one GPU)
 #              the deployment's sampled units (sampled_units.py: its Commit's draw, reproduced and checked against the record), as their
 #              Call Definitions at their counts, into $SWEEP/sampled/$ROW/; staged, then proved with COVER=1: every unit, not one statement
-#   SUMMARY=<path> in any mode but cut: the job's statements, prove time and selftests as one JSON record
+#   SUMMARY=<path> in any mode but cut: the job's statements, prove time and selftests as one JSON record; MODE=sampled's also lists
+#              the draw's units: sampled_units, units_proved, units_not_proved, units_excluded (each unit the sweep leaves out, by
+#              Definition name and why) and fully_provable (false unless every unit was proved), from the Definitions' shapes
+#              ($SWEEP/sampled/$ROW/counts.json, written by MODE=sampled-stage)
 #   PRUNE=1 in a proving mode: once it succeeded, its staged circuits are deleted from the run and from FLOCK_STAGE_CACHE
 # env: SWEEP=/workspace/jobs/sweep2  SELECT=units  FLOCK_WORK=/workspace/jobs/flock-sweep2  SM=120  and 70-class-sweep.sh's (SELFTEST=0 here)
 for kv in "$@"; do case $kv in *=*) export "$kv" ;; esac; done
@@ -33,6 +36,84 @@
 done
 { nvidia-smi --query-gpu=index,name,driver_version,memory.total --format=csv; nproc; } | tee $R/out/host.txt
 export PYTHONPATH=$REPO/packages/verity/src:$REPO/backends/numerical/python:$REPO/backends/flock/python:$REPO/integrations/vllm:$REPO/tools/circuit_check/src:$REPO/protocols/sampled_proofs:$REPO/protocols/one_stage:$REPO/protocols/pouw
+# A staged class once on disk (node 1's /workspace, 30 Sep): a fresh stage copies out/ into FLOCK_STAGE_CACHE, so after
+# 70-class-sweep.sh each out/**/classes/<shape>/circuit.txt and .bin whose sha256 equals the same file of a cache entry of its shape
+# becomes a hardlink to it. At the job's end an entry is pruned when its circuit.txt has no other link and a run that ended with
+# rc 0 proved its statement (a results.jsonl record of the same shape and stage, accepted); `stage_prune dry` only lists. Both
+# append to out/stage-dedupe.tsv. Shell only: an edit to a .py file would change class_statement's stage-cache key.
+stage_link() (
+  set +x; c=${FLOCK_STAGE_CACHE:-}; [ -d "$c" ] || exit 0
+  n=0; freed=0
+  link() {
+    local l b; l=$(stat -c %h "$1"); b=$(stat -c %s "$1")
+    ln -f "$2" "$1.lnk$BASHPID" && mv -f "$1.lnk$BASHPID" "$1" || { rm -f "$1.lnk$BASHPID"; return; }
+    n=$((n + 1)); [ "$l" = 1 ] && freed=$((freed + b))
+    printf 'linked\t%s\t%s\t%s\t%s\n' "$3" "$b" "$1" "$2" >> "$R/out/stage-dedupe.tsv"
+  }
+  for d in "$1"/classes/*/; do
+    f=${d}circuit.txt; [ -f "$f" ] || continue
+    for rj in $(grep -l -F "\"shape\": \"$(basename "$d")" "$c"/$(printf '?%.0s' {1..32})/rec.json 2>/dev/null); do
+      e=$(dirname "$rj")
+      if ! [ "$f" -ef "$e/circuit.txt" ]; then
+        [ -f "$e/circuit.txt" ] && [ "$(stat -c %s "$f")" = "$(stat -c %s "$e/circuit.txt")" ] || continue
+        s=$(sha256sum < "$f" | cut -c1-64); [ "$s" = "$(sha256sum < "$e/circuit.txt" | cut -c1-64)" ] || continue
+        link "$f" "$e/circuit.txt" "$s"
+      fi
+      for g in "$d"*.bin; do
+        h=$e/${g##*/}; [ -f "$g" ] && [ -f "$h" ] && ! [ "$g" -ef "$h" ] || continue
+        s=$(sha256sum < "$g" | cut -c1-64); [ "$s" = "$(sha256sum < "$h" | cut -c1-64)" ] && link "$g" "$h" "$s"
+      done
+      break
+    done
+  done
+  echo "stage_link $1: $n files linked, $freed bytes freed"
+)
+stage_prune() (
+  set +x; c=${FLOCK_STAGE_CACHE:-}; [ -d "$c" ] || exit 0
+  n=0; freed=0; p=$(mktemp)
+  $(command -v python3) - "$c" "$(dirname "$R")" > "$p" <<'EOF' || { rm -f "$p"; exit 0; }
+import json, sys
+from pathlib import Path
+cache, runs = Path(sys.argv[1]), Path(sys.argv[2])
+key = lambda r: json.dumps({"shape": r.get("shape"), "stage": r.get("stage")}, sort_keys=True)
+proved = set()
+for st in runs.glob("*/status.json"):
+    try:
+        t = json.loads(st.read_text())["transitions"][-1]
+    except (OSError, ValueError, KeyError, IndexError):
+        continue
+    if t.get("state") != "done" or t.get("rc") != 0:
+        continue
+    for f in [*st.parent.glob("out/classes/results.jsonl"), *st.parent.glob("out/*/classes/results.jsonl")]:
+        for ln in f.read_text(errors="replace").splitlines():
+            try:
+                r = json.loads(ln)
+            except ValueError:
+                continue
+            if isinstance(r, dict) and (r.get("live") or {}).get("accepted") is True and r.get("stage"):
+                proved.add(key(r))
+for e in sorted(cache.iterdir()):
+    circ, rec = e / "circuit.txt", e / "rec.json"
+    try:
+        if len(e.name) != 32 or not circ.is_file() or not rec.is_file() or circ.stat().st_nlink != 1:
+            continue
+        r = json.loads(rec.read_text())
+        if key(r) in proved:
+            print(f"{e}\t{sum(f.stat().st_size for f in e.iterdir() if f.is_file() and f.stat().st_nlink == 1)}\t"
+                  f"{(r.get('stage') or {}).get('circuit_sha512')}")
+    except (OSError, ValueError):
+        continue
+EOF
+  while IFS=$'\t' read -r e b h; do
+    if [ "${1:-}" = dry ]; then echo "stage_prune: would prune $e ($b bytes, circuit_sha512 $h)"
+    else
+      mv "$e" "$e.prune$BASHPID" 2>/dev/null && rm -rf "$e.prune$BASHPID" || continue
+      printf 'pruned\t%s\t%s\t%s\n' "$h" "$b" "$e" >> "$R/out/stage-dedupe.tsv"
+    fi
+    n=$((n + 1)); freed=$((freed + b))
+  done < "$p"
+  rm -f "$p"; echo "stage_prune${1:+ $1}: $n entries, $freed bytes"
+)
 case ${MODE:?cut or shape} in
 cut)
   W=$FLOCK_WORK/flock-circuit; mkdir -p $W; UV=$(command -v uv || echo /workspace/jobs/bin/uv)
@@ -78,6 +159,7 @@
   st=${SELFTEST:-0}; case ",${SELFTEST_SHAPES:-}," in *",$SHAPE,"*) st=1 ;; esac
   OUT=$O bash backends/flock/pod/70-class-sweep.sh DEFS=$O/defs.json SHAPES=$O/shapes.txt SELECT=${SELECT:-units} \
     SELFTEST=$st SELFTEST_LARGEST=0 STAGE_ONLY=$([ $MODE = stage ] && echo 1 || echo 0) || rc=1
+  stage_link $O
   done ;;
 sampled-stage|sampled)
   A=$SWEEP/sampled/$ROW; mkdir -p $A; rc=0
@@ -92,13 +174,20 @@
     cp $R/out/draw/defs.json $R/out/draw/picks.json $A/
   fi
   OUT=$R/out bash backends/flock/pod/70-class-sweep.sh DEFS=$A/defs.json SELECT=${SELECT:-units} COVER=1 SELFTEST=${SELFTEST:-0} \
-    SELFTEST_LARGEST=0 STAGE_ONLY=$([ $MODE = sampled-stage ] && echo 1 || echo 0) || rc=1 ;;
+    SELFTEST_LARGEST=0 STAGE_ONLY=$([ $MODE = sampled-stage ] && echo 1 || echo 0) || rc=1
+  stage_link $R/out
+  if [ $MODE = sampled-stage ] || [ ! -s $A/counts.json ]; then
+    ${PYBIN:-$FLOCK_WORK/flock-circuit/py/bin/python3} -m verity_flock.class_statement --definitions $A/defs.json --partition q-word \
+      --out $R/out/counts --select ${SELECT:-units} --counts-only && cp $R/out/counts/counts.json $A/counts.json || rc=1
+  fi ;;
 esac
+[ $MODE = cut ] || stage_prune
 # SUMMARY=<path>: the job's proofs in one record (a feeder reads it): statements proved and accepted, their prove time, the selftests
 if [ -n "${SUMMARY:-}" ]; then
   mkdir -p $(dirname $SUMMARY)
-  $(command -v python3) - $R/out "$SUMMARY" $MODE $SECONDS $rc <<'EOF' || rc=1
+  $(command -v python3) - $R/out "$SUMMARY" $MODE $SECONDS $rc ${A:-} <<'EOF' || rc=1
 import json, os, sys
+from collections import Counter
 from pathlib import Path
 out, dest, mode, job_s, rc = Path(sys.argv[1]), sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
 recs = [json.loads(ln) for f in sorted(out.rglob("results.jsonl")) for ln in f.read_text().splitlines() if ln.strip()]
@@ -115,6 +204,30 @@
      "prove_total_s": round(sum(x.get("prove_total_s_sum") or 0 for x in live), 3), "e2e_s": round(sum(x.get("e2e_s_sum") or 0 for x in live), 3),
      "selftests": len(st), "selftests_pass": sum(1 for x in st if x.get("all_pass") is True),
      "gpu_cases": len(gpu), "gpu_cases_pass": sum(1 for c in gpu if c.get("pass") is True), "gpu_case_names": sorted({c.get("case") for c in gpu})}
+# MODE=sampled: the draw's units (its picks, one Call each), those proved, and those the sweep leaves out (the token-select Calls,
+# which --select drops), each by name and why; fully_provable only when every unit was proved
+A = Path(sys.argv[6]) if len(sys.argv) > 6 and sys.argv[6] else None
+if mode == "sampled" and A and (A / "picks.json").exists():
+    picks = json.loads((A / "picks.json").read_text())["picks"]
+    counts = json.loads((A / "counts.json").read_text()) if (A / "counts.json").exists() else None
+    per = counts["per_definition"] if counts else {}
+    ok = {r["shape"] for r in recs if (r.get("live") or {}).get("accepted") is True}
+    excluded, proved, not_proved = [], 0, Counter()
+    for p in picks:
+        name = p["spec"].split("{")[0]
+        if counts is None:
+            continue
+        if p["spec"] not in per:
+            why = ("not provable in practice (the top-p sampler Call is one unit over the whole vocabulary row)"
+                   if name.startswith("GumbelTopPTokenSelect") else "left out by the sweep (--select drops the token-select Calls), not attempted")
+            excluded.append({"definition": name, "spec": p["spec"], "request_id": p.get("request_id"), "step": p.get("step"),
+                             "op_path": p.get("op_path"), "why": f"{name}: {why}"})
+        elif all(sh in ok for sh in per[p["spec"]]):
+            proved += 1
+        else:
+            not_proved[name] += 1
+    s |= {"sampled_units": len(picks), "units_proved": proved if counts else None, "units_not_proved": dict(not_proved),
+          "units_excluded": excluded, "fully_provable": counts is not None and proved == len(picks)}
 Path(dest).write_text(json.dumps(s, indent=1))
 print(json.dumps(s)[:800])
 EOF
```
