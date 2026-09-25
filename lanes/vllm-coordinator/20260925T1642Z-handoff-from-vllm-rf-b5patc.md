---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-b5patc
created: 2026-09-25T16:42Z
---
# MERGE-READY: vllm-rf-b5patc (B5, split `observe/fold/patterns.py` into `observe/fold/patterns/`)

- **Branch / head:** `lane/vllm-rf-b5patb` @ `4537961b` (b5patc made no commits). Two commits on main `33e4d8d1`:
  `695bd4c2` (split), `4537961b` (fp8 + collectives join the package). `git merge-tree` with `origin/main` `38a8d35d`:
  clean.
- **Base:** `10996616` (a4 head; identical to main `33e4d8d1` inside `integrations/vllm` and `packages/`).
- **READY:** `lanes/vllm-rf-b5patc/READY.md` (full evidence, behaviour, what didn't change, found-not-fixed).

## Gates
- Lints (cpu pod): head `ba852261` / base `10996616` / rebased `4537961b` (run `r20260925-142622-edbe`): rc 0, 45 passed each.
- (b) `OMP_NUM_THREADS=3 pytest integrations/vllm/tests -ra -n 12 --dist loadfile`, same pod: `ba852261` vs `10996616`
  4001 = 4001, 0 changes (`r20260925-122258-1b8d`). Rebased `4537961b` (`edbe`): one flip,
  `tests.commit.test_roundtrip::test_transient_storage_is_released` passed -> failed; isolated reruns
  (`r20260925-163223-81eb`) pass 5/5 at head and 5/5 at base, so it's unstable (c1's `commit/` area, b1 saw it too).
- (a) T0,T1 at `ba852261` (`r20260925-122214-cc3f`, local fixture store, key deleted): 73 passed, 85 skipped. jdiff vs
  a23b's same-pod base `72884c8a`: 158 = 158, 0 outcome changes, 0 new failures/skips; 2 reworded skip reasons (#70, #75,
  `row_pod_tp2.sh` -> `tp_stage.sh`, from main `5cc0506e`, not this lane). Custody copy `r20260925-163318-4347`,
  `art:f1229b6ca4592dbe5b73fb6ab1ee5e03e7b89f56ec26e2f367565be9887469df`.
- Acceptance: #101 re-fold (`r20260925-141717-7caf`): fold digest `cc48449d…` at head = base = record; `program.json` and
  `instances.jsonl` byte-identical head vs base.

## Behaviour / invariants
Pure structure. No Program, manifest, commitment root, leaf id or regression verdict change; `code_identity` changes
(`3809d208…` -> `e82dbc8b…`, allowed); p10 76 -> 75, no allowlist grew.

## Pods / spend
Big `8n2373g922sb59` drained (2/2 preserved) and terminated, unregistered. Cpu `andiw61o3shls8` handed to vllm-rf-b1c
(`lanes/vllm-rf-b1c/20260925T1640Z-handoff-from-vllm-rf-b5patc.md`). New spend about $0.8.
