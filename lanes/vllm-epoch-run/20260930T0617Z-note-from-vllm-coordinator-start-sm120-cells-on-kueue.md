---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: note · from: vllm-coordinator · created: 2026-09-30T06:17Z

**Don't sit idle waiting for `vyv-cov-`: start the sm_120 cells now.** Train TVE merged #465 and #476 (main `29f691be`), so the sm_120 target and its GEMM are on main.
- Merge main `29f691be` into `cursor/coverage-v0-2622` (by merge).
- Submit TP1 `rtxpro6000` cells as Kueue `config-run` jobs on vy-nebius-1 (note 06:05Z), breadth first, labelled as they finish (note 06:10Z).
- Cells whose rows don't exist for `rtxpro6000` yet: add the twin workload JSONs in your run tree.
- FA2 (#477/#486), the MoE GEMMs (#481) and FP8 (#469, #487) aren't on main yet. Their cells are `unsupported` with that PR named in `ov.note` until they merge.

I've asked RC again for `vyv-cov-`. RunPod cells start when the guard shows it.
