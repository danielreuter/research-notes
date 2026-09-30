---
id: 20260930T1159Z-handoff-from-nebius-infra-steward-switch-to-two-task-config-run
campaign: overnight-sep30
lane: build-optimization
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> Build owner (bc-47d0a3ed): the two-task `config-run` works with #536; once `infra/nebius` has `8f777377`, your GPU fallback jobs can hold no GPU for their Builds

**What failed for you:** the two-task template's build task hit two problems:
- no vLLM platform on a 0-GPU pod, fixed by #536;
- no `libcuda.so.1` in that pod, fixed by `8f777377`, which gives the build task the host's copy at `/workspace/jobs/cuda-driver`.

**Measured on node 1, 11:21–11:48Z:** a SmolLM2-135M rtxpro6000 cell passed end to end.
- **Build:** 5m52s with no GPU; digests equal the GPU-visible reference.
- **Commit:** 440 s; replay 460/460.
- **GPU hold:** about 7.5 min once cached, against about 18 min per cell on the one-GPU template.

**Switch once `git log origin/infra/nebius` shows `8f777377`.** Root is pushing it; I'll post a line when it lands.
- **Coverage-style cells:** merge #536 (`cursor/build-cuda-platform-3847`, `3f195ad3`) and `origin/infra/nebius`, then submit
  `submit.sh config-run ...`.
- **Build-only benchmark jobs** (`cb-*`, `cr2-*`): run them as CPU-only tasks, following the two-task template's `build` task:
  - no accelerators;
  - `CUDA_VISIBLE_DEVICES=`;
  - `LD_LIBRARY_PATH=/workspace/jobs/cuda-driver`.

  They then hold no GPU at all.
