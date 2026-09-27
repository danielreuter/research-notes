---
cursor:
  subagentId: "bc-c520c11b-172b-5758-a4c3-07b2e7956014"
---

lane: coordinator · kind: handoff · from: one-stage-e2e · created: 2026-09-27T10:55Z · status: open · repo: danielreuter/verity ·
origin: PR #143 @ 108e2e54, run r20260927-101433-97d7

# A4 P4 is accepted and complete on serving's own roots: #101's layer 0 without GEMM, 12,341 units, ≤ 158 wrong at 2⁻²⁰

- **The run:** `r20260927-101433-97d7`, PRESERVED; driver [#143](https://github.com/danielreuter/verity/pull/143) @ `108e2e54`.
- **The input:** vllm-serving-commit's bundle `art:6719029d…`.
  - It comes from their served run `r20260927-092505-bee3`, which #101 PASSes with the `vllm-v1` run root unchanged.
  - Registration `c2b8ec64…`, partition P4 `46f80472…`, `subset:1024`, `window.kind: served`.
- **The checks before the draw all passed:**
  - per member: the pin, partition, program, global indices, classes and template program digest, and the roots and
    recomputed served domains;
  - for the audit: R1–R6 and the source.
- **The verdicts, 12 of 12:** M0's verifier, the Lean draw test and Lean verify (#142 `712ae5f7`,
  `verity/flock-circuit@967b8d06`) each accept all four members, and Lean derives the units from the verifier's own program.
- **Draws per template** (you asked for these). There was one Lean draw over the whole population, and each member was
  served its share.

  | Member | n | expected | drawn |
  |---|---|---|---|
  | RMSNorm Triton | 287 | 23.8 | 21 |
  | RoPE | 11,480 | 952.6 | 951 |
  | RMSNorm fused | 287 | 23.8 | 23 |
  | SiLU·mul | 287 | 23.8 | 29 |

- **The bound and the negatives:** at most 158 wrong units of 12,341 except with probability 2⁻²⁰. The negatives were 4 of 4
  refused: R2, R3, a draw outside the partition, and a proved set short of the draw.
- **Versions:**
  - Serving's files were written with M0 `68ae79f2`, and the checks ran against that.
  - The session ran on the verifier's re-headered copies for M0 `e226a920`'s circuit, which keys `program_digests` by
    descriptor id as Lean needs. The classes are unchanged, and the leaf layer is byte for byte serving's.
- **Cost:** 30 min on the CPU pod, about $0.32. This lane's overnight pod spend is about $4 of the $40 cap.
- **P6:** its inputs are staged, and it's waiting on serving's P6 bundle (M0 `e226a920`, per-instance `units.classes`). If it
  misses about 11:30Z, this run stands as A4. The pod stays up for P6.
