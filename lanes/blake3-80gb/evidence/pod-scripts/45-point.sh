#!/usr/bin/env bash
# blake3-80gb: one measured point (not a sweep): bench-vu --commit-per-rep, 5 reps, rep 1 dumped, the pod's pinned ligero-verify
# on the dump (producer check), outputs.json -> bench-result/v1 + its proof tree as outputs of the attempt.  REL L P VUS
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:?}; tag=$(echo "$REL-l$L-p$P-n$VUS" | tr '+' '_'); D=$RD/$tag; mkdir -p $D
gpu_idle || exit 3
$PY -m backends.direct.ligero.run --relation ${REL:?} bench-vu --zk --mode interactive --auth included-hash --commit-per-rep \
    --batch ${L:?} --pipeline ${P:?} --total-vus ${VUS:?} --target -128 --reps ${REPS:-5} --device cuda --instance-procs 16 \
    --out $D/result.json --dump-dir $D/proofs --dump-reps 1 > $D/bench.log 2>&1
rc=$?; echo "bench rc=$rc"; grep -E "^rep " $D/bench.log | cut -c1-260
cd $D/proofs || exit 1
$V system-digest --system system.bin > rust_digest.json 2> rust_digest.err; echo "system-digest rc=$? $(head -c 200 rust_digest.json)"
$V batch --system system.bin --dir rep1 --jobs $NT --threads 1 --target-bits 128 --json rust_batch.json > rust_batch.out 2>&1
echo "rust batch rc=$? $(tail -n 1 rust_batch.out | cut -c1-300)"; sha256sum $V > ligero_verify.sha256
cd $RD
$PY - $RD $tag <<'PY'
import json, sys
from pathlib import Path
rd, tag = Path(sys.argv[1]), sys.argv[2]
meta = json.loads((rd / tag / "result.json").read_text())
cont = meta.get("contention") or {}
meta["protocol"] = {"warm": True, "runs": 5, "statistic": "median", "contended": cont.get("contended"),
                    "warm_rule": "one full untimed pass (bench-vu warm-up) before the timed reps, same process"}
meta.update(lane="blake3-80gb", tag=tag, label=f"blake3-80gb {tag} (frozen-size point, not a sweep point)")
outs = [{"name": tag + "-proofs", "kind": "run-files/v1", "tree": f"{tag}/proofs", "meta": {"lane": "blake3-80gb", "tag": tag + "/proofs"}},
        {"name": tag, "kind": "bench-result/v1", "meta": meta, "refs": {"run_files": "@" + tag + "-proofs"}}]
(rd / "outputs.json").write_text(json.dumps({"schema": "research/outputs/v0.1", "outputs": outs}, indent=1, default=str))
print("outputs.json written")
PY
exit $rc
