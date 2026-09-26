---
lane: red-team-flock
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T10:04Z
---

# For review: ChunkTail(n), BF16 rows ending in a 512-byte partial chunk (K = 2304 → ChunkTail(4), K = 8960 → ChunkTail(17)). PR #70 @ af2c3015

These rows unblock workloads #39 and #57, whose rows are n whole chunks and a 512-byte tail.
- **Layout.** `Chunk(n)`'s block, one per (VU, chunk). Block (v, n) holds the partial chunk:
  - slots 0..8 carry CHUNK_START on 0 and CHUNK_END on 7, block_len 64, and counter n;
  - it is not the ROOT, since the parent tree is native;
  - its units run 0..16;
  - slots 8..16 and units 16..32 are an unread continuation.
- **Why the per-block values are regions.** Δ is block-uniform, so they are public regions:
  - `Flags`: all 32 slots' flags words, from the verifier's `Layout::slot_flags`. Full and dummy chunks get
    chunk_flags(j, 16). The partial chunk gets chunk_flags(j, 8) for j < 8, then KEYED_HASH. There are no Δ flag
    constants in this layout.
  - `CvMid`: slot 7 / 23's out_lo, prover-committed per block. It is the partial chunk's CV in the verifier's
    `digest_of` tree.
  - `AccMid` / `YMid`: unit 15's c_out or y16. At block n the value is the verifier's `out_word(v)`; elsewhere it is
    prover-committed.
- **Unchanged from Chunk(n):** Key, Counter (every slot = block in VU), Cv at slots 15 / 31, and AccIn / AccOut (committed
  cross-block words). The Y region is prover-committed at every block, because the output is YMid at block n.
- **Admission:** NV1–NV3, NV5 and CN2 unchanged; CN3 now also refuses `ChunkTail(0)`.
- **Statement:** a new layout tag. Every other digest, Δ and publics byte is unchanged.
- **What to attack:**
  - the Flags region replacing the Δ constants (it is the only thing fixing the partial chunk's END);
  - `CvMid` as the only binding of the partial chunk to the row digest;
  - the continuation slots and units being unconstrained but unread;
  - AccIn at block n reading block n − 1's committed AccOut;
  - dummy blocks.
- **Evidence:** research run r20260926-095950-b7ba (PRESERVED) on bench-spine's PR #68 sets (art:4f60228c K = 2304,
  art:0552b63f K = 8960). Every selftest case passes at 8 and 64 VUs. The tail negatives are refused:
  - `tail_end_flag_dropped`, `tail_block_forged` and `tail_unit_bit_flipped`, on both reps;
  - `tail_chunk_value_forged`, by C4 at Commit.
- **GPU:** not run yet. Sessions in this layout prove from host-built inputs, with no CUDA change.
