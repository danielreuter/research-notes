---
lane: flock-gpu-link
kind: handoff
from: flock-vllm-v1 (bc-9713144f-acde-5fa5-9c0b-667f89154cdd)
created: 2026-09-25T23:02Z
---

# FYI: flock-vllm-v1 touches three of your files, additively (branch cursor/flock-vllm-v1-4cdd, based on flock-backend a6a6e548 ⊃ your 48045063)

No action needed; this is so a later merge of your branch and mine doesn't surprise you. Everything else of mine is in
new files (`live/src/vllm_block.rs`, `live/src/bin/flock-vllm-v1.rs`, `pod/40-vllm-v1.sh`).

- `cuda/prove_chunk.cuh` (commit 2f3849f2):
  - `FlockChunkParams` gains three trailing fields, `host_z / host_a / host_b`. When `host_z` is set in mode 1, the whole
    packed z, a, b come from the host (cudaMemcpy, then your `chunk_zlin_transpose`), and every witness kernel is skipped.
  - `pure_comb_expand` takes `sub_log` (it was hard-wired to 14), and `pure_eq_gather` for the compression slots uses
    `sub_log`. Your BLAKE3 path passes 14, so nothing changes for it.
  - The shape check is unchanged for your path. The host-witness path allows ≤ 256 slots and k_log 20..22.
- `live/src/gpu.rs`: the struct fields and `none()` for the above, `statics_with` → `statics_for(comp, da, db)` (your
  `statics_with` calls it with `comp()`), and a new `pub fn prove_vllm`. `prove_pure` gets `host_*: null()`.
- `live/src/lib.rs`: `pub mod vllm_block;`, plus the origin/main merge resolution (your Σ-in-root_F check is kept beside
  route-a-live's P-live check; the verdict keeps `handle_s` beside `prime_rounds`).

Your `flock-pure-gpu` builds and its behaviour is unchanged. My GPU selftest (21 cases, H100, r20260925-225318-3959) ran
on top of your pure-mode kernels.
