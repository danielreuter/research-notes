---
id: vllm-rf-b4c/state
lane: vllm-rf-b4c
kind: state
updated: 2026-09-25T16:55Z
---
# b4c (engine and hooks: re-gate after c1): state

**b4c succeeds b4b** (bc-892f86c5; its session ended at the 16:03Z laptop restart). Agent bc-3b287dbf (cloud), coordinator
bc-ecac3029. Start commit **`5c05ff6d`** (`lane/vllm-rf-b4b`, rebased onto main `8b3537d5` = c1). No b4c branch: no commits
needed so far. Brief: `$STORE/internal/lane-briefs/vllm-b4c.md`. Budget $8 of new spend.

## Log
- 16:25Z first checkpoint. Worktrees on the VM: `/workspace-wt/head` (`5c05ff6d`), `/workspace-wt/base` (`8b3537d5`).
- 16:47Z `vyv-rf-b4b-cpu` bootstrapped (--cpu, BOOTSTRAP-OK; AMD EPYC 9965, 32-CPU affinity, 128 GB cgroup) + pytest-xdist 3.8.0.
- 16:48Z gate (b) + lints launched on cpu, head and base concurrently (`tools/gate_b.sh`; XMLs kept at `/workspace/b4c/{head,base}/`):
  base `r20260925-164820-0072`.
- `vyv-rf-b4b-g1` L40S driver 580.159.04 / CUDA 13.0: no replacement needed. Bootstrap (gpu) running; `tools/g1.sh` on the pod.

## Running
- cpu: gate (b) head and base.
- g1: bootstrap (FA2 matReq tap build), then #101 + non-interference at head.

## Next
1. jdiff base vs head on cpu; lints count (expect 47).
2. #101 at head vs record (program ccc21347…, manifest 90f81868…, run root 7adcef49…, commit PASS; non-interference 992/992).
3. READY.md for `5c05ff6d`, merge-ready handoff, pods handed to vllm-rf-b5vab.

## Open questions
- b4b's (READY.md, `../vllm-rf-b4b/`) carry over: `engine.hooks` / `engine.env` in the `core` P9 layer; import-time pins in three CLIs.

## Found, not fixed
- b4b's list carries over (`../vllm-rf-b4b/READY.md`).
- The Project-store mount returns EAGAIN (`BlockingIOError: [Errno 11]`) intermittently on reads, stats and rewrites; the
  research CLI (checkpoint, pods sync via machines.d) needs retries.
