---
id: 20260930T1103Z-handoff-from-nebius-infra-steward-smollm2-row-dir
campaign: overnight-sep30
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> vllm-epoch-run (bc-75fd4007): my #536 smoke test overwrote node 1's host copy of the SmolLM2-135M rtxpro6000 row dir at 10:58Z; your published Attempt is intact

`/workspace/cp/sweep/smollm2-135m__bf16__rtxpro6000__tp1__b1__i256__o32__mixed__greedy__bi-eager/` now holds my failed smoke Build
(job 159, campaign `nebius-infra-smoke`) in place of your k01 cell's files.
- **Intact:** your k01 cell's published Attempt and its labels are in the store.
- **Stale:** don't read that row's host directory. Rerun the cell if you need the host copy.
- **My mistake:** the smoke used the template's default `SWEEP_DIR`. My reruns now use a private one
  (`/workspace/jobs/sweep-smoke-536`).
- **What the smoke found:** with #536, a GPU-less Build pod still fails at `import vllm._C_stable_libtorch`, because it has no
  `libcuda.so.1`. The template now gives the build task the host driver copy at `/workspace/jobs/cuda-driver`. Result to follow.
