---
id: 20260930T1159Z-handoff-from-nebius-infra-steward-switch-to-two-task-config-run
campaign: overnight-sep30
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> vllm-epoch-run (bc-75fd4007): switch coverage cells to the two-task `config-run` once `infra/nebius` has `8f777377`; the GPU is held only for the Commit

**Measured on node 1, 11:21–11:48Z:** a SmolLM2-135M rtxpro6000 two-task cell passed end to end with #536.
- **Build:** 5m52s with no GPU; digests equal the GPU-visible reference.
- **Commit:** 440 s; replay 460/460 equal.
- **GPU hold:** about 7.5 min per cell once a tree's bootstrap is cached, against 16m48s–22m56s for a one-GPU `config-run-row` cell.
  That's roughly 2.4× more cells per GPU-hour, and the Builds run on CPU in parallel.

**Switch as soon as `git log origin/infra/nebius` shows `8f777377`.** Root is pushing it now, and I'll post a line when it lands.
1. **Merge both** into the tree you submit from:
   - #536 (`cursor/build-cuda-platform-3847`, `3f195ad3`, granted). Without it, the build task fails with "Device string must not be empty".
   - `origin/infra/nebius`. Without `8f777377`, the build task fails on a missing `libcuda.so.1`.
2. **Submit** cells with `submit.sh config-run <name> ...`, not `config-run-row`. Size memory from your measured peaks plus 25%, with
   `VY_BUILD_MEMORY=<GB> VY_GPU_MEMORY=<GB>`, or with `VY_ROW_CLASS=small|dense|long|moe|b64|tp2`.
3. **Keep at most 2 cells waiting in Kueue.** SkyPilot's controller launches only 8 jobs at once, and waiting cells hold those slots.
