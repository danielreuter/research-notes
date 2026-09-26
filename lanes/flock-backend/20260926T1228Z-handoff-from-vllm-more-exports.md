---
lane: flock-backend
kind: handoff
from: vllm-more-exports (agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4)
created: 2026-09-26T12:28Z
---

# vllm-more-exports: no captured FP8 GEMM sets from #74 today; its Commit doesn't fit a 251 GB H100 pod, so keep the synthetic spine sets for now

- **What passed:** #74 (Qwen3-4B-FP8, H100, B8) passed Build and Match. The Match needed the 32 MiB snapshot cap of record: the derived 137 MB cap thrashed at the 234 GiB cgroup, with 230 GiB of pinned host memory.
- **The unbounded Commit needs about 300 GiB.** Host staging takes 197 GiB pinned, of which the FA3 hidden M1 stream is 136 GiB. The C2 replay's Programs take another 69 GiB of Python objects. I stopped that Commit before it OOM'd, in the oracle compare (run `r20260926-101428-71e2`).
- **The bounded path crashes.** `--bounded-staging --retain-exclude fa3_hidden_m1` would fit: its bound is 158 GiB. But it crashes in finalize with `vllm_v1.fold`: "leaf must be a 32-byte digest" (run `r20260926-115930-46a1`). I didn't patch commitment code under the budget.
- **So no captured FP8 art ids exist.** The two ways to get them are an H100 host with at least 320 GB RAM running the unbounded Commit, or a fix to the bounded/exclude finalize.
- **The format, for when they exist.** Exporter support is on [PR #63](https://github.com/danielreuter/verity/pull/63). The served FP8 GEMM is block-scaled: per 128-tile, 4 wgmma e4m3 k32 steps from +0, then an FFMA promotion by sx·sw, then bf16. So no served FP8 coordinate is an unscaled K-long chain.
  - The exact sets will be `ScaledMmFp8BlockCoordinate<K,128>` at K = 2560 / 4096 / 9728: `x.u8`, `sx.u32`, `w.u8`, `sw.u32`, `y.u16`.
  - `lanes/vllm-more-exports/evidence/derive_fp8_chain_sets.py` writes the same captured bytes as spine-format `gemm-coordinate/k<K>/sm90-wgmma-e4m3` sets (`y.u32` from your chain relation; source "captured inputs, model y").
