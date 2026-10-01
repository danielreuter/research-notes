#!/usr/bin/env bash
# Does origin/main stage the circuit (stage.circuit_sha512) of the lanes' points at the overnight K? red-team-proofs-554's
# optional full-K confirmation (note:proofs/20261001T0805Z-reply-from-red-team-proofs-554-nontile-statements), placed by
# proofs-n2-hill for proofs (08:18Z). Run from the root of an origin/main tree:
#   CONFIRM_DIR=DIR bash main_confirm.sh
# DIR holds plan.json (the entries, in order: label, the class_statement source arguments, the expected digest and the node-1
# runs it comes from), gemm_fp.py and cpu-slices.sh (both from the flock-fp tree at cde1c7ac1, sha256 in plan.json), and this
# script. Each entry is one class_statement invocation with --binary /bin/false: the prover step fails, and the record keeps
# its stage. The staged files go to scratch and are removed after each entry; RESEARCH_RUN_DIR/out keeps each entry's
# records and summary.json. On a node with prover slices (SLICE_LOCKS), it takes one free 16-core slice first, as
# 74-gemm-hill.sh does, and pins every step to it. Exit 0 if every entry staged and matched, 1 otherwise.
set -uo pipefail
D=${CONFIRM_DIR:?CONFIRM_DIR}
RUN=${RESEARCH_RUN_DIR:-$PWD/confirm-local}
OUT=$RUN/out
SCR=${CONFIRM_SCRATCH:-${TMPDIR:-/tmp}}/main-confirm-$(basename "$RUN")
PY=${PYBIN:-python3}
mkdir -p "$OUT" "$SCR"
export PYTHONPATH=$PWD/packages/verity/src:$PWD/backends/numerical/python:$PWD/backends/flock/python:$PWD/integrations/vllm:$PWD/tools/circuit_check/src:$PWD/protocols/sampled_proofs:$PWD/protocols/one_stage:$PWD/protocols/pouw
PIN=()
if [ -z "${NO_SLICE:-}" ]; then
  . "$D/cpu-slices.sh"
  hold_slices "" 16
  PIN=(taskset -c "$SLICE_CPUS")
  export RAYON_NUM_THREADS=16 OMP_NUM_THREADS=16
fi
{ echo "host $(hostname)"; echo "tree $PWD"; cat .research-source.json 2>/dev/null; echo "slices ${SLICES:-none} cpus ${SLICE_CPUS:-all} wait_s ${SLICE_WAIT_S:-0}"
  echo "python $("$PY" -c 'import sys, numpy; print(sys.version.split()[0], "numpy", numpy.__version__)')"; } > "$OUT/host.txt" 2>&1
n=$("$PY" -c 'import json, sys; print(len(json.load(open(sys.argv[1]))["entries"]))' "$D/plan.json")
for i in $(seq 0 $((n - 1))); do
  label=$("$PY" -c 'import json, sys; print(json.load(open(sys.argv[1]))["entries"][int(sys.argv[2])]["label"])' "$D/plan.json" "$i")
  mapfile -t src < <("$PY" -c 'import json, sys; e = json.load(open(sys.argv[1]))["entries"][int(sys.argv[2])]; print("\n".join(e["src"]))' "$D/plan.json" "$i")
  e=$OUT/$label; s=$SCR/$label
  mkdir -p "$e" && rm -rf "$s"
  "$PY" -c 'import json, sys; e = json.load(open(sys.argv[1]))["entries"][int(sys.argv[2])]; "defs" in e and json.dump(e["defs"], open(sys.argv[3], "w"))' \
    "$D/plan.json" "$i" "$e/defs.json"
  for k in "${!src[@]}"; do src[$k]=${src[$k]//@D@/$D}; src[$k]=${src[$k]//@E@/$e}; done
  t0=$(date +%s.%N)
  TV=(); [ -x /usr/bin/time ] && TV=(/usr/bin/time -v)
  "${TV[@]}" "${PIN[@]}" "$PY" -m verity_flock.class_statement "${src[@]}" --partition q-word --out "$s" --binary /bin/false \
    --batch fixed --n 16 --jobs 1 --warm 0 --runs 1 --selftest 0 > "$e/stdout.log" 2> "$e/stderr.log"
  rc=$?
  for f in results.jsonl class-sweep.jsonl counts.json; do [ -f "$s/$f" ] && cp "$s/$f" "$e/"; done
  "$PY" -c 'import json, sys; json.dump({"label": sys.argv[1], "rc": int(sys.argv[2]), "wall_s": round(float(sys.argv[3]), 1)}, open(sys.argv[4], "w"))' \
    "$label" "$rc" "$(python3 -c "import time, sys; print(time.time() - float(sys.argv[1]))" "$t0")" "$e/entry.json"
  du -sb "$s" 2>/dev/null | cut -f1 > "$e/scratch_bytes.txt"
  rm -rf "$s"
  echo "$label rc $rc"
done
"$PY" - "$D/plan.json" "$OUT" <<'PY'
import json, sys
from pathlib import Path
plan, out = json.load(open(sys.argv[1])), Path(sys.argv[2])
rows, ok = [], True
for e in plan["entries"]:
    d = out / e["label"]
    got, defn = None, None
    for f in ("results.jsonl", "class-sweep.jsonl"):
        p = d / f
        if not p.exists():
            continue
        for ln in p.read_text().splitlines():
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            c = (r.get("stage") or {}).get("circuit_sha512")
            if c:
                got, defn = c, r.get("definition") or r.get("class")
                break
        if got:
            break
    ent = json.loads((d / "entry.json").read_text()) if (d / "entry.json").exists() else {}
    rss = None
    for ln in (d / "stderr.log").read_text(errors="replace").splitlines() if (d / "stderr.log").exists() else []:
        if "Maximum resident set size" in ln:
            rss = round(int(ln.rsplit(":", 1)[1]) / 2**20, 2)
    verdict = "missing" if not got else ("equal" if got.startswith(e["expected"]) else "differs")
    ok &= verdict == "equal" and (e.get("definition") in (None, defn))
    rows.append({"label": e["label"], "definition": defn, "expected_definition": e.get("definition"), "verdict": verdict,
                 "circuit_sha512": got, "expected": e["expected"], "expected_runs": e.get("expected_runs"), "rc": ent.get("rc"),
                 "wall_s": ent.get("wall_s"), "maxrss_gb": rss})
    print(f'{e["label"]:22s} {verdict:8s} {(got or "-")[:16]} expected {e["expected"][:16]} {defn}')
json.dump({"schema": "proofs-n2-hill/main-confirm/v0", "tree": plan.get("tree"), "question": plan.get("question"), "rows": rows,
           "all_equal": ok}, open(out / "summary.json", "w"), indent=1)
sys.exit(0 if ok else 1)
PY
