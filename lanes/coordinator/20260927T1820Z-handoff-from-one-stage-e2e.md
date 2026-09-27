---
cursor:
  subagentId: "bc-c520c11b-172b-5758-a4c3-07b2e7956014"
---

lane: coordinator · kind: handoff · from: one-stage-e2e · created: 2026-09-27T18:20Z · status: final · repo: danielreuter/verity ·
origin: PR #168 @ 60f7e28c, run r20260927-170424-8360

# A4 P6 re-audited under the stratified law: accepted and complete, both RMSNorms drawn, ≤ 91,063 of 6,771,765 at 2⁻²⁰

- **The run:** `r20260927-170424-8360`, PRESERVED (record `art:39e89a007c9e`). It's in the checkpoint.
- **The re-audit:** P6's served roots, unchanged, under `stratified:1024`. `previous` is P6's `0d1f8f84…`, and the window
  is tagged `stratified-floor-1`.
- **Draws per template,** matching the law's k_s exactly:

  | template | drawn |
  |---|---|
  | RMSNorm Triton | **1** |
  | GEMM K = 2048 | 933 |
  | RoPE | 2 |
  | RMSNorm fused | **1** |
  | SiLU·mul | 1 |
  | GEMM K = 8192 | 89 |

  That's 1,027 in all. The draw came from Lean #167 `draw --stratified`, and Lean `draw-test` accepts it under the law.
- **The verdicts, 19 of 19:** all six templates proved and verified, plus the stratified-law draw test.
- **The bound:** 91,063, with 286 each for the three 287-unit templates.
- **The negatives, 13 of 13 refused:** your three new ones, the window reuse, and the nine earlier ones.
- **Pod:** an A100-SXM4 pod, since no CPU shape had stock. It ran 56 min and cost about $1.9, and it's terminated. This
  lane's spend is about $8.7 of $40.
- **Details:** `lanes/stratified-law/20260927T1820Z-handoff-from-one-stage-e2e.md`, and PR
  [#168](https://github.com/danielreuter/verity/pull/168).
