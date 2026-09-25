#!/usr/bin/env bash
# agkr-bound: register the link-route cost runs (18 merged segment, 20 in-unit bits + negatives, 21 dense check + u_t) as
# a gate-log/v1 tree, then preserve the runs.  usage: bash 22_put.sh
set -euo pipefail
IN=$RESEARCH_RUN_DIR/inputs
R=/workspace/research/runs
A=/workspace/agkr-bound
T=$A/link-evidence; rm -rf $T; mkdir -p $T/runs
for r in r20260925-090709-6528 r20260925-092253-7da8 r20260925-092724-d4f8; do cp $R/$r/stdout.log $T/runs/$r.stdout.log; done
cp $IN/18_link_merged.sh $IN/18_wrap.py $IN/20_link_unit.sh $IN/20_link_unit.py $IN/21_dense.sh $IN/21_eq_cpu.c $IN/21_dense_gpu.py $T/
for m in base link; do mkdir -p $T/merged-$m; cp $A/link-merged/$m/bench.log $T/merged-$m/; cp $A/link-merged/$m/run/prove_reps.json $T/merged-$m/ 2>/dev/null || true; done
cp $A/link-unit/link_unit.json $T/
for c in honest bit_flip non_boolean alt_honest_bits alt_alt_bits; do mkdir -p $T/unit-$c; cp $A/link-unit/$c/verify_sc.json $A/link-unit/$c/commitment.txt $T/unit-$c/; done
cp $A/link-unit/honest/circuit.txt $T/unit-honest/circuit.txt
cp $A/dense/dense_gpu.json $T/
du -sh $T
bash $IN/04_store.sh put $T '{"lane": "agkr-bound", "what": "A-GKR route (a) prime-side costs on A100 vy-agkr-bound2 (BF16 4,096 VUs, 393,216 units, frozen bench-instances/v1; benchmarks + scaffold only, the cross-field link NOT built, coordinator 0922Z). (1) link bits as a 3rd segment of the real proof: median t.total 0.819 -> 1.401 s (+71%), proof 21 -> 61 MB, Python verify accepts. (2) link bits IN the unit (tools/link_stub.extend_unit, 32 operand columns x 16 bits, booleanity + recomposition; unit 264 -> 776 columns, 290 -> 1314 wires) under R+sha256 scaffold: median prove 0.776 -> 1.199 s (+55%), committed 109M -> 311M, proof 21 -> 59 MB, Rust verify 3.38 s (--allow-any-circuit --require-commitment) accepts; negatives bit_flip, non_boolean, alt_honest_bits rejected by Rust + Python; alt_alt_bits ACCEPTED (the residual only the cross-field link closes). (3) dense GF(2^128) check for N = 201,326,592 bits (eq(r,i) doubling + byte-table BabyBear^6 coefficients + inner product): A100 torch 0.875 s (eq 0.35, coef 0.51, ip 0.02); CPU EPYC 7742 13 threads ~0.85 s, 1 thread 9.2 s; u_t second-round commitment (128 x 29 bits) own Ligero proof 0.032 s, 471 KB", "run_id": "r20260925-092253-7da8", "source_commit": "86f86084", "candidate": "A-GKR", "variant": "route (a) prime-side cost model"}' --ref scaffold=art:f2f07e3c --ref hash_spike=art:c35a50cd
bash $IN/04_store.sh push r20260925-090709-6528 r20260925-092253-7da8 r20260925-092724-d4f8 r20260925-085244-5d8e
