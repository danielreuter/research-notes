---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-b1c
created: 2026-09-25T19:46Z
---
# MERGE-READY vllm-rf-b1c: `lane/vllm-rf-b1c` @ `1fd7e9dc` (base `40b9e571`, a5c)

- **Branch/head:** `lane/vllm-rf-b1c` @ `1fd7e9dc`, pushed. b1's 12 commits rebased onto main `239c0e28`, merge of main
  `38a8d35d` (`8f94cb48`), P10 fix `ec6219f5`, merge of `lane/vllm-rf-a5c` `40b9e571` (`1fd7e9dc`). Merge order a5 -> b4 -> b1.
- **Gates at 1fd7e9dc vs 40b9e571, same pod** (`r20260925-180315-713f`, vyv-rf-b5pat-cpu): lints 45/45 both; gate (b)
  base 51 F / 3691 P / 11 E / 287 S, head 48 F / 3729 P / 11 E / 287 S; jdiff rc 0: 0 new failures, skips or skip reasons,
  4 renamed, 39 new all pass. Evidence `lanes/vllm-rf-b1c/evidence/gate_b-1fd7e9dc.tgz`, R2 `art:002d54b5…`.
  Gate (a) T0+T1 158/158 = a23b base and #101 head = base = record carry over from b1b at `8c0bec08`.
- **GPU:** #70 TP2 32/32 = f1's record (`r20260925-141723-16b0`). **#67 not produced:** Commit OOM-killed on the 188 GB
  L40S at head AND at base identically (rc 137 at 2598 s / 2676 s, same 32-worker replay fork, shmem 85.8 GiB; admission
  predicted short 11.7 GiB). Not a code change. Per your 18:10Z root decision: gate (a) T1 replay_partition is the MoE
  evidence in READY.md; the OOM runs are recorded as a pod-shape finding; the epoch lane re-records #67.
- **Behaviour changes from the merges:** `verity-vllm beyond-gemm` and `crosscheck` commands removed from `pipeline/cli.py`
  (their modules are test-side since b1's `19ca2453`; no production caller, only manual shell use and the tests); `pipeline/row_stages.form_b` imports `check.replay.coverage`.
  No digest, manifest, root, leaf id or verdict change; no allowlist grew.
- **Found-not-fixed:** `pipeline/commit.py` imports `workload_target` from `pipeline.workload` (it lives in
  `global_program`), so admission `lag` is always 1 (left for the epoch lane); after an OOM kill the engine child keeps the GPU (next Commit on the pod
  fails at vLLM start). Full list in READY.md.
- READY: `lanes/vllm-rf-b1c/READY.md`. Pods: tp2, g2, b5pat-cpu all terminated. b1c spend ~$4.2 of $10.
