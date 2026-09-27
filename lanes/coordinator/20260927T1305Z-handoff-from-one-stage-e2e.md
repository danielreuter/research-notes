---
cursor:
  subagentId: "bc-c520c11b-172b-5758-a4c3-07b2e7956014"
---

lane: coordinator · kind: handoff · from: one-stage-e2e · created: 2026-09-27T13:05Z · status: open · repo: danielreuter/verity ·
origin: PR #143 @ 9515b4d4, run r20260927-120715-3086; PR #116 @ 608e7130

# A4 P6 is accepted and complete: #101's whole layer 0 with GEMM on serving's own roots, 6,771,765 units, ≤ 91,051 wrong at 2⁻²⁰

- **The run:** `r20260927-120715-3086`, PRESERVED; driver [#143](https://github.com/danielreuter/verity/pull/143) @
  `9515b4d4`, on #116's red-team fixes.
- **The input:** vllm-serving-commit's bundle for served run `r20260927-102240-f954`, which #101 PASSes with the `vllm-v1`
  run root unchanged. Registration `0d1f8f84…`, partition P6 `631d88f8…`, `subset:1024`.
- **The checks before the draw all passed,** including the grid rule on every shared-row reference.
- **The verdicts, 12 of 12:** M0's verifier, the Lean draw test and Lean verify (#142, `@967b8d06`) accept all four drawn
  members, and the served shares equal the Lean draw.
- **The bound:** at most 91,051 wrong units (1.34%) except with probability 2⁻²⁰.
- **The negatives, 9 of 9 refused,** including the new C1, C2, roots and R4 cases.
- **Draws per template,** drawn against expected:

  | template | drawn | expected |
  |---|---|---|
  | GEMM K = 2048 | 923 | 933.3 |
  | GEMM K = 8192 | 97 | 88.9 |
  | RoPE | 3 | 1.74 |
  | SiLU·mul | 1 | 0.043 |
  | RMSNorm Triton | 0 | 0.043 |
  | RMSNorm fused | 0 | 0.043 |

  The two RMSNorms went undrawn, as the uniform law predicts. Their roots and domains were checked before the draw. That's
  the stratified-draw question for Daniel.
- **Two failed attempts first, both preserved:**
  - `r20260927-110739-dd76`: the pod's stale `served/` directory held P4's files. `pod.sh` is fixed (#116 `608e7130`).
  - `r20260927-112223-cc25`: M0's `prove` was OOM-killed at 64 GB on GEMM K = 2048's 6.17 M instances. Its memory
    scales with the population, not the draw; I've told M0 (`lanes/flock-netlist/20260927T1200Z`).
  - Attempt 3 ran on a 256 GB pod and peaked at 86.6 GB.
- **#116:** at `608e7130`, carrying C1–C3, N1 and the five negatives. The delta check was requested
  (`lanes/red-team-flock-3/20260927T1120Z`).
  - A1 bound `r20260927-110313-402a` and A3b `r20260927-115041-1b5d`, both at the new head, are accepted.
  - A3b: ≤ 37 of 856, served = Lean draw, 10 of 10 negatives.
- **Pods:** all terminated. This lane's pod spend overnight is about $7.3 of the $40 cap. The morning summary follows by
  14:30Z.
