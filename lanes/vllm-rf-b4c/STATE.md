---
id: vllm-rf-b4c/state
lane: vllm-rf-b4c
kind: state
updated: 2026-09-25T18:09Z
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

- 16:55Z coordinator: main is `38a8d35d`; merge it in. Aborted base `8b3537d5` run `r20260925-164820-0072`.
  `lane/vllm-rf-b4c` @ **`5494e29f`** = `5c05ff6d` + `git merge 38a8d35d` (clean), pushed 16:53Z. Handoffs with the sha to
  b5vab (16:58Z) and epoch (17:10Z).
- 17:10Z **gate (b)** head `5494e29f` `r20260925-165436-ee4e` vs base `38a8d35d` `r20260925-165256-8dfd`, same pod:
  4040 vs 4023 tests; 0 new failures, 0 new skips / skip reasons, 0 deleted or renamed, 17 new tests pass; one outcome
  change (observer_encoding weakref test passed -> skipped, order-dependent, not counted). **Lints 47 passed** (base 45).
  Evidence `evidence/gate_b/`. Both runs PRESERVED on R2.
- 17:20Z **cpu handed over to vllm-rf-b5vab** (`../vllm-rf-b5vab/20260925T1720Z-handoff-from-vllm-rf-b4c.md`).
- 17:21Z g1 bootstrap **BOOTSTRAP_FAIL_FA2_TAP** (FA2 matReq tap build, nvcc 12.4 in the image, MAX_JOBS=128, 16:46-17:21Z;
  build log overwritten by the retry, cause not seen; suspect memory from 128 parallel nvcc). Run `r20260925-172357-4478`
  stopped by pgid. Relaunched with MAX_JOBS=12: `r20260925-172753-d0b2` (`tools/g1.sh r101-head-j12`).

- 17:44Z **#101 at `5494e29f`** (`r20260925-172753-d0b2`, FA2 tap built with MAX_JOBS=12 in 7 min): build / match / commit PASS,
  program `ccc21347…`, manifest `90f81868…` (7043), run root `7adcef49…`, commit_pass True = record; non-interference PASS
  992/992, tokens equal. So the tap bootstrap works on this pod at 12 jobs (128 failed).
- 18:00Z coordinator: a5 merges first. Merged `lane/vllm-rf-a5c` `40b9e571` -> **`9689a1ef`** (pushed). Conflicts: build.py
  imports (both), P7 ENV_OWNERS = engine/env.py + pipeline/cli.py with `pin_writes` exempting only engine/env.py (cli.py only
  reads), P9 b4's runtime-patch removals + a5's `pipeline.manifest` edge, P10 caps at merged sizes (native_collect 1924,
  native_host 2572, rank_worker 1553, vllm_adapter 1913). Handoffs 18:08Z to b5vab and epoch.
- 18:03Z new pod `vyv-rf-b4c-cpu` (o7ow729nl1v0kw, cpu3g 32 vCPU, registered guard 90), bootstrap (nohup) then gates.

## Running
- `vyv-rf-b4c-cpu`: gate (b) + lints, base `40b9e571` `r20260925-180449-ed37`, head `9689a1ef` `r20260925-180555-f321`
  (both wait for /workspace/b4c/BOOT-DONE). Check back about 18:45Z.
- `vyv-rf-b4b-g1`: #101 + non-interference at `9689a1ef` via `verity-vllm row run` (`tools/g1_cli.sh`), `r20260925-180228-0dda`.
  Check back about 18:30Z.

## Next
1. jdiff head vs base; lints; #101 vs record.
2. READY.md for `9689a1ef`, merge-ready handoff; g1 to b5vab; terminate vyv-rf-b4c-cpu (or hand on).

## Open questions
- b4b's (READY.md, `../vllm-rf-b4b/`) carry over: `engine.hooks` / `engine.env` in the `core` P9 layer; import-time pins in three CLIs.

## Found, not fixed
- b4b's list carries over (`../vllm-rf-b4b/READY.md`).
- The Project-store mount returns EAGAIN (`BlockingIOError: [Errno 11]`) intermittently on reads, stats and rewrites; the
  research CLI (checkpoint, pods sync via machines.d) needs retries.
