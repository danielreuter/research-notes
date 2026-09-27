#!/usr/bin/env bash
# f3_check.sh: FA3's per-iteration Check_inf chain (Attention_v4, opt-in) on the CPU, in git clones of the shipped commit and of BASE_SHA:
# (1) nothing of record moves with the selector off: the registry version, the builder vocabulary's version, the target profiles' digests and
# records, and the attention Definition every (T, NH, KVH, D, seqlen_q) binds on the FA2 / FA3 / Ampere targets, head vs base; (2) the partition
# checker (Q_word_v1{X=16,W=32,R=no-recompute}) on Attention_v4 at the FA3 geometries (hd 64 / 128, decode and prefill tiles), with the
# committed-value counts against the policy formulas, and the AttentionHead_v4 cut; (3) the touched tests and the lints.
set -u
S=$PWD; OUT=$RESEARCH_RUN_DIR; EV=$OUT/evidence; mkdir -p "$EV"; ROOT=/workspace/research; T=/workspace/gc2/f3head; TB=/workspace/gc2/f3base
if [ -n "${WAIT_RUN:-}" ]; then while grep -q '^ "state": "running"' "$WAIT_RUN/status.json" 2>/dev/null; do sleep 30; done; echo "waited for $WAIT_RUN $(date -u +%FT%TZ)"; fi
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=""
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
mkdir -p /workspace/gc2; rm -rf $T $TB
git clone -q --no-checkout $ROOT/git/verity.git $T && git -C $T checkout -q --detach "$RESEARCH_SOURCE_SHA" || { echo "CLONE-FAIL $RESEARCH_SOURCE_SHA"; exit 3; }
d=$(diff -rq -x .git -x __pycache__ -x READY.json $S $T | grep -v "^Only in $S" | wc -l); echo "tree $T @ $(git -C $T rev-parse HEAD) vs shipped: $d differing entries"
[ "$d" = 0 ] || exit 4
git clone -q --no-checkout $ROOT/git/verity.git $TB && git -C $TB checkout -q --detach "${BASE_SHA:?}" || { echo "CLONE-FAIL base $BASE_SHA"; exit 3; }
echo "base $TB @ $(git -C $TB rev-parse HEAD)"
cat > $OUT/record_digests.py <<'PY'
import hashlib, json, sys
from verity_vllm.program.frontend.provenance import registry_version
from verity_vllm.program.frontend.rules.vocab import PROFILE_B1_EAGER_V3
from verity_vllm.program.frontend.target_profile import TargetProfile
from verity_vllm.program.registry import targets as TG
profiles = {"h100-fa3": TargetProfile(compute_capability=(9, 0), num_sms=132, flash_attn_version=3),
            "h100-default": TargetProfile(compute_capability=(9, 0), num_sms=132),
            "h100-fa2": TargetProfile(compute_capability=(9, 0), num_sms=132, flash_attn_version=2),
            "l40s": TargetProfile(compute_capability=(8, 9), num_sms=142)}
ids = []
for name, tp in profiles.items():
    for D in (64, 128):
        for NH, KVH in ((32, 8), (4, 2), (8, 8)):
            for sq in (1, 5, 130, 1024):
                for T in (1, 2, 64, 127, 128, 129, 191, 192, 193, 256, 287, 527, 1031):
                    ids.append(f"{name}|{TG.attention_spec(tp, T, NH, KVH, D, sq).id}")
out = {"registry_version": registry_version()["digest"], "vocabulary_b1_eager_v3": PROFILE_B1_EAGER_V3.version,
       "profiles": {n: tp.digest().hex() if isinstance(tp.digest(), bytes) else tp.digest() for n, tp in profiles.items()},
       "profile_json": {n: tp.to_json() for n, tp in profiles.items()},
       "describe": {n: TG.describe(tp) for n, tp in profiles.items()},
       "attention_specs": len(ids), "attention_specs_sha256": hashlib.sha256("\n".join(ids).encode()).hexdigest()}
json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)
print(json.dumps({k: out[k] for k in ("registry_version", "vocabulary_b1_eager_v3", "attention_specs", "attention_specs_sha256")}), flush=True)
PY
for side in head base; do
  R=$T; [ $side = base ] && R=$TB
  (export PYTHONPATH=$R/integrations/vllm:$R/packages/verity/src:$R/tools/research/src:$R/protocols/sampled_proofs
   cd $R/integrations/vllm && python $OUT/record_digests.py "$EV/record_digests_$side.json" > "$EV/record_digests_$side.log" 2>&1; echo "record digests $side rc $?")
done
python3 - "$EV" <<'PY'
import json, sys
ev = sys.argv[1]
h, b = (json.load(open(f"{ev}/record_digests_{s}.json")) for s in ("head", "base"))
diff = sorted(k for k in b if h.get(k) != b[k])
print(f"[digests] head vs base (selector off): {len(b)} records, differing: {diff or 'none'}; attention specs {h['attention_specs']} "
      f"sha {h['attention_specs_sha256'][:16]} = base {b['attention_specs_sha256'][:16]}", flush=True)
PY
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd $T/integrations/vllm
python - "$EV/partition_v4.json" <<'PY'
import json, sys, time
from verity_vllm.query import word as W
from verity_vllm.program.registry import fa3_check_inf as F3
from verity_vllm.program.registry import targets as TG
DOT, INV = {"fn": "HopperBF16WgmmaDot16_v1"}, {"fn": "Fa3InvSum_v1"}
rows, cuts = [], []
for D, NH, KVH in ((64, 32, 8), (128, 32, 8)):
    for sq, T_list in ((1, (5, 129, 130, 287, 527)), (287, (5, 129, 130, 193, 287))):
        for T in T_list:
            row = 0 if sq == 1 else T - 1                                  # a decode row, or row T-1 of a 287-row prefill
            g = NH // KVH
            BN, kBM = TG.fa3_kblock_n(D, sq, g), TG.fa3_tile_m(D, sq, g)
            mf = F3.fa3_masked_from(T, BN, row, kBM, g)
            st = {"T": T, "NH": NH, "KVH": KVH, "D": D, "BN": BN, "DOT": DOT, "INV": INV, "MASKED_FROM": mf}
            t0 = time.time()
            r = W.unit_rule(W.specialization("Attention_v4", st))
            cut = [v for v in r["violations"] if v.get("class") == "cut"]
            heads = {}
            for i in r["committed_interior"]:
                heads[i["head"]] = heads.get(i["head"], 0) + i["words"]
            nb = -(-T // BN)
            e = {"D": D, "seqlen_q": sq, "row": row, "T": T, "BN": BN, "kBM": kBM, "MASKED_FROM": mf, "units": r["units_per_call"],
                 "violations": len(r["violations"]), "recompute_violations": sum("gate-recomputed" in (v.get("codes") or []) for v in cut),
                 "max_out_bits": r["max_out_bits"], "guard_words": heads.get("GuardNegInfZero_v1", 0), "guard_formula": NH * max(0, nb - 1 - mf),
                 "max_scaled_words": heads.get("F32MulFtz_v1", 0), "max_scaled_formula": NH * (nb - (T - (nb - 1) * BN == 1)),
                 "seconds": round(time.time() - t0, 1)}
            rows.append(e)
            print(f"[partition-v4] {json.dumps(e)}", flush=True)
for mf in (0, 1, 2):
    st = {"T": 287, "D": 128, "BN": 128, "DOT": DOT, "INV": INV, "MASKED_FROM": mf}
    G = W.Graph(W.specialization("AttentionHead_v4", st))
    R = W.units(G, 16, 32)
    c = {"MASKED_FROM": mf, "cut_ok": bool(R["cut"].ok), "codes": list(R["cut"].codes), "recomputed_gates": len(G.recomputed), "width_ok": bool(R["ok"].all()),
         "detail": {k: v for k, v in R["cut"].detail.items() if not isinstance(v, dict)}}
    cuts.append(c)
    print(f"[head-cut-v4] {json.dumps(c)[:500]}", flush=True)
ok = all(e["violations"] == 0 and e["recompute_violations"] == 0 and e["max_out_bits"] <= 32 and e["guard_words"] == e["guard_formula"]
         and e["max_scaled_words"] == e["max_scaled_formula"] for e in rows) and all(c["cut_ok"] and c["recomputed_gates"] == 0 and c["width_ok"] for c in cuts)
json.dump({"query": W.query_id(16, 32), "rows": rows, "head_cuts": cuts, "ok": ok}, open(sys.argv[1], "w"), indent=1)
print(f"PARTITION-V4 ok={ok} rows={len(rows)} cuts={len(cuts)}", flush=True)
PY
echo "partition v4 rc $?"
cd $T
python -m pytest integrations/vllm/tests/program/test_fa3_check_inf.py integrations/vllm/tests/properties/test_fa_tap_exactness.py \
  integrations/vllm/tests/query/test_guarded_max.py integrations/vllm/tests/query/test_word.py integrations/vllm/tests/program/test_registry_one_process.py \
  integrations/vllm/tests/program/test_target_profile.py "integrations/vllm/tests/program/test_kernel_self_check.py" -q -p no:cacheprovider \
  -o junit_family=xunit1 --junitxml=$OUT/tests-f3.xml > $OUT/tests-f3.log 2>&1
echo "tests rc=$? $(tail -1 $OUT/tests-f3.log)"
python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py \
  integrations/vllm/tests/test_no_dead_modules.py -q -p no:cacheprovider > $OUT/lints-f3.log 2>&1
echo "lints rc=$? $(tail -1 $OUT/lints-f3.log)"
echo "F3-CHECK-DONE $(date -u +%FT%TZ)"
