---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
lane: coordinator
kind: handoff
from: vllm-cross-call-check (bc-f7aadce6)
to: research coordinator (bc-8ece7cde), tonight's merge pipeline
created: 2026-09-28T01:44Z
---

# Merge request: PR #197, top-p `splits` as a per-step constant for single-request workloads (after #192)

Daniel approved it at 00:25Z. Queue it after M0's prover PR (#192/#193). **It's a statement change: it merges only after
red-team-flock-3 (bc-f0bc7e75) approves**, and the root asks for that review.

- **The PR:** [#197](https://github.com/danielreuter/verity/pull/197), branch `cursor/splits-single-request-constant-666c`, head
  `4497a75d`, on `main` `df3bc5e1`. It merges cleanly on current `main`. Pods cost about $0.45: a CPU pod for about 13 minutes, then
  an L40S for about 22 minutes, both terminated.
- **Contents** (the ruling M-0169 amended for single-request workloads only):
  - A one-request workload's Program takes S = `SplitsFor_v1(1, num_SMs)` as a `Const32[S]` operand and has no `splits` input.
  - The Match holds that constant equal to the fold's S at every event: the compare, GM-01 G3 and X-09's DAG acceptance.
  - Compose refuses a constant-S component in a multi-request workload.
  - The manifest and Commit follow from the missing input: no `sampler_splits`, no splits word.
- **Digest moves (#101):** `ccc21347…` → `79caee21b124d591fe9bc003142660e071aacc443e4a6fdba16a1a6581e4684c`.
  - required-value manifest `90f81868…` → `eb393312…`;
  - workload `a2b43bde…` → `3d7531f8…`;
  - construction version `817b8682…` → `26042284…`;
  - program graph `a2c23989…` → `9fbbb557…`.

  The base Build reproduces the record exactly (`r20260928-012525-4b0f`); the new one is `r20260928-012534-6768`. The
  captured-101 manifests and the 55 store artifacts naming `ccc21347…` stay as the old Program's history, and a #101 re-run
  supersedes them. The PR lists every move.
- **Evidence:** both Builds against #101's recorded fold (`art:34dd1ef2…`) are canonical-equal with the record's own hash
  (`8ff6a1f2…`), 32/32 steps and 102428 operands, and the new constant equals the fold's S at all 32 events.
- **Tests:**
  - local: the touched suites, `tests/check`, `tests/query` and the lint ratchets pass;
  - full `integrations/vllm/tests`: fails the same 12 tests at `df3bc5e1` (CPU torch 2.14 numerics, CUDA driver, closure,
    order), plus one order-dependent test that passes alone;
  - no local `check` run: the pipeline's recorded `check` is the one of record.
- **After it:** the lowering lane (bc-9916bbb1) specialises the top-p keep word on the constant (about −3.9e12 ANDs on #101),
  handed over at `lanes/flock-ir-lowering/20260928T0144Z-handoff-from-vllm-cross-call-check-splits-constant.md`.
