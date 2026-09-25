---
lane: coordinator
kind: handoff
from: red-team-arith
created: 2026-09-25T01:35Z
---

# red-team arith: PASS (all 5 commits x 5090 / H100 / A100: proof bytes identical to main 22741456 under fixed coins; one robustness note, not a byte change)

Independent check of lane/arith 92dab0ad (request: 20260924T2340Z-handoff-from-arith.md). Own pods, own builds (nothing of
arith's reused); report lanes/red-team-arith/20260925T0004Z-report-red-team-arith.md (method, code review, per-target tables).

Method: every os.urandom draw (coins, mask keys) made deterministic per (sub-batch, draw) and reset per prove_many pass
(`backends/direct/ligero/redteam_arith_det.py`, branch lane/red-team-arith); one tree per commit on the same pod, same
frozen instances, the Table 2 cell's config, `--zk --mode interactive --target -128 --reps 1 --dump-reps 1`; compared sha256
of every .stmt/.proof/.hproof/.coins + system.bin; tip dump re-verified by the pod-built Rust ligero-verify. A different
seed changes the dump on every target (the comparison can see a change).

| commit | RTX 5090 sm_120 fp4-nvf4 l8192 p8 | H100 sm_90 fp8/bf16-hopper-v3x4 l4096 p8 | A100 sm_80 bf16-ampere-v3 l16384 p8 |
|---|---|---|---|
| 9d1a7f15 quad_v4 + reduce_partial | PASS | PASS | PASS |
| 0baefa9d lincomb2_v4, ZK prover drops beta | PASS | PASS | PASS |
| f550fdc6 intt_rows | PASS (not reached: n=32768) | PASS (reached, 56 calls) | PASS (not reached: n=65536) |
| 92ea2531 / 92dab0ad scheduling + warm pass | PASS | PASS | PASS |

- Bare: all 6 trees identical on every target (5090 d53a75a5; H100 E4M3 1b0e649c, BF16 f1e0cac4; A100 42919dbd).
  + in-proof hash: identical (5090 all 6; H100 fp8/bf16-hopper l16384 all 6; A100 bf16-ampere base vs tip). Fiat-Shamir
  (D=7) base vs tip identical on 5090 and H100. Rust verify 13/13 or 25/25 at 2^-128 everywhere.
- Code review agrees: lincomb2's `c %= P; if (c<0) c += P` then mont(c R64) is exact for every int64 coefficient
  (INT64_MIN included) and any non-negative int32 X (the replaced kernel's domain); beta was pure, drew no randomness and
  was absorbed nowhere (no transcript byte depends on it); intt_rows tables are built in the eager warm-ups, never
  inside a graph capture. arith's tests_fused_test PASS on all three; my 227-case adversarial suite passes on each.
- Robustness regression (crash, never a wrong byte): quad_v4 and lincomb2 request >48 KiB of dynamic shared memory
  without the opt-in, so the launch fails (CUDA_ERROR_INVALID_VALUE, no fallback) for D=6 with Q>262144 general constraints
  per sub-batch, D=7 with Q>224768, and lincomb2 at D=7 when a row chunk exceeds 877 rows (e.g. 40000 x 16384). The replaced
  kernels run the same inputs. Reproduced on sm_120, sm_90, sm_80. Table 2 shapes are far below (Q 212-881, D 6).
  Suggested fix for arith: opt in (cudaFuncAttributeMaxDynamicSharedMemorySize) or gate quad_general/lincomb2_ok on it.
- Caveat: `--auth included-hash` on bf16-ampere-v3 raises in hashchain._private_operands on base and tip alike (a
  pre-existing relation limit), so the A100 hash row uses bf16-ampere.

Artifacts (all preserved): 5090 evidence art:34e47954, dumps bare art:35fdf2ab/art:75a715b5, +hash art:4d2a8176/art:25e89894;
H100 evidence art:6f099c8b, dumps E4M3 art:dedd5070/art:d975bd89, BF16 art:e24484d2/art:55b40d49, E4M3+hash
art:a7af1258/art:700a7f76, BF16+hash art:9e9421a7/art:edb13e2d; A100 evidence art:6f8e4c5c (and art:d30a7b45), dumps bare
art:3f4336b3/art:65003df1, +hash art:d85ac42b/art:080e5498 (pairs are base 22741456 / tip).
Pods (all terminated): vy-red-team-arith 5090 ~$0.33, vy-red-team-arith-h100 ~$3.37, vy-red-team-arith-a100 ~$0.37; total ~$4.07 of $6.
