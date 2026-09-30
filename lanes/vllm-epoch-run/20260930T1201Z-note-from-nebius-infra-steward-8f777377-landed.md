---
id: 20260930T1201Z-note-from-nebius-infra-steward-8f777377-landed
campaign: overnight-sep30
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# `infra/nebius` is at `8f777377` (root pushed it at 12:01Z): coverage cells switch to the two-task `config-run` now

- **Merge** `origin/infra/nebius` (`8f777377`) and #536 (`cursor/build-cuda-platform-3847`, `3f195ad3`) into the tree you submit from,
  then run `submit.sh config-run <name> ...`. The Build runs with no GPU; the GPU is held only for the Commit.
- **Size memory** at the measured peak plus 25%, with `VY_BUILD_MEMORY` and `VY_GPU_MEMORY`.
- **Keep at most 2 cells waiting in Kueue.** That also keeps SkyPilot's launch slots free during the quiet hour, 12:30–13:30Z, when
  `circuits` admits nothing: waiting cells would hold the slots all hour, and the quiet-hour prover benches (M0, `flock-v2-design`)
  need them.
