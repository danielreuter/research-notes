#!/usr/bin/env bash
# ms_merge_check.sh: #102's merge of main (MAIN_SHA) on the CPU, in git clones of the shipped merge commit and of MAIN_SHA.  The #101 manifest
# is built from the STORED record Build (regression fixtures: programs art:a9be8f7c.. build_request/instances.json.gz + records art:a4ea1a18..
# build_request/result.json / artifact.json, sent with the run) by both trees: with every flag off the two files must be byte-identical; with
# --guarded-max they may differ only by the MS class (each stream identity's element range grown by HB x M x NB, geometry `ms`, the manifest
# digest, and the query header's policy text / max_scaled block).  Then the touched test directories and the lints on the merge.
set -u
S=$PWD; OUT=$RESEARCH_RUN_DIR; EV=$OUT/evidence; mkdir -p "$EV"; ROOT=/workspace/research; T=/workspace/gc2/mergehead; TM=/workspace/gc2/main
if [ -n "${WAIT_RUN:-}" ]; then while grep -q '^ "state": "running"' "$WAIT_RUN/status.json" 2>/dev/null; do sleep 30; done; echo "waited for $WAIT_RUN $(date -u +%FT%TZ)"; fi
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES=""
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
B=/workspace/r101store/build_request; mkdir -p $B
cp $OUT/inputs/instances.json.gz $OUT/inputs/result.json $OUT/inputs/artifact.json $B/ && sha256sum $B/* | sed "s#$B/##" | tee $EV/stored_build.sha256
mkdir -p /workspace/gc2; rm -rf $T $TM
git clone -q --no-checkout $ROOT/git/verity.git $T && git -C $T checkout -q --detach "$RESEARCH_SOURCE_SHA" || { echo "CLONE-FAIL $RESEARCH_SOURCE_SHA"; exit 3; }
d=$(diff -rq -x .git -x __pycache__ -x READY.json $S $T | grep -v "^Only in $S" | wc -l); echo "tree $T @ $(git -C $T rev-parse HEAD) vs shipped: $d differing entries"
[ "$d" = 0 ] || exit 4
git clone -q --no-checkout $ROOT/git/verity.git $TM && git -C $TM checkout -q --detach "${MAIN_SHA:?}" || { echo "CLONE-FAIL main $MAIN_SHA"; exit 3; }
echo "main $TM @ $(git -C $TM rev-parse HEAD); merge parents $(git -C $T log -1 --format=%P)"
ROW=llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager
for side in main merge; do
  R=$T; [ $side = main ] && R=$TM
  (export PYTHONPATH=$R/integrations/vllm:$R/packages/verity/src:$R/tools/research/src:$R/protocols/sampled_proofs
   cd $R/integrations/vllm
   python -m verity_vllm.pipeline.cli manifest build --program $B --workload workloads/$ROW.json --out $EV/manifest_off_$side.json > $EV/manifest_off_$side.log 2>&1
   echo "manifest off $side rc $? $(tail -1 $EV/manifest_off_$side.log | cut -c1-160)"
   python -m verity_vllm.pipeline.cli manifest build --program $B --workload workloads/$ROW.json --guarded-max --out $EV/manifest_gm_$side.json > $EV/manifest_gm_$side.log 2>&1
   echo "manifest guarded-max $side rc $? $(tail -1 $EV/manifest_gm_$side.log | cut -c1-160)")
done
sha256sum $EV/manifest_*_main.json $EV/manifest_*_merge.json | sed "s#$EV/##"
python3 - "$EV" <<'PY'
import json, sys
ev = sys.argv[1]
b = {k: open(f"{ev}/manifest_{k}.json", "rb").read() for k in ("off_main", "off_merge", "gm_main", "gm_merge")}
res = {"off_byte_identical": b["off_main"] == b["off_merge"]}
off, gm_main, gm_merge = json.loads(b["off_main"]), json.loads(b["gm_main"]), json.loads(b["gm_merge"])
res["off_manifest_digest"] = off["manifest_digest"]
res["off_identities"] = len(off["identities"])
fam = gm_merge["query"]["attention_hidden_family"]
moved, grow, bad = 0, 0, []
ids = []
for r0, r1 in zip(gm_main["identities"], gm_merge["identities"]):
    if r1.get("family") == fam and isinstance(r1.get("geometry"), dict) and r1["geometry"].get("ms"):
        g = r1["geometry"]
        w = g["HB"] * g["M"] * g["NB"]
        undo = dict(r1, element_range=[r1["element_range"][0], r1["element_range"][1] - w], geometry={k: v for k, v in g.items() if k != "ms"})
        moved += 1
        grow += w
        if undo != r0:
            bad.append(r1.get("op_path"))
        ids.append(undo)
    else:
        if r1 != r0:
            bad.append(r1.get("op_path"))
        ids.append(r1)
q0, q1 = dict(gm_main["query"]), dict(gm_merge["query"])
ms_block = q1.get("guarded_max", {}).pop("max_scaled", None)
for q in (q0, q1):
    q.pop("query_text", None)
    q.pop("query_id_digest", None)
rest0 = {k: v for k, v in gm_main.items() if k not in ("identities", "manifest_digest", "query")}
rest1 = {k: v for k, v in gm_merge.items() if k not in ("identities", "manifest_digest", "query")}
res.update(gm_identities=(len(gm_main["identities"]), len(gm_merge["identities"])), gm_stream_identities_lengthened=moved, gm_ms_words=grow,
           gm_identity_mismatches_after_undoing_ms=bad[:5], gm_query_equal_but_policy_text_and_max_scaled=q0 == q1, gm_max_scaled=ms_block,
           gm_rest_equal=rest0 == rest1, gm_manifest_digests=(gm_main["manifest_digest"], gm_merge["manifest_digest"]),
           gm_main_guard_words=gm_main["query"]["guarded_max"]["words"], gm_merge_guard_words=gm_merge["query"]["guarded_max"]["words"])
res["gm_differs_only_by_ms"] = (not bad and res["gm_query_equal_but_policy_text_and_max_scaled"] and res["gm_rest_equal"]
                                and len(gm_main["identities"]) == len(gm_merge["identities"]))
json.dump(res, open(f"{ev}/merge_manifests.json", "w"), indent=1)
print(f"[merge-manifests] {json.dumps(res)}", flush=True)
PY
for side in main merge; do
  R=$T; [ $side = main ] && R=$TM
  (cd $R && export PYTHONPATH=$R/integrations/vllm:$R/packages/verity/src:$R/tools/research/src:$R/protocols/sampled_proofs
   OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests/query integrations/vllm/tests/pipeline integrations/vllm/tests/properties integrations/vllm/tests/acquire \
     integrations/vllm/tests/commit -q -p no:cacheprovider -n 12 --dist loadfile -o junit_family=xunit1 --junitxml=$OUT/tests-$side.xml > $OUT/tests-$side.log 2>&1
   echo "tests $side rc=$? $(tail -1 $OUT/tests-$side.log)")
done
cd $T
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py \
  integrations/vllm/tests/test_no_dead_modules.py -q -p no:cacheprovider > $OUT/lints-merge.log 2>&1
echo "lints rc=$? $(tail -1 $OUT/lints-merge.log)"
echo "MS-MERGE-CHECK-DONE $(date -u +%FT%TZ)"
