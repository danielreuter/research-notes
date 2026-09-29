---
cursor:
  subagentId: "bc-605d7c89-ca73-5a32-a582-ee77c49e762a"
---

lane: coordinator · kind: merge-request · from: merge queue (bc-605d7c89) · to: the research coordinator (bc-8ece7cde) ·
created: 2026-09-29T06:55Z · repo: danielreuter/verity

# Merge request: #368 `research queue`, the `next` branch, admission and landing (change 5, PR 1), check passed

- **PR:** [#368](https://github.com/danielreuter/verity/pull/368), head `c1295898`, base `main` `d120933b`. It's marked ready.
- **Recorded check:** `r20260929-055157-7b33` passed, and it's preserved on R2.
  - It ran on `vy-mq-test-check1`, a cpu3g with 8 vCPU and 32 GB in US-IL-1, under your `vy-mq-test-` guard, in 2663 s.
  - pytest took 414 s, circuit-check 320 s and the cold Lean audit 1289 s.
  - `lean-agreement` passed in 1338 s: 16 of 16 sets, 559 of 559 sessions in agreement.
- **About the agreement (bc-1122c760's AVX-512 warning):** it ran although #368 doesn't touch `backends/flock/`, because `--record` diffs two-dot against `origin/main`; #356 fixes that.
  - The pod's EPYC 9355 has AVX-512 (`avx512f`, `avx512bw`, `avx512vl` and others), so the pinned upstream build ran.
  - Every set's `upstream.txt` is non-empty and every session agrees, so the step's pass is real. I didn't stop it or re-record.
- **What it touches:** only `tools/research`. No circuits, no Lean, nothing under `backends/flock/`. It belongs in a non-Lean train.
- **Conflict to expect:** `tools/research/src/research/cli.py`'s usage docstring against #358. Keep both lines.
- **Behaviour change:** none until someone runs `research queue`. Store labels also accept the new `pr:{n}@{sha}` target, and the vocabulary has a `grant` key.
- **The pod** is still up, now idle. I'm keeping it for #373's recorded check and the two-pod key measurement, within the $5 test budget, and I'll terminate it when those are done. Test spend so far is about $0.25.
