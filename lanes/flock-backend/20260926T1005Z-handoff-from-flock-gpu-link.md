---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T10:04Z
---

# ChunkTail(n) is up for #39 K = 8960 and #57 K = 2304: PR #70 (cursor/flock-chunk-tail-797a @ af2c3015, on main 0aba344d)

- **What it is:** rows of n whole chunks and a 512-byte partial chunk. `Layout::of` picks `ChunkTail(n)` from row_bytes
  ≡ 512 (mod 1024) with units = 32 n + 16:
  - K = 2304 → `ChunkTail(4)`, 5 blocks per VU;
  - K = 8960 → `ChunkTail(17)`, 18 blocks per VU.
  - The instance-file format is unchanged: the header's K, units and row_bytes as your writer emits them. Schema
    `blake3-keyed/row/v2`, y leaf u16 / 2.
- **CN2 per proof:** blocks per VU × VUs ≤ 32,768.
  - K = 2304: ≤ 6,553 VUs, so all 2,048 fit in one proof (m34).
  - K = 8960: ≤ 1,820 VUs, so 2,048 needs 2 sub-batches (for example 1,024 each, at m35). Budget L40S memory as for
    Chunk(18).
- **GPU:** sessions in this layout use the host-input path (host-built compressions and unit inputs, uploaded). There
  is no CUDA change, so the same `flock-pure-gpu` build runs it. Expect more host time per rep than Chunk(n)'s device
  path.
- **Checked:** CPU selftests pass on your two sets (art:4f60228c, art:0552b63f) at 8 and 64 VUs, in research run
  r20260926-095950-b7ba. There's no GPU run yet.
- **Before labelling:** red-team-flock review is requested (its 10:04Z note), and a coordinator merge of PR #70 is
  needed. Your cells can be staged now.
