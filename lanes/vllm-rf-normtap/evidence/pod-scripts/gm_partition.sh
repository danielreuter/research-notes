#!/usr/bin/env bash
# gm_partition.sh: the no-recompute partition checker (Q_word_v1{X=16,W=32,R=no-recompute}: query/word.py + verity.ir.partition.validate_unit_cut)
# on the attention Definitions, in a LOCAL TRIAL MERGE of cursor/no-recompute-partition-289b and cursor/vllm-rf-guarded-max-57d5 (the shipped
# commit, never pushed): every attention specialization #101 runs (FA2), Gemma's softcap attention and FA3's, with each committed interior
# value mapped to the stream field that carries it (the guarded max -> ROW word 3 under the guarded-max tap).  Then #101's whole-Program check,
# and the merged tree's tests and lints, in a git clone of the shipped commit.  Evidence under $RESEARCH_RUN_DIR/evidence.
set -u
S=$PWD; OUT=$RESEARCH_RUN_DIR; EV=$OUT/evidence; mkdir -p "$EV"; ROOT=/workspace/research; T=/workspace/gc2/gmmerge
if [ -n "${WAIT_RUN:-}" ]; then while grep -q '^ "state": "running"' "$WAIT_RUN/status.json" 2>/dev/null; do sleep 30; done; echo "waited for $WAIT_RUN $(date -u +%FT%TZ)"; fi
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
mkdir -p /workspace/gc2; rm -rf $T
git clone -q --no-checkout $ROOT/git/verity.git $T && git -C $T checkout -q --detach "$RESEARCH_SOURCE_SHA" || { echo "CLONE-FAIL $RESEARCH_SOURCE_SHA"; exit 3; }
d=$(diff -rq -x .git -x __pycache__ -x READY.json $S $T | wc -l); echo "tree $T @ $(git -C $T rev-parse HEAD) vs shipped: $d differing entries"
[ "$d" = 0 ] || exit 4
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd $T/integrations/vllm
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
PROG=/workspace/gm/sweep/$ROW/build_request

python - "$EV/partition_attention.json" "$PROG" <<'PY'
import collections, json, sys, time
from verity_vllm.query import word as W
from verity_vllm.query import guarded_max as GM
from verity_vllm.query.program_view import from_instances
from verity_vllm.query.required import FLASH_ATTENTION_LAUNCHES

out_p, prog = sys.argv[1], sys.argv[2]
FIELD = {"GuardNegInfZero_v1": "ROW word 3 (the guarded-max tap)"}
NOT_CARRIED = {"F32MulFtz_v1": "not carried: ROW word 2 is the kernel's visit index (vt_step), not max * scale"}


def field(scope, head):
    return FIELD.get(head) or NOT_CARRIED.get(head) or W.committed_today(scope, head) or "no stream field (a new tap)"


def rule_of(fam, statics):
    t0 = time.time()
    r = W.unit_rule(W.specialization(fam, statics))
    cut = [v for v in r["violations"] if v.get("class") == "cut"]
    return {"units": r["units_per_call"], "gates": r["gates"], "max_out_bits": r["max_out_bits"], "violations": r["violations"],
            "recompute_violations": sum("gate-recomputed" in (v.get("codes") or []) for v in cut), "redundant_gates": r.get("redundant_gates", 0),
            "committed_interior": [dict(i, field=field(i["scope"], i["head"])) for i in r["committed_interior"]],
            "committed_interior_words": r["committed_interior_words"], "seconds": round(time.time() - t0, 2)}


def head_cut(fam, statics):
    f = W.specialization(fam, statics)
    G = W.Graph(f)
    R = W.units(G, 16, 32)
    return {"family": fam, "statics": statics, "cut_ok": bool(R["cut"].ok), "codes": list(R["cut"].codes), "recomputed_gates": len(G.recomputed),
            "width_ok": bool(R["ok"].all()), "detail": {k: v for k, v in R["cut"].detail.items() if not isinstance(v, dict)}}


doc = {"query": W.query_id(16, 32)}
P = from_instances(f"{prog}/instances.json.gz")
calls = collections.Counter((c.family, json.dumps(dict(c.statics), sort_keys=True, default=str)) for c in P.calls if c.family in FLASH_ATTENTION_LAUNCHES)
by_head, specs, bad = collections.Counter(), [], []
for (fam, st), k in sorted(calls.items(), key=lambda kv: json.loads(kv[0][1]).get("T", 0)):
    r = rule_of(fam, json.loads(st))
    for i in r["committed_interior"]:
        by_head[(i["head"], i["field"])] += i["words"] * k
    specs.append({"family": fam, "statics": json.loads(st), "calls": k, **{x: r[x] for x in ("units", "gates", "max_out_bits", "committed_interior_words",
                  "recompute_violations", "redundant_gates")}, "violations": len(r["violations"])})
    if r["violations"]:
        bad.append({"family": fam, "statics": json.loads(st), "violations": r["violations"][:4]})
doc["row101"] = {"attention_calls": sum(calls.values()), "specializations": len(specs), "violations": bad,
                 "committed_interior_words": sum(s["committed_interior_words"] * s["calls"] for s in specs),
                 "units": sum(s["units"] * s["calls"] for s in specs), "recompute_violations": sum(s["recompute_violations"] for s in specs),
                 "by_value": [{"head": h, "field": f, "words": w} for (h, f), w in by_head.most_common()],
                 "guarded_max_words_policy": sum(GM.attention_words(P).values()), "specs": specs}
print(f"[partition] #101 attention: {doc['row101']['attention_calls']} Calls, {len(specs)} specializations, violations {len(bad)}, "
      f"recompute violations {doc['row101']['recompute_violations']}", flush=True)
for e in doc["row101"]["by_value"]:
    print(f"[partition]   {e['head']:28s} {e['words']:>10,}  {e['field']}", flush=True)
print(f"[partition]   policy words (query.guarded_max.attention_words): {doc['row101']['guarded_max_words_policy']:,}", flush=True)
# Gemma's softcap attention (FA2, hd 256, kBlockN 64) and FA3's (H100, hd 64 / 128, kBlockN 128): the Definitions themselves
other = {}
for name, fam, base in (("softcap", "AttentionSoftcap_v1", {"NH": 8, "KVH": 4, "D": 256, "BN": 64, "CAP": 50.0}),
                        ("fa3_hd64", "Attention_v2", {"NH": 32, "KVH": 8, "D": 64, "BN": 128, "DOT": {"fn": "HopperBF16WgmmaDot16_v1"}, "INV": {"fn": "Fa3InvSum_v1"}}),
                        ("fa3_hd128", "Attention_v2", {"NH": 32, "KVH": 8, "D": 128, "BN": 128, "DOT": {"fn": "HopperBF16WgmmaDot16_v1"}, "INV": {"fn": "Fa3InvSum_v1"}})):
    rows = []
    for T in (5, 130, 287):
        try:
            r = rule_of(fam, dict(base, T=T))
            g = sum(i["words"] for i in r["committed_interior"] if i["head"] == "GuardNegInfZero_v1")
            rows.append({"T": T, "units": r["units"], "violations": len(r["violations"]), "recompute_violations": r["recompute_violations"],
                         "guard_words": g, "guard_words_formula": base["NH"] * (-(-T // base["BN"]) - 1), "max_out_bits": r["max_out_bits"],
                         "by_value": [{"head": i["head"], "field": i["field"], "words": i["words"]} for i in r["committed_interior"]]})
        except Exception as e:
            rows.append({"T": T, "error": f"{type(e).__name__}: {e}"[:300]})
        print(f"[partition] {name} T={T}: {json.dumps({k: v for k, v in rows[-1].items() if k != 'by_value'})}", flush=True)
    other[name] = rows
doc["definitions"] = other
# one head, cut detail: every gate certified once, reads through committed values, widths, recomputed gates
cuts = []
for fam, st in (("AttentionHead_v3", {"T": 287, "D": 64, "BN": 128}), ("AttentionHead_v3", {"T": 129, "D": 64, "BN": 128}),
                ("AttentionHeadSoftcap_v1", {"T": 130, "D": 256, "BN": 64, "CAP": 50.0}),
                ("AttentionHead_v2", {"T": 287, "D": 128, "BN": 128, "DOT": {"fn": "HopperBF16WgmmaDot16_v1"}, "INV": {"fn": "Fa3InvSum_v1"}})):
    try:
        cuts.append(head_cut(fam, st))
    except Exception as e:
        cuts.append({"family": fam, "statics": st, "error": f"{type(e).__name__}: {e}"[:300]})
    print(f"[partition] head cut {json.dumps(cuts[-1], default=str)[:600]}", flush=True)
doc["head_cuts"] = cuts
json.dump(doc, open(out_p, "w"), indent=1, default=str)
print("PARTITION-ATTENTION-DONE", flush=True)
PY
echo "partition attention rc $?"

python - "$EV/word_101.json" "$PROG" "workloads/$ROW.json" <<'PY'
import collections, json, os, sys
from verity_vllm.pipeline import manifest as M
out_p, prog, wl_p = sys.argv[1:4]
P = M.from_instances(os.path.join(prog, "instances.json.gz"))
res = M._load_json(os.path.join(prog, "result.json"))
art = M._load_json(os.path.join(prog, "artifact.json")) if os.path.exists(os.path.join(prog, "artifact.json")) else None
corr = M.Correspondence.of(P, prog, implementation_paths=M.Correspondence.implementation_paths_of(res))
r = M.request_manifest(P, corr, res, workload=M._load_json(wl_p), artifact=art, program_dir=prog)
w = M.word_check(P, corr, r.required, "16/32", strict=False)
att = [g for g in w["groups"] if g["definition"].startswith("Attention")]
out = {"query": w["query"], "ok": w["ok"], **{k: w[k] for k in ("calls", "units", "gates", "committed_interior_words")},
       "violations": [{k: v.get(k) for k in ("definition", "class", "calls", "codes")} for v in w["violations"]],
       "attention": {"groups": len(att), "calls": sum(g["calls"] for g in att), "units": sum(g["units"] for g in att),
                     "committed_interior_words": sum(g["committed_interior_words"] for g in att), "violations": sum(g["violations"] for g in att)}}
json.dump(out, open(out_p, "w"), indent=1, default=str)
print(f"[word-101] {json.dumps(out)[:1500]}", flush=True)
PY
echo "word 101 rc $?"

cd $T
python -m pytest integrations/vllm/tests/query/test_guarded_max.py integrations/vllm/tests/query/test_word.py integrations/vllm/tests/query/test_norm_scales.py \
  integrations/vllm/tests/query/test_partition_structural.py integrations/vllm/tests/query/test_partition_stubs.py \
  integrations/vllm/tests/properties/test_fa_tap_exactness.py packages/verity/tests/ir/test_ir_partition.py -q -p no:cacheprovider \
  -o junit_family=xunit1 --junitxml=$OUT/tests-gmmerge.xml > $OUT/tests-gmmerge.log 2>&1
echo "tests rc=$? $(tail -1 $OUT/tests-gmmerge.log)"
python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py \
  integrations/vllm/tests/test_no_dead_modules.py -q -p no:cacheprovider > $OUT/lints-gmmerge.log 2>&1
echo "lints rc=$? $(tail -1 $OUT/lints-gmmerge.log)"
echo "GM-PARTITION-DONE $(date -u +%FT%TZ)"
