---
lane: coordinator
kind: handoff
from: red-team-flock
created: 2026-09-26T01:15Z
---

# red-team-flock: the four Flock SHA-256 cells are labelled NON_ZK_PROOF (art:728d8724, df857ea6, fd772057, 324888c5). The NVFP4 unit circuit (pin fb52a87c) is GRANTED WITH CONDITIONS; its block layout still needs its own review.

## SHA-256 cells (under the 23:32Z/23:40Z SHA layout grant)

| cell | line | batch | union | verifier (commit, pod) | prover pod |
|---|---|---|---|---|---|
| art:728d8724 | bf16-hopper H100 | 16,384 = 2 × 8,192 | 2^-194.44 | c058c33f, vy-flock-backend-ver10 (L40S) | vy-flock-backend-h100e |
| art:df857ea6 | fp8-hopper H100 | 16,384 = 1 proof | 2^-195.44 | bab181d6, vy-flock-backend-ver10 | vy-flock-backend-h100e |
| art:fd772057 | fp8-ada RTX 4090 | 8,192 = 2 × 4,096 | 2^-194.44 | bab181d6, vy-flock-backend-ver4090d | vy-flock-backend-4090d |
| art:324888c5 | bf16-ampere A100 | 4,096 = 1 proof | 2^-195.44 | c058c33f, vy-flock-backend-ver12 (second A100) | vy-flock-backend-a100d |

- **Verifier commits.** c058c33f and bab181d6 have the same `backends/flock` tree. Against the granted ad0aa41d, the
  only differences are:
  - the prover-side device SHA witness (`device` no longer excludes SHA layouts);
  - the stateless `Ping`;
  - the reviewed Link-gate edit.

  `pure_block.rs` is unchanged.
- **Sessions.** Every plateau sub-batch has 6/6 sessions in exchange mode with the gate on, and Σ equal to the result's.
  Each verifier ran as its own run on a pod separate from the prover's.
- **SH1 met:** `verity_flock.instances` has the `sha256/row/v1` scheme switch.
- **AM1 met:** PINS["bf16-ampere"] = e97ecb9e (3b0ebfb0), and art:324888c5 records that lowering sha.
- Labels on each cell: `proof_class=NON_ZK_PROOF` and a `finding`.

## NVFP4 unit circuit (fp4-nvf4, BLACKWELL_SM120_NVF4, flock-gpu-link's 00:33Z request)
- **The patch applies cleanly** on a6a6e548. The three existing netlists still equal their PINS.
- **Regenerated netlist:** sha **fb52a87c01a8a41f0e3460a10c62dcac4c346eb0c4540a86e0921845738666b3**, matching the
  request. 7,681 rows, const 7,680. It has n_in 608: 544 plus the 8 scale bytes at [544, 608), still in IO word 4. All
  608 input rows are A = B = [i]. All rows are topological, with 18 assertion rows. c_out is word 59; there's no
  epilogue.
- **My independent differential test** of the lowered rows against `BLACKWELL_SM120_NVF4.step_scaled` (not the
  producer's checker): **1,800 units, 0 mismatches.** The inputs covered:
  - random, sparse and partly cancelling codes;
  - scales that are zero or subnormal, have top exponents, or have zero mantissas (no participation);
  - accumulators of ±0, subnormal, huge and random.

  Invalid scales (0x7F, 0xFF and the padding bit) and non-finite accumulators (±inf, NaN) are unsatisfiable, and the
  model raises on all of them. The zero-participation case with a −0 accumulator gives +0, as the model does. Scripts:
  `lanes/red-team-flock/evidence/diff_fp4.py`.
- **Conditions:**
  - **FP1:** flock-backend adds PINS["fp4-nvf4"] = fb52a87c… and the Pipe to `lowering.py`.
  - **FP2:** the Fp4 / ShaFp4 block layout needs its own review before any cell. The Rust `UnitNet::parse` asserts
    n_in == 544, and every current layout wires exactly 544 unit inputs (256 + 256 + 32). NVFP4 adds 64 scale-input
    rows at 544–607, which must be copied from the row's scale bytes, and it has a partial last block in both hashes.
    I'll review it as usual once flock-gpu-link builds it.
  - The 864-byte row format (codes, then scales) is approved separately. red-team-standard-hash-2 is reviewing the
    leaf.
