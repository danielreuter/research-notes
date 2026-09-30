---
id: 20260930T1445Z-handoff-from-vllm-config-run-tp2-commit-gpu-hold
campaign: overnight-sep30
lane: vllm-config-run-tp2
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-config-run-tp2
to: vllm-coordinator
cc: nebius-infra
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---
# Config-run Commit GPU hold: 436 s -> 83-88 s on the SmolLM2 B1 cell, roots byte-identical

**Result.** On SmolLM2-135M rtxpro6000 B1 i256 o32 greedy bi-eager, stage.commit (the GPU hold) went from 436 s (recorded cell
cov-k01-10) and 563 s (cold probe) to 88 s and 83 s. All 35 root/digest fields of the committed run are identical to cov-k01-10:
run root a48fbe4eb4a31fcf, replay 460/460 with seed 11857905589137121231, the same weights and Program digests. Nothing vLLM
executes changed. The 460 uniform draw, the replay fields and the warm-up are all untouched.

**Cause: not vLLM, and not the warm-up's own work.** A py-spy profile of the warm-up puts it in `torch.utils.cpp_extension` running
ninja: the `hidden_gpu_tree` extension was rebuilt at every Commit, about 110-170 s of nvcc each time.
- `native_jit.jit_load` keys the build dir by source digest, which is correct, but torch writes each tree's own source path into that dir's
  `build.ninja`. The next job from any other tree therefore rewrites it, and ninja rebuilds.
- The shared `/workspace/jobs/torch-extensions/hidden_gpu_tree/8879fa424900/.ninja_log` holds about 38 such rebuilds today.
- The rebuilds run under the host-wide build lock, so concurrent cells queue behind each other. That explains the 137-632 s warm-up
  spread.
- The native collector (`/workspace/cp/nc_build/4e713f39b5f2`, 20 builds) has the same bug, costing ~30 s in committer_setup.
- Second cause: Kueue pods have an ephemeral HOME (`/home/sky`, no `~/.triton`), so Triton recompiles the batch-invariant kernels in every
  pod (36 cache entries). That costs ~80 s of engine.build (vLLM's profile run).

## Per-phase timeline (s; stage.commit = GPU hold)

| phase | cov-k01-10 (recorded) | A: cold Triton, old code | B: warm Triton, old code | E: warm + fix, other tree path | F: warm + fix |
|---|---:|---:|---:|---:|---:|
| engine.build | 78.0 | 93.6 | 12.2 | 15.3 | 13.0 |
| committer_setup | 30.8 | 33.8 | 1.9 | 2.0 | 2.0 |
| warmup_instrumented | 273.6 | 382.6 | 189.0 | **1.6** | **1.6** |
| pair0 control / instrumented | 0.7 / 0.8 | - / 0.8 | - / 1.0 | - / 0.9 | - / 1.0 |
| sampled_replay | 30.0 | 28.9 | 28.4 | 41.9 | 39.6 |
| **stage.commit** | **436.1** | **562.8** | **254.2** | **87.7** | **82.9** |

- Run D (the first fixed run, 297.6 s) builds both extensions once into the fresh staged dirs.
- E runs from a second copy of the tree at another path, and F runs back from the first. Neither rebuilds: the `.ninja_log` build counts stay
  at 2 and 4.
- The ~13 s gap between warmup_control0 and committer_setup is the form-(B) producer facts pass (11 s), which is CPU work.
- The eq tree runs the config-run Commit with `--only-arm instrumented`; cov-k01-10's older tree also ran a control arm. That is a tree
  difference and predates this work; A shows the same.
- Evidence (runs, identity, ninja log, py-spy summary, probe template):
  `notes-asset:internal/lanes/vllm-config-run-tp2/assets/20260930-commit-hold/`.
- The probe was Kueue jobs 196, 203 and 208 on vy-nebius-1, after 13:30Z. It used the Build of r20260930-095004-bd5b, which is
  digest-equal to cov-k01-10.

## PR and template

1. **Code (small, against main).** Branch `cursor/jit-tree-invariant-sources-3847`, head e0c56cb4; the environment opens the PR.
   - `native_jit.jit_load` compiles from a copy of the sources staged in the digest-keyed dir (`<bd>/src/`, rewritten only when the
     bytes differ). `build.ninja` is then the same for every tree of one source set.
   - Two new tests are included. The vLLM lints and the commit tests are green; the one failure, `test_kernel_dump` (a missing `.npz`
     fixture), is pre-existing.
   - No record field names these paths.
2. **Template (nebius-infra; copied there).** In the `gpu` task's run step of `config-run.yaml`, after `SRC=...--mine`:

   ```bash
   case "$ROW" in *__bi-eager) export TRITON_CACHE_DIR=/workspace/jobs/cache/triton/$(basename "$SRC");; esac
   if grep -q staged_sources "$SRC/integrations/vllm/verity_vllm/commit/committer/native_jit.py"; then
     export HIDDEN_GPU_BUILD=/workspace/jobs/cache/jit/hidden_gpu NATIVE_COLLECT_BUILD=/workspace/jobs/cache/jit/nc
   fi
   ```

   - The Triton cache is keyed by tree (the job_tree content id).
   - It is limited to eager rows because compiled rows record `triton_cache_dir` in `generated_kernels` (code_identity), and I have not
     checked those headers.
   - The fresh JIT parents are used only by trees that carry the fix. Old trees would otherwise keep rewriting `build.ninja` and cost
     fixed trees a rebuild.
   - No third task is needed for this.

## Warm-up, eager, gpu_memory_utilization

- **bi-eager:** the log shows compilation mode 0, cudagraph NONE and no capture sizes. Nothing is compiled or captured.
- **Warm-up (`--warmup 1`):** kept as is.
  - It is the bounded-staging learn-only pass: 32 plans, 0 mismatches. The committed run then hits every plan instead of learning.
  - Dropping it would change the committed run's staging path.
  - It now costs 1.6 s, so there is nothing left to save.
- **gpu_memory_utilization:** left alone. With warm caches vLLM's init takes about 3 s ("init engine ... took 3.05 s"), so the KV
  cache size (0.5, 47 GiB here) is not on the hold's critical path. I have no evidence that lowering it saves time.

## Needs your decision

1. **Replay off the GPU (not started).** After the fixes, the B1 hold is ~85 s, of which the replay is 30-42 s. That meets the
   <2 min target without moving it. For B8 i1024 o128 cells, though, the Build lane measured 360-520 s of replay.
   - Moving it needs:
     - the Commit to persist the committed store it retains on the host (440 MB raw here, GBs at B8);
     - a `row stage replay` that reads it plus the Programs;
     - a third Kueue task.
   - The replay also re-registers the **live** model weights and checks them against the committed weights root
     (`weights_check`). A CPU step would have to register the weights of record from the checkpoint instead. That changes what the
     field attests, which is a semantics change and yours to rule on.
   - Go or no-go, and whether B8 cells justify it?
2. **Rollout.**
   - Coverage runs sm_120 cells on pre-merge trees, so the fix only helps trees that carry it: merge the PR, then rebase the
     coverage tree family onto it.
   - The template lines above go to nebius-infra.
