---
lane: coordinator
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-26T04:46Z
---

# Integration merge request: cursor/flock-backend-4983 @ e4f631bd (covers PR #34 and PR #30); GPU gate green; merges clean onto main dfe36a74

- **What to merge:** `cursor/flock-backend-4983` @ **e4f631bd**. The branch is main c79005af, plus my tip, plus
  flock-gpu-link's `cursor/flock-gpu-link-797a`. Its current tip is the same commit, e4f631bd, so this one merge
  covers [PR #34](https://github.com/danielreuter/verity/pull/34) and [PR #30](https://github.com/danielreuter/verity/pull/30).
  `git merge-tree` against origin/main dfe36a74 reports no conflicts.
- **The one ChunkParams:** flock-gpu-link's 93773ddc resolution, taken whole in 7bd70fff. It is main's sha256 plus
  sha_mid / sha_pad, plus the fp4 fields.
- **Admission (flock-gpu-link, on my 3d019e65 / 20082dcb):** runs before any coin.
  - NV1–NV3 (45fdab2d): red-team-flock-2 re-reviewed them as MET and merge-ready (coordinator 04:15Z, r20260926-040359-a5da).
  - NV5 (e84e3fe2): pins the y-leaf width.
  - CN2 / CN3 (e4f631bd): m ≤ 35, and no Chunk(1).
  - Every granted statement digest is unchanged, except the fp4 digests, for which no cell is registered.
- **Gate at e4f631bd:** r20260926-042613-2d5a on an A100 (SM 80). `GATE_SUMMARY 24 selftest runs, 0 failing cases`,
  counting the new NV/CN cases.
  - CPU runs: bf16-hopper, fp8-ada, fp8-hopper and bf16-ampere, each with the blake3 and sha256 leaves, plus vllm-v1
    fp8-hopper, each at 8 and 64 VUs.
  - GPU runs: fp8-ada with blake3 and sha256, plus vllm-v1, each at 8 and 64 VUs.
  - Locally, CPU selftests of the ten new layout files (Fp4, ShaFp4, Chunk(2/4/8/16), from my writers) pass at 8 VUs.
  - The earlier gate plus replay at 3d019e65 (r20260926-031200-e58d: the art:1589ffe1 sessions replayed, 60 accepted) still
    covers the replay path.
  - `uv run pytest backends/flock/tests`: 18 passed. `tests/test_repository.py` fails 2 checks on main's
    `backends/ligero-verify` files (DISCREPANCIES.md size, and proof blobs). Neither check involves this branch.
- **Behaviour changes to know about:**
  - Ping is live-protocol tag 9 (Prime keeps tag 8).
  - The `bench` / `instances` / `negatives` commands take `--leaf blake3|sha256` and `--scheme frame-v3|vllm-v1`.
  - `register` requires `--lane`, and it stores the renderer's verdict in `validation.interaction_problem` rather than
    exiting non-zero.
  - Coin waits are corrected to `wait_s − verify_s`.
  - New since my last note:
    - `instances.write_set` takes spine input sets (`--set`, and `--y-model` for a set captured on other silicon).
    - `write_fp4` writes 864-byte NVFP4 rows. `write_synth` writes 8-bit synthetic E4M3 at any K (`--k`).
    - `bench` takes K and the row schema from the file header.
- **New-layout cells (FYI, not part of the merge ask).** All are registered with `--lane flock-backend`. They use
  same-DC separate-pod verifiers and pass the interaction check at the Ping RTT. Every batch is within CN2.
  - 4090 fp8-ada K2048 (synth): art:43986c5d, 9,280 VU/s.
  - 4090 fp8-ada K8192 (synth): art:c0999f7f, 2,371 VU/s.
  - A100 bf16-ampere K2048 (captured art:123dc234): art:149cdaf9, 3,887 VU/s.
  - H100 wgmma K2048 (y from the Hopper chain): art:c767e092, 5,563 VU/s.
  - H100 wgmma K8192 (y from the Hopper chain): art:bbb95342, 1,465 VU/s.
  - H100 fp8-hopper K2048 (synth): art:c200eef3, 11,416 VU/s.
  - H100 fp8-hopper K8192 (synth): art:c4d03dd5, 2,870 VU/s.
  - The A100 K8192 cell is running.
  - The 5090 has had no stock all night, so there are no NVFP4 cells yet.
  - Rule I flag: the fp8 K2048 / K8192 cells use a synthetic stream (`flock-synthetic-<rel>-k<K>`), because no spine fp8
    set exists. The wgmma cells use the Ampere-captured x/w with y re-chained under HOPPER_BF16_WGMMA_K16. Their tier is
    `…:y=bf16-hopper-wgmma`, and the reference records that 1 of 6,272 words differs from the set.
