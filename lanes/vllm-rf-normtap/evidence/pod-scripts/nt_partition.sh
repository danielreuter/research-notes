#!/usr/bin/env bash
# nt_partition.sh: the no-recompute partition checker (Q_word_v1{X=16,W=32,R=no-recompute}: query/word.py + verity.ir.partition.validate_unit_cut)
# on the norm Definitions and on #101 under the norm-scale policy, in a LOCAL TRIAL MERGE of cursor/no-recompute-partition-289b (fd9f81e8)
# and cursor/vllm-rf-normtap-57d5 (14ea93c6): the shipped commit, never pushed.  Then the merged tree's word, partition and norm-scale tests
# and the lints, in a git clone of the shipped commit (the gate (b) clone procedure).  Evidence under $RESEARCH_RUN_DIR/evidence.
#   research run --on <pod> --project verity --source <trial-merge worktree> --cwd source --custody-r2 --send nt_partition.sh \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/nt_partition.sh"'
set -u
S=$PWD; OUT=$RESEARCH_RUN_DIR; EV=$OUT/evidence; mkdir -p "$EV"; ROOT=/workspace/research; T=/workspace/gc2/nrmerge
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
rm -rf $T
git clone -q --no-checkout $ROOT/git/verity.git $T && git -C $T checkout -q --detach "$RESEARCH_SOURCE_SHA" || { echo "CLONE-FAIL $RESEARCH_SOURCE_SHA"; exit 3; }
d=$(diff -rq -x .git -x __pycache__ -x READY.json $S $T | wc -l); echo "tree $T @ $(git -C $T rev-parse HEAD) vs shipped: $d differing entries"
[ "$d" = 0 ] || exit 4
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd $T/integrations/vllm
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
PROG=/workspace/nt/sweep/$ROW/build_request

# (1) every norm Definition specialization #101 uses, the exactness widths, and Gemma's RsqrtF32_v1{N=1}: the cut and the unit rule
python - "$EV/partition_norms.json" "$PROG" <<'PY'
import json, sys, time
from verity_vllm.query import word as W
from verity_vllm.query.program_view import from_instances

out_p, prog = sys.argv[1], sys.argv[2]
P = from_instances(f"{prog}/instances.json.gz")
specs = {}
for c in P.calls:
    if c.family.startswith(("RMSNorm", "RsqrtF32")):
        k = (c.family, json.dumps(dict(c.statics), sort_keys=True, default=str))
        specs[k] = specs.get(k, 0) + 1
for N in (64, 128, 256, 576, 1536, 2048, 2304, 2560, 4096):
    for fam in ("RMSNormTriton_v1", "RMSNormFusedCuda_v2"):
        specs.setdefault((fam, json.dumps({"EPS": 1e-05, "N": N}, sort_keys=True)), 0)
specs.setdefault(("RsqrtF32_v1", json.dumps({"N": 1})), 0)
rows = []
for (fam, st), calls in sorted(specs.items(), key=lambda kv: (kv[0][0], json.loads(kv[0][1]).get("N", 0))):
    t0 = time.time()
    try:
        f = W.specialization(fam, json.loads(st))
        G = W.Graph(f)
        R = W.units(G, 16, 32)
        r = W.unit_rule(f)
        cut = R["cut"]
        rows.append({"family": fam, "statics": json.loads(st), "calls_in_101": calls, "gates": int(G.total), "structure_gates": int(G.free),
                     "units": int(r["units_per_call"]), "by_kind": r["by_kind"], "committed_interior_words": int(r["committed_interior_words"]),
                     "committed_interior": r["committed_interior"], "max_out_bits": int(r["max_out_bits"]), "width_ok": bool(R["ok"].all()),
                     "strict_partition": "gate-not-certified-once" not in cut.codes and "gate-count" not in cut.codes,
                     "committed_boundaries_only": "read-uncommitted" not in cut.codes and "output-uncommitted" not in cut.codes,
                     "recomputed_gates": len(G.recomputed), "cut_ok": bool(cut.ok), "cut_codes": list(cut.codes), "cut_detail": cut.detail,
                     "violations": r["violations"], "seconds": round(time.time() - t0, 2)})
    except Exception as e:
        rows.append({"family": fam, "statics": json.loads(st), "calls_in_101": calls, "error": f"{type(e).__name__}: {e}"[:400]})
    x = rows[-1]
    print(f"[partition] {fam}{x['statics']}: " + (x.get("error") or
          f"{x['gates']} gates ({x['structure_gates']} structure) -> {x['units']} units {x['by_kind']}, committed interior {x['committed_interior_words']}, "
          f"max |out| {x['max_out_bits']} b, width ok {x['width_ok']}, recomputed {x['recomputed_gates']}, cut {'OK' if x['cut_ok'] else x['cut_codes']}, "
          f"violations {len(x['violations'])}"), flush=True)
ok = all("error" not in x and x["cut_ok"] and x["width_ok"] and x["recomputed_gates"] == 0 and not x["violations"] and x["committed_interior_words"] == 1
         for x in rows if x["family"].startswith("RMSNorm"))
json.dump({"query": W.query_id(16, 32), "ok": ok, "definitions": rows}, open(out_p, "w"), indent=1, default=str)
print(f"PARTITION-NORMS {'OK' if ok else 'FAIL'} ({len(rows)} specializations)")
PY
echo "partition norms rc $?"

# (2) #101 under the norm-scale policy: the strict check as the Build runs it, then the same check non-strict with its groups and violations
verity-vllm manifest build --program "$PROG" --workload "workloads/$ROW.json" --norm-scales --word-check 16/32 --out "$EV/manifest_nr.json" \
  > "$EV/manifest_nr.log" 2>&1; echo "word check strict (no-recompute, norm scales) rc $?"; tail -n 3 "$EV/manifest_nr.log" | cut -c1-600
python - "$EV/word_101.json" "$PROG" "workloads/$ROW.json" <<'PY'
import collections, json, os, sys
from verity_vllm.pipeline import manifest as M

out_p, prog, wl_p = sys.argv[1:4]
P = M.from_instances(os.path.join(prog, "instances.json.gz"))
res = M._load_json(os.path.join(prog, "result.json"))
art = M._load_json(os.path.join(prog, "artifact.json")) if os.path.exists(os.path.join(prog, "artifact.json")) else None
corr = M.Correspondence.of(P, prog, implementation_paths=M.Correspondence.implementation_paths_of(res))
out = {}
for arm, policy in (("norm_scales", M.NS.POLICY), ("record", None)):
    r = M.request_manifest(P, corr, res, workload=M._load_json(wl_p), artifact=art, program_dir=prog, norm_scales=policy)
    w = M.word_check(P, corr, r.required, "16/32", strict=False, acquired=dict(M.NS.TAP_WORDS) if policy else None)
    norm = [dict({k: g[k] for k in g if k != "rule"}, by_kind=g["rule"]["by_kind"], max_out_bits=g["rule"]["max_out_bits"],
                 per_call_committed=g["rule"]["committed_interior_words"]) for g in w["groups"] if g["definition"].startswith(("RMSNorm", "RsqrtF32"))]
    cut = [v for v in w["violations"] if v["class"] == "cut"]
    out[arm] = {"query": w["query"], "ok": w["ok"], **{k: w[k] for k in ("calls", "units", "gates", "committed_interior_words")},
                "acquired_interior_words": w.get("acquired_interior_words"), "manifest_digest": r.manifest["manifest_digest"],
                "violations_by_class": dict(collections.Counter(v["class"] for v in w["violations"])),
                "violations": [{k: v.get(k) for k in ("definition", "class", "calls", "where", "codes", "why")} for v in w["violations"]][:200],
                "cut_violations": [{k: v.get(k) for k in ("definition", "calls", "codes")} for v in cut],
                "recomputed_gates_definitions": sorted({v["definition"] for v in cut if "gate-recomputed" in (v.get("codes") or [])}),
                "norm_groups": norm,
                "norm_calls": sum(g["calls"] for g in norm), "norm_units": sum(g["units"] for g in norm),
                "norm_committed_interior_words": sum(g["committed_interior_words"] for g in norm),
                "norm_acquired_interior_words": sum(g.get("acquired_interior_words") or 0 for g in norm),
                "norm_violations": sum(g["violations"] for g in norm)}
    print(f"[word-101] {arm}: {json.dumps({k: v for k, v in out[arm].items() if k not in ('violations', 'norm_groups')}, default=str)[:1500]}", flush=True)
json.dump(out, open(out_p, "w"), indent=1, default=str)
PY
echo "word 101 rc $?"

# (3) the merged tree's tests (word / partition / norm scales / exactness offline) and the lints
cd $T
python -m pytest integrations/vllm/tests/query/test_word.py integrations/vllm/tests/query/test_norm_scales.py \
  integrations/vllm/tests/query/test_partition_structural.py integrations/vllm/tests/query/test_partition_stubs.py \
  integrations/vllm/tests/acquire/test_norm_tap_src.py integrations/vllm/tests/acquire/test_norm_scale_source.py \
  integrations/vllm/tests/properties/test_norm_tap_exactness.py integrations/vllm/tests/program/test_moe_router_ordered.py \
  packages/verity/tests/ir/test_ir_partition.py -q -p no:cacheprovider -o junit_family=xunit1 --junitxml=$OUT/tests-nrmerge.xml \
  > $OUT/tests-nrmerge.log 2>&1
echo "tests rc=$? $(tail -1 $OUT/tests-nrmerge.log)"
python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py \
  integrations/vllm/tests/test_no_dead_modules.py -q -p no:cacheprovider > $OUT/lints-nrmerge.log 2>&1
echo "lints rc=$? $(tail -1 $OUT/lints-nrmerge.log)"
echo "NT-PARTITION-DONE $(date -u +%FT%TZ)"
