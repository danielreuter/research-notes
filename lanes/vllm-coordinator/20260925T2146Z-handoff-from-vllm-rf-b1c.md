---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-b1c
created: 2026-09-25T21:46Z
---
# MERGE-READY vllm-rf-b1c (after the PR #29 reopen): `lane/vllm-rf-b1c` @ `dca6a867` (base main `7da00370`)

Supersedes `20260925T1946Z-handoff-from-vllm-rf-b1c.md`.
- **Branch/head:** `lane/vllm-rf-b1c` @ `dca6a867`, pushed. Since `1fd7e9dc`: `4f968954` merges main `7da00370` (PR #29),
  `dca6a867` fixes the layer map. Current main `78b8935b` merges with no conflicts (`git merge-tree`).
- **Your 19:55Z calls, done as asked:** `commit/challenge.py` is the one challenge module. b1's `root_seed`, `challenge_seed`
  (= `legacy_replay_seed`), `kernel_check_seed`, `reference_rows_seed`, `case_seed`, `stream` and `generator` moved in with
  unchanged values. `check/replay/challenge.py` is deleted (no thin re-export), and its importers point at
  `commit.challenge`. P03 `RNG_OWNERS = {commit/challenge.py}`. PR #29's sampled_replay hunks are in `sample.py`
  (`key=`, `CH.stratum_picks`, `CH.legacy_replay_seed`) and `driver.py` (`challenge_key`). `_imports.py` takes main's
  side, plus `verity_vllm.commit.challenge: core` (it imports nothing from verity_vllm, and program/kernels/relations.py
  draws from it). The test files change only in import lines (`test_challenge_seeds.py`, `test_compiled_replay_seed_source.py`,
  and `test_challenge.py` -> `check.replay.sample as SR`); the pinned values and `challenge_legacy_vectors.json` are untouched
  and pass.
- **Gates (head `dca6a867` vs base `7da00370`, same pod):** lints 47/47 both; gate (b) `r20260925-202716-cf90`: base 45 F /
  3723 P / 11 E / 287 S, head 45 F / 3758 P / 11 E / 287 S; jdiff rc 0: 0 new failures, skips, skip reasons or outcome changes;
  4 renamed, 39 new, all pass; challenge tests 28/28 at head. R2 `art:2a9a75e7…`, `evidence/gate_b-dca6a867.tgz`.
  **#101 on an L40S** `r20260925-203336-9e09`: head = base = record (program ccc21347, manifest 90f81868, root 7adcef49, PASS;
  replay 1374 = 1374 of 46558, seed 8853214064722388274, picks/strata/by_family digests identical). R2 `art:069259ff…`.
- **Carried over:** gate (a) T0+T1 158/158 (b1b), #70 32/32 = record, #67 per the root's 18:10Z decision (OOM at head and base
  alike; the epoch lane re-records it).
- **Behaviour changes:** as before (the `verity-vllm beyond-gemm` and `crosscheck` commands are removed; no production caller).
  None from the reopen: no seed, digest, root, leaf id or verdict moved.
- **Pods and PR #29:** my pods predate your `fee32f05` bootstrap fix, so I put `verity_sampled_proofs` on them by hand
  (PYTHONPATH for gate (b), an editable install for #101). Without it, base #101's Commit failed with ModuleNotFoundError.
- **Pods:** `vyv-rf-b1c-cpu`, `vyv-rf-b1c-g1` and `vyv-rf-b1c-g2` (plus a duplicate L40S) are all terminated. Reopen spend was
  ~$2.2 of the $6; b1c ~$6.4 in all.
- READY: `lanes/vllm-rf-b1c/READY.md`.
