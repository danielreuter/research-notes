#!/usr/bin/env bash
# proofs-rows' copy of backends/flock/pod/73-sweep-shape.sh (backend-sweep-2's, at 70e99f57), with the (b) stage/prove split:
#   MODE=shape STAGE_ONLY=1 ...   (no GPU) the chunk's statement exactly as its GPU job would stage it (the same settings, so the
#              same FLOCK_STAGE_CACHE key), into the cache, and a marker $FLOCK_STAGE_CACHE/staged/<ident>.json with the files' sha256
#   MODE=shape REQUIRE_STAGED=1 ...   (one GPU) the chunk, only if that marker and its cache entry exist (else rc 3 before the
#              prover starts); after it, rc 3 if the job staged the shape itself (a GPU-side stage) or proved other bytes
#   stage_mark.py (beside this script) computes ident and checks; SUMMARY gains stage_only, staged, stage_cached, stage_s, stage_checks
#   and script_sha256
# and MODE=sampled's SUMMARY reports the draw's units beside the totals: sampled_units, units_proved, units_not_proved, units_excluded
#   (each unit the sweep leaves out, by Definition name and why: GumbelTopPTokenSelect*'s "not provable in practice") and
#   fully_provable (false unless every unit was proved); MODE=sampled-stage writes the Definitions' shapes it needs ($A/counts.json).
# Run from the tree (cwd), as bash /path/to/this/73-sweep-shape.sh; everything else is unchanged.
# The backend sweep as one Kueue job per unit shape (vy-nebius-1's dispatcher), over a served row's Build.
#   MODE=cut   ROW=<row slug> BUILD=<the row's Build dir, with build_request/instances.json.gz>
#              the row's program graph (verity_vllm program-graph) and class_statement --counts-only under SELECT, into
#              $SWEEP/$ROW/ (program.json, counts.json, shapes.tsv: shape, word gates, row units, its Definitions) and the run's out/
#   MODE=stage ROW=<row slug> SHAPE=<shape digest>   (no GPU)
#              builds the prover and stages that one shape into FLOCK_STAGE_CACHE, from the Definitions of $SWEEP/$ROW/counts.json
#              that hold it, at their row Call counts
#   MODE=shape ROW=<row slug> SHAPE=<shape digest>   (one GPU)
#              proves it (70-class-sweep.sh) with the same settings, so a staged shape comes from the cache; SELFTEST=1
#              SELFTEST_GPU=1 for its selftest on the GPU (the device's proofs and transcripts against the CPU's, byte for byte)
#   SHAPES=<digest>,<digest>,... in place of SHAPE: those shapes one after another in one job, each into out/<k>/ (k from 1);
#              SELFTEST_SHAPES=<digest>,<digest> selftests only those. The job fails if any shape did
#   MODE=sampled-stage ROW=<deployment slug> EV=<its evidence dir> (no GPU), then MODE=sampled (one GPU)
#              the deployment's sampled units (sampled_units.py: its Commit's draw, reproduced and checked against the record), as their
#              Call Definitions at their counts, into $SWEEP/sampled/$ROW/; staged, then proved with COVER=1: every unit, not one statement
#   SUMMARY=<path> in any mode but cut: the job's statements, prove time and selftests as one JSON record
# env: SWEEP=/workspace/jobs/sweep2  SELECT=units  FLOCK_WORK=/workspace/jobs/flock-sweep2  SM=120  and 70-class-sweep.sh's (SELFTEST=0 here)
for kv in "$@"; do case $kv in *=*) export "$kv" ;; esac; done
set -uxo pipefail
REPO=$(pwd); R=${RESEARCH_RUN_DIR:-/tmp/sweep-shape}; mkdir -p $R/out
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd); sha256sum $HERE/73-sweep-shape.sh $HERE/stage_mark.py | tee $R/out/script.sha256
SWEEP=${SWEEP:-/workspace/jobs/sweep2}; D=$SWEEP/$ROW; mkdir -p $D
export FLOCK_WORK=${FLOCK_WORK:-/workspace/jobs/flock-sweep2}; mkdir -p $FLOCK_WORK/home; export HOME=$FLOCK_WORK/home
export FLOCK_STAGE_CACHE=${FLOCK_STAGE_CACHE:-$FLOCK_WORK/stage-cache} SM=${SM:-120}
# the prover as flock-m0-v3 measures it (#554, attempt #15): 4x4 GEMM tiles and m = 35 statements, witnesses built 4 ahead
export FLOCK_GEMM_TILE=${FLOCK_GEMM_TILE:-4x4} BATCH_ANDS=${BATCH_ANDS:-34359738368} MAX_STATEMENT_BITS=${MAX_STATEMENT_BITS:-34359738368} \
  FC_PIPELINE_DEPTH=${FC_PIPELINE_DEPTH:-4} FC_HOST_PREPIN=${FC_HOST_PREPIN:-1}
unset CARGO_TARGET_DIR
[ -n "${RAYON_NUM_THREADS:-}" ] || export RAYON_NUM_THREADS=${OMP_NUM_THREADS:-$(nproc)}
for c in $FLOCK_WORK/cuda-root /workspace/cache/flock/cuda-root; do
  [ ! -x /usr/local/cuda-13.3/bin/nvcc ] && [ -z "${CUDA_TK:-}" ] && [ -x $c/usr/local/cuda-13.3/bin/nvcc ] && export CUDA_TK=$c/usr/local/cuda-13.3
done
{ nvidia-smi --query-gpu=index,name,driver_version,memory.total --format=csv; nproc; } | tee $R/out/host.txt
export PYTHONPATH=$REPO/packages/verity/src:$REPO/backends/numerical/python:$REPO/backends/flock/python:$REPO/integrations/vllm:$REPO/tools/circuit_check/src:$REPO/protocols/sampled_proofs:$REPO/protocols/one_stage:$REPO/protocols/pouw
case ${MODE:?cut or shape} in
cut)
  W=$FLOCK_WORK/flock-circuit; mkdir -p $W; UV=$(command -v uv || echo /workspace/jobs/bin/uv)
  [ -x $W/py/bin/python ] || { $UV venv -q --python 3.12 $W/py && $UV pip install -q --python $W/py/bin/python numpy blake3; } || exit 1
  PY=$W/py/bin/python3
  $PY -m verity_vllm.pipeline.cli program-graph $R/out/program.json $BUILD/build_request/instances.json.gz \
    --row "{\"row\": \"$ROW\"}" || exit 1
  echo "graph_s=$SECONDS" | tee $R/out/cut-timing.txt
  $PY -m verity_flock.class_statement --program-graph $R/out/program.json --partition q-word --out $R/out/cut \
    --select ${SELECT:-units} --counts-only || exit 1
  echo "cut_s=$SECONDS" | tee -a $R/out/cut-timing.txt
  $PY - $R/out/cut/counts.json $R/out/shapes.tsv <<'EOF' || exit 1
import json, sys
c = json.load(open(sys.argv[1]))
defs = {}
for fid, per in c["per_definition"].items():
    for sh in per:
        defs.setdefault(sh, []).append(fid)
rows = sorted(c["shapes"].items(), key=lambda kv: (kv[1]["word_gates"], kv[0]))
with open(sys.argv[2], "w") as f:
    for sh, s in rows:
        f.write(f"{sh}\t{s['word_gates']}\t{s['row_units']}\t{json.dumps(sorted(defs.get(sh, [])))}\n")
print(f"{len(rows)} shapes, {sum(s['row_units'] or 0 for _, s in rows)} row units")
EOF
  cp $R/out/program.json $R/out/cut/counts.json $R/out/shapes.tsv $D/ || exit 1 ;;
stage|shape)
  rc=0; k=0; SHAPES=${SHAPES:-$SHAPE}
  so=0; { [ $MODE = stage ] || [ "${STAGE_ONLY:-0}" = 1 ]; } && so=1
  MARK=("${PYBIN:-$FLOCK_WORK/flock-circuit/py/bin/python3}" $HERE/stage_mark.py)
  for SHAPE in ${SHAPES//,/ }; do
  k=$((k + 1)); O=$R/out/$k; mkdir -p $O
  $(command -v python3) - $D/counts.json $SHAPE $O/defs.json <<'EOF' || { rc=1; continue; }
import json, sys
c, s = json.load(open(sys.argv[1])), sys.argv[2]
holders = {fid: per for fid, per in c["per_definition"].items() if s in per}
if not holders:
    sys.exit(f"shape {s} is in no Definition of {sys.argv[1]}")
# the smallest Definition holding it (attention's shared shapes are in up to 1,151 of them), its Calls scaled to the shape's row
# units: those cap the batch; the row's own count stays counts.json's, which the rollup reads
fid = min(holders, key=lambda f: (sum(holders[f].values()), f))
row = c["shapes"][s]["row_units"] or holders[fid][s] * c["calls"][fid]
json.dump({fid: max(1, round(row / holders[fid][s]))}, open(sys.argv[3], "w"))
EOF
  echo $SHAPE > $O/shapes.txt
  st=${SELFTEST:-0}; case ",${SELFTEST_SHAPES:-}," in *",$SHAPE,"*) st=1 ;; esac
  req=0; [ $so = 0 ] && [ "${REQUIRE_STAGED:-0}" = 1 ] && req=1
  [ $req = 1 ] && { "${MARK[@]}" pre $O $SHAPE || { rc=3; continue; }; }
  OUT=$O bash backends/flock/pod/70-class-sweep.sh DEFS=$O/defs.json SHAPES=$O/shapes.txt SELECT=${SELECT:-units} \
    SELFTEST=$st SELFTEST_LARGEST=0 STAGE_ONLY=$so || rc=1
  if [ $so = 1 ]; then "${MARK[@]}" write $O $SHAPE || rc=1
  elif [ $req = 1 ]; then "${MARK[@]}" post $O $SHAPE || rc=3; fi
  done ;;
sampled-stage|sampled)
  A=$SWEEP/sampled/$ROW; mkdir -p $A; rc=0
  if [ $MODE = sampled-stage ] || [ ! -s $A/defs.json ]; then
    W=$FLOCK_WORK/flock-circuit; mkdir -p $W; UV=$(command -v uv || echo /workspace/jobs/bin/uv)
    [ -x $W/py/bin/python ] || { $UV venv -q --python 3.12 $W/py && $UV pip install -q --python $W/py/bin/python numpy blake3; } || exit 1
    # the draw is the deployment's own: its executing tree's replay code (tree.json), never this tree's
    T=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["tree"].removesuffix("/integrations/vllm"))' $EV/tree.json) || exit 1
    [ -d $T/integrations/vllm ] || { echo "the deployment's executing tree $T is gone: its draw can't be reproduced"; exit 1; }
    PYTHONPATH=$T/packages/verity/src:$T/integrations/vllm:$T/protocols/sampled_proofs:$T/protocols/one_stage \
      $W/py/bin/python3 backends/flock/pod/sampled_units.py $EV $R/out/draw || exit 1
    cp $R/out/draw/defs.json $R/out/draw/picks.json $A/
  fi
  OUT=$R/out bash backends/flock/pod/70-class-sweep.sh DEFS=$A/defs.json SELECT=${SELECT:-units} COVER=1 SELFTEST=${SELFTEST:-0} \
    SELFTEST_LARGEST=0 STAGE_ONLY=$([ $MODE = sampled-stage ] && echo 1 || echo 0) || rc=1
  # each sampled Definition's shapes (SUMMARY's units_proved: a pick is proved when every shape of its Definition is); the stage job
  # writes them, a prove job whose stage predates this does
  if [ $MODE = sampled-stage ] || [ ! -s $A/counts.json ]; then
    ${PYBIN:-$FLOCK_WORK/flock-circuit/py/bin/python3} -m verity_flock.class_statement --definitions $A/defs.json --partition q-word \
      --out $R/out/counts --select ${SELECT:-units} --counts-only && cp $R/out/counts/counts.json $A/counts.json || rc=1
  fi ;;
esac
# SUMMARY=<path>: the job's proofs in one record (a feeder reads it): statements proved and accepted, their prove time, the selftests
if [ -n "${SUMMARY:-}" ]; then
  mkdir -p $(dirname $SUMMARY)
  $(command -v python3) - $R/out "$SUMMARY" $MODE $SECONDS $rc ${so:-0} ${A:-} <<'EOF' || rc=1
import json, os, sys
from collections import Counter
from pathlib import Path
out, dest, mode, job_s, rc = Path(sys.argv[1]), sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
recs = [json.loads(ln) for f in sorted(out.rglob("results.jsonl")) for ln in f.read_text().splitlines() if ln.strip()]
staged = [json.loads(ln) for f in sorted(out.rglob("staged.jsonl")) for ln in f.read_text().splitlines() if ln.strip()]
split = {"stage_only": sys.argv[6] == "1", "staged": sum(1 for r in staged if "stage" in r),
         "stage_cached": sum(1 for r in recs if r.get("stage_cached")), "stage_s": round(sum(r.get("stage_s") or 0 for r in recs + staged), 3),
         "stage_checks": [json.loads(f.read_text()) for f in sorted(out.glob("*/stage-check.json"))],
         "statement_digests": sorted({r["live"]["statement_digest"] for r in recs if (r.get("live") or {}).get("statement_digest")}),
         "script_sha256": (out / "script.sha256").read_text().split() if (out / "script.sha256").exists() else None}
live = [r["live"] for r in recs if r.get("live")]
st = [r["selftest"] for r in recs if r.get("selftest")]
gpu = [c for x in st for c in x.get("gpu_cases", [])]
s = {"run": os.path.basename(os.environ.get("RESEARCH_RUN_DIR", "")), "mode": mode, "rc": rc, "job_s": job_s,
     "binary_sha256": sorted({ln.split()[0] for f in out.rglob("binary.sha256") for ln in f.read_text().splitlines()[:1]}),
     "shapes": len(recs), "proved": sum(1 for x in live if x.get("accepted") is True),
     "not_proved": [{"shape": r["shape"][:16], "why": r.get("broke") or r.get("skipped") or (r.get("live") or {}).get("why")}
                    for r in recs if (r.get("live") or {}).get("accepted") is not True],
     "statements": sum(x.get("timed_runs") or 0 for x in live), "accepted_statements": sum(x.get("accepted_runs") or 0 for x in live),
     "units": sum((r.get("cover") or {}).get("statements", 0) * (r.get("cover") or {}).get("units_per_statement", 0) for r in recs),
     "prove_total_s": round(sum(x.get("prove_total_s_sum") or 0 for x in live), 3), "e2e_s": round(sum(x.get("e2e_s_sum") or 0 for x in live), 3),
     "selftests": len(st), "selftests_pass": sum(1 for x in st if x.get("all_pass") is True),
     "gpu_cases": len(gpu), "gpu_cases_pass": sum(1 for c in gpu if c.get("pass") is True), "gpu_case_names": sorted({c.get("case") for c in gpu})} | split
# MODE=sampled: the draw's units (its picks, one Call each), those proved, and those the sweep leaves out (the token-select Calls,
# which --select drops), each by name and why; fully_provable only when every unit was proved
A = Path(sys.argv[7]) if len(sys.argv) > 7 and sys.argv[7] else None
if mode == "sampled" and A and (A / "picks.json").exists():
    picks = json.loads((A / "picks.json").read_text())["picks"]
    counts = json.loads((A / "counts.json").read_text()) if (A / "counts.json").exists() else None
    per = counts["per_definition"] if counts else {}
    ok = {r["shape"] for r in recs if (r.get("live") or {}).get("accepted") is True}
    excluded, proved, not_proved = [], 0, Counter()
    for p in picks:
        name = p["spec"].split("{")[0]
        if counts is None:
            continue
        if p["spec"] not in per:
            why = ("not provable in practice (the top-p sampler Call is one unit over the whole vocabulary row)"
                   if name.startswith("GumbelTopPTokenSelect") else "left out by the sweep (--select drops the token-select Calls), not attempted")
            excluded.append({"definition": name, "spec": p["spec"], "request_id": p.get("request_id"), "step": p.get("step"),
                             "op_path": p.get("op_path"), "why": f"{name}: {why}"})
        elif all(sh in ok for sh in per[p["spec"]]):
            proved += 1
        else:
            not_proved[name] += 1
    s |= {"sampled_units": len(picks), "units_proved": proved if counts else None, "units_not_proved": dict(not_proved),
          "units_excluded": excluded, "fully_provable": counts is not None and proved == len(picks)}
Path(dest).write_text(json.dumps(s, indent=1))
print(json.dumps(s)[:800])
EOF
fi
exit ${rc:-0}
