#!/usr/bin/env bash
# agkr-bound: register the integration v2 check (r20260925-051328-c48b) and the public-input bound dev pass
# (r20260925-050836-bdba) as gate-log/v1 trees.  usage: bash 07_put.sh
set -euo pipefail
IN=$RESEARCH_RUN_DIR/inputs
R=/workspace/research/runs
T=/workspace/agkr-bound/integ2-evidence; rm -rf $T; mkdir -p $T
cp $R/r20260925-051328-c48b/stdout.log $T/integ_v2_stdout.log; cp $IN/06_integ_v2.sh $T/
for c in bf16-ampere bf16-hopper fp8-hopper fp4-nvf4; do
  mkdir -p $T/$c; cp /workspace/agkr-bound/integ2/$c/run/{result.json,prove_reps.json,verify_independent.json,verify_rep0.json} $T/$c/
  cp /workspace/agkr-bound/integ2/$c/bench.log $T/$c/
done
bash $IN/04_store.sh put $T '{"lane": "agkr-bound", "what": "A-GKR integration v2 = 2994bd25 (a2edab4d + origin/main c1891d48 circuit pins + fp8-ada/fp8-hopper merged-LK and --no-merge + fp4-nvf4 pin lines, merge_tables torch-free) on A100 vy-agkr-bound: verifier cargo test 11+4, backends/gkr pytest (tests 8 incl. circuit pins, gpu/v2 16, packed 38+9s, tensor 21+1s, fused 8+17s); one bench_result cell per family with verify --relation R, circuit_pinned true, proof sha256 equal to the verified cell: bf16-ampere f2c05851 (art:300a526a), bf16-hopper 4a05ada6 (art:c09947fd), fp8-hopper 0021aa91 (art:ad76c106), fp4-nvf4 ebe7c545 (art:f277786d)", "run_id": "r20260925-051328-c48b", "source_commit": "2994bd25fa0c94cdf8ff82292f8019628fd861d9", "candidate": "A-GKR"}' --ref integration_v1=art:c347036b
T=/workspace/agkr-bound/bound-pi-evidence; rm -rf $T; mkdir -p $T
cp $R/r20260925-050836-bdba/stdout.log $T/bind_dev_stdout.log; cp $IN/02_bind_dev.sh $IN/03_negatives.py $T/
for c in bf16-ampere fp8-hopper fp4-nvf4; do
  D=/workspace/agkr-bound/dev/$c; mkdir -p $T/$c/neg $T/$c/statement
  cp $D/run/{result.json,prove_reps.json,verify_independent.json,verify_rep0.json} $T/$c/; cp $D/bench.log $T/$c/
  cp $D/run/statement/{bind.txt,instances.txt,manifest.json} $T/$c/statement/
  cp $D/neg/negatives.json $D/neg/mutate.json $T/$c/neg/; cp $D/neg/*/verify_*.json $T/$c/neg/ 2>/dev/null || true
  for k in honest unbound_alt bound_alt alt_xbin; do for f in $D/neg/$k/verify_*.json; do cp $f $T/$c/neg/${k}_$(basename $f); done; done
done
bash $IN/04_store.sh put $T '{"lane": "agkr-bound", "what": "A-GKR operands bound as PUBLIC inputs (intermediate, not the full relation: coordinator 0507Z), lane/agkr-bound b5299000 on A100: relation R+bound (circuit files pinned under R, x.bin/w.bin/public words pinned under R+bound in verifier/src/instances.rs); per family 1 rep 4096 VUs, Rust verify --relation R+bound accepts (soundness -130.19, binding batching term <= 2^-161.6); negatives each NEGATIVES OK: wrong operand word with the honest y rejected by Rust + Python (ligero functional) and clear mode, the same proof without bind.txt accepted under R (the gap), a bound statement under R and an unbound one under R+bound rejected, altered x.bin rejected by the instance pin, mutate 17/17 rejected. bf16-ampere t.total 0.843, fp8-hopper 0.399, fp4-nvf4 0.327 (A100, 1 rep, not Table 2 cells)", "run_id": "r20260925-050836-bdba", "source_commit": "b5299000", "candidate": "A-GKR", "variant": "A-GKR, operands bound (public inputs)"}'
