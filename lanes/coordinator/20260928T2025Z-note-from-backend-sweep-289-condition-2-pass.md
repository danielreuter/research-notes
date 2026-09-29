---
cursor:
  subagentId: "bc-ea1c2c4f-07dd-56b4-afdd-10e38e1a866f"
id: 20260928T2025Z-note-from-backend-sweep-289-condition-2-pass
campaign: backend-sweep
lane: coordinator
kind: handoff
status: final
repo: verity
origin: backend-sweep (bc-ea1c2c4f)
---

# #289 condition 2: PASS at `788bf662`, run `r20260928-200802-32fc`

This is the result of condition 2 in `20260928T1824Z-merge-request-refinement-train-flock-gemm-witness-289.md`. That merge request is M0's document, so the result is recorded here beside it.

- **Result:** byte identity passes on the GPU at `788bf6629fd4e2eafba31d0fe9d6c406096ac908`.
- **Source:** the bundle `artifacts/pr289-788bf662-on-adcf38bf.bundle` (sha256 `a2ab0cdb…bffbf`).
- **Run:** `r20260928-200802-32fc`, preserved.
  - Settings: the two GEMM coordinates, `BATCH=16 SELFTEST=1 SELFTEST_GPU=1 SELFTEST_CASES=gpu_paths_agree,gpu_proofs_match_cpu`.
  - Hardware: 1× L40S, `r5o8isntyy4q8x`, terminated at 20:18:50Z.
  - Labels: `merge_condition=289-condition-2`, `verdict=pass`.
- **Per coordinate** (K = 2,048 at m = 28 and K = 8,192 at m = 29): accepted, `selftest.all_pass` true on the GPU, and both GPU cases pass.
  - `gpu_paths_agree`: proofs and transcripts equal, `host_units [true, true]`, `rep_reused [false, true]`.
  - `gpu_proofs_match_cpu`: proofs and transcripts equal.
- **Supersedes** `20260928T1935Z-note-from-backend-sweep-289-condition-2.md`, the build break at `9728be8d`.
- **Spend:** $0.70 of the $3 cap, all attempts included. No `vyb289-` pod is left, and the guard is stopped.
