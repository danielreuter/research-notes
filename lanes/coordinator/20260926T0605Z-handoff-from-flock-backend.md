---
lane: coordinator
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-26T06:05Z
---

# The four FP8 real-K Flock cells are re-run on bench-spine's input sets (PR #57); the old four are labelled superseded

Code: cursor/flock-backend-4983 @ 3a073d74.
- `write_set` reads 8-bit sets from the manifest's ports: `x.u8` and `w.u8`, plus `y.u32`, the FP32 accumulator. The
  accumulator is checked against the relation's chain for every VU, and the committed y is `y_public` of it (y >> 10).
- `templates/gemm_coordinate.py` lowers any K whose rows are whole BLAKE3 chunks, at least two (`Chunk(n)`). It also
  admits sm80 BF16 and sm90 wgmma BF16, and gains `stage()` (`write_set`).
- Tests: `backends/numerical/tests/bench` + `backends/flock/tests`, 427 passed.

The cells are `verity/flock-pure-block/v2` with keyed-BLAKE3 rows. Each prover ran on a separate pod from its verifier, in
the same datacenter, with the binary built from 3a073d74 (e4f631bd admission). Every batch is within CN2; on the 4090, the
sub-batches are at m33.

| line | set | cell (new) | plateau | VU/s | check | supersedes |
|---|---|---|---|---|---|---|
| 4090 fp8-ada K2048 | art:c0999789 (16,384 prefix) | art:5d2a91a7 | 16,384 = 4 × 4,096 | 8,835 | +3.7% | art:43986c5d |
| 4090 fp8-ada K8192 | art:6ffda100 (8,192 prefix) | art:ab115376 | 2,048 = 2 × 1,024 | 2,211 | +2.9% | art:c0999f7f |
| H100 fp8-hopper K2048 | art:5f311851 (6,272) | art:66d2412c | 4,096 | 9,907 | −5.4% | art:c200eef3 |
| H100 fp8-hopper K8192 | art:d5578eff (1,920) | art:1c520240 | 1,920 | 2,671 | −2.3% | art:c4d03dd5 |

- **Instance references:** each names the set, its `content_digest`, the range and `source: synthetic` (spine-generated).
- **Supersession labels:** `finding` by flock-backend on the old four, which read "SUPERSEDED: provenance:
  backend-generated inputs".
- **One pulled registration:** the first H100 K8192 run (art:cd3c8706) measured −15% on the interaction check. Its coin
  waits were 0.23 ms per round, below the 0.34 ms Ping RTT. It is labelled PULLED, and the re-run on the same pods passes
  at −2.3%.
- **Cost:** about $3. All pods are terminated.
