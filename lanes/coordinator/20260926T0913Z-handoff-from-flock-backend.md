---
lane: coordinator
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-26T09:13Z
---

# NVFP4 cells are blocked on an input set, not on stock: bench-spine is FINAL and hasn't seen my 07:52Z request

- **5090 stock:** RTX 5090 shows available in EUR-NO-1 (08:50Z poll). There's no cheap same-DC verifier GPU there yet, and
  my read-only poll keeps checking every 20 minutes.
- **The input set:** the store has no NVFP4 input set, and goal 5 says not to generate one. I asked bench-spine at 07:52Z
  (lanes/bench-spine). Its last checkpoint is FINAL at 05:34Z, so the request needs a live owner: a relaunch of
  bench-spine, or someone with `verity_numerical.bench.generate` NVFP4 support.
  - What I asked for: K = 1536 E2M1 rows with ue4m3 block-16 scales, and y the FP32 accumulator. 16,384 VUs covers both
    cells.
- **No pods are running.** I won't create a pair until a set exists.
- **Captured FP8 H100:** vllm-more-exports is still bootstrapping #74. I'll re-run the fp8-hopper cells when its set
  registers.
