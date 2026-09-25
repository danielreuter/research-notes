---
id: vllm-rf-c2/state
lane: vllm-rf-c2
kind: state
agent: bc-568d82f4 (Cursor), coordinator bc-ba6cec03
updated: 2026-09-25T08:58Z
---
# c2 (Definition library, D8/D9, decision 3a): state

a4 base: 10996616

- Worktree `~/projects/verity-wt/rf-c2`, branch `lane/vllm-rf-c2` from `10996616`.
- Budget: $25 of pod spend. Spent so far: `vyv-rf-c2-cpu` from 08:51Z at $1.28/h.

## Commits
(none yet)

## Running
- `vyv-rf-c2-cpu` (RunPod `v34wij1rkanus8`, cpu3g 32 vCPU / 128 GB, EPYC 7702P, registered guard 90): base tree
  syncing to `/workspace/base`, then bootstrap, then step 1 (`tools/equality.py`).

## Next
1. Step 1 on the pod at base: `tools/equality.py` (exhaustive conversions, Hopper k16 specials + 7.4 M seeded cases,
   Gemm_v2 / Const encoding equality) + `tests/program/test_derived_rows.py`.
2. Digest-neutral commit: cite core for the four duplicates, `const`, and `DotBf16/GemmCoordinate/Gemm _v2`; one-process
   load test; drop the four P1 `definition-id` entries.
3. Gates: lints, gate (b) head vs base (this pod), gate (a) T0+T1 (cpu3m 512 GB), GPU Build #101 (L40S),
   Hopper: CPU re-encode of #73/#74 stored Programs.
4. Inventory; move silicon/basic Definitions core lacks (with old-vs-new equality tests).
5. Epoch commit (AmpereBF16TcDot16 v1 -> v2) at the tip, separate.

## Open questions
(none)

## Found, not fixed
- Two collisions beyond the allowlisted four block a one-process import of `verity.ml` + the integration registry:
  `Const<w>[0x..]_v1` (b1.py's own `const()` vs core's; core makes `ZERO32` at import) and `DotBf16_v2`,
  `GemmCoordinate_v2`, `Gemm_v2` (b1.py vs `verity.ml.gemm`). P1's lint only scans `primitive`/`PrimitiveDefinition`/
  `CompositeDefinition` calls, not the `@composite` decorator, so the second set is not in its allowlist. Fixing both in
  step 2.
