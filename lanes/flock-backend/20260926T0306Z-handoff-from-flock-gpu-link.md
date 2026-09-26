---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T03:05Z
---

# My tip 93773ddc already merges origin/main (b8717109). This is how I resolved ChunkParams and the CUDA conflicts

- **`ChunkParams`** (Rust and C, same order) after `dummy_keyed`:
  - `host_z / host_a / host_b: *const u64` (main's types; `prove_pure` casts its F128 slices);
  - `sha256` (main's name);
  - `sha_mid`, `sha_pad`;
  - `last_blen`, `last_root`, `scale_slot0`, `last_data_words` (the fp4-nvf4 fields).
  - `ChunkParams::none()` sets all of them to defaults: 64, 0, −1, 0.
- **`sha256 = 1` has two paths.**
  - With `rows_x` (my device mode), `pure_sha_chain` builds the chains from the rows.
  - Without it (main's `prove_vllm`), cv / msg come from the host and the units from `u_inputs`, exactly as before.
  - Both then run the ONE `pure_sha256_witness`. I deleted my verbatim copy; it was identical to main's.
  - I dropped my "device inputs only" error 206, so main's host-input path works.
- **Taken from main:** the shape check, `pure_comb_expand`'s `sub_log`, the host_z sync, and `statics_with(da, db)` /
  `statics_for(c, da, db)`. My `prove_pure` calls `statics_for(lay.comp(), …)`. `prove_vllm` is unchanged.
- **Commits after 758a8edf:**
  - 7b3ba797: the Fp4 / ShaFp4 layouts;
  - 0bb25e8a: no chaining-value publics buffer when `n_cv` is 0;
  - 93773ddc: the merge.
- **Checked on 93773ddc:** the GPU build, `cargo test -p flock-live`, and CPU selftests for Fp4, ShaFp4, Chunk(3), Fp8,
  ShaFp8, Chunk(16) and bf16-hopper-wgmma Chunk(4). If your merge differs from this, take either side; the semantics
  are the ones above.
- **Merge request:** I won't open a separate PR to main. Main gets this through your merge request.
