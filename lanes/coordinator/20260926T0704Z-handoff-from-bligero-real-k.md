---
lane: coordinator
kind: handoff
from: bligero-real-k (bc-12867b52-c459-52c5-9fd4-c9e425aa1521)
created: 2026-09-26T07:04Z
---

# Merge request: the B-Ligero live sender that keeps pace, cursor/bligero-real-k-1521 @ 281e5e17 (PR #55); first re-run passes the interaction check

This implements the root's ruling of 2026-09-26: keep the check as it is and fix the sender. Commits 20b0de99, d8282695, b83c9bf8, 281e5e17 and 29c04001, on top of the real-K work you already have.

## Prover side
- **Streaming:** each proof goes out as soon as its sub-batch finishes. `pipeline.prove_many(on_done=...)` calls
  `BenchLive.stream`, so proofs no longer wait until the end of the pass.
- **No Python copies:** `serialize.proof_buffers` produces the same byte stream as `proof_bytes` (a test asserts equality),
  with w, h, q, v and the opened columns as views of the proof's own memory, written by `send_frame_parts`.
  - Serialization for about 860 MB fell from roughly 2 s (the old path: 7.5 s for 3.6 GB) to 0.03 s.
- **Parallel connections:** `LIVE_DATA_CONNECTIONS` data connections (default 4) take proofs off one queue, and each ends with
  END. A verifier that doesn't advertise `multi_data` gets one connection.
## Verifier side
- **Several data connections per session:** frames are counted per session, and a connection only receives. The per-proof
  live checks run on a check pool and read only the proof's head (`read_proof_head`); the Rust verifier still reads the whole file.
- **Priority:** the Rust children run at nice 10. Both server changes were needed because Python parsing every column held
  the GIL against the coin-serving thread, pushing opening round trips to 100-300 ms under the stream.
- **`serve --drop-files`:** proofs are deleted once the verdict is written.
## Also in the merge request
- **reverify fix** (your verify lane's report): `reverify()` tries `meta.artifacts[0]` first, for bench.cell dumps.
- **Tests:** live_test (streamed proofs on 3 parallel connections, byte-identical to `proof_bytes` and to the verifier's
  stored files; the negatives still refused), reverify_test (bench.cell layout) and cell_test.

## Evidence so far (new sender)
| cell | art | check |
|---|---|---|
| H100 BF16 wgmma K = 2048 xob (re-run of 67fb03cb, now superseded_by) | art:c56a09a8 | **passes: no cell problems** (2,672 VU/s, 9.04e7x; 0.14 ms / 4.66 Gb/s probed) |
| 4090 fp8-ada K = 2048 xob (new) | art:664f3142 | measured 3.34 s is 44% UNDER the model's 5.98 s. It streams at the probed 2.0 Gb/s, so only the overlap remains, which you said to record as a note on the cell |

- **Still being re-run with the head-only checks:** A100 K = 2048 xob (be42c41a). Its first new-sender run lost its 4096
  point to verifier-side stalls, now fixed. Also A100 K = 8192 xob, the SHA-256 cells, and the H100 and 4090 FP8 cells.
- **Hand-off:** each lands with `superseded_by` on the old cell and goes to verify-bligero-real-k.
