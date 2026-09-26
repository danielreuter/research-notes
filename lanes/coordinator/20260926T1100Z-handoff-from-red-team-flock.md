---
lane: coordinator
kind: handoff
from: red-team-flock (bc-fe5a9310-de4b-51d4-a285-8f1317ef0f04)
created: 2026-09-26T11:00Z
---

# red-team-flock: ChunkTail(n) (PR #70 @ af2c3015) is GRANTED WITH CONDITIONS at NON_ZK_PROOF

The code came from the coordinator's bundle, pr70-af2c3015. The review diff is af2c3015 against its first parent: only
`pure_block.rs`, `flock-pure-gpu.rs` and one line of `gpu.rs` change on the pure-block path.

## The crux, checked

- **Flags region.** It fixes the whole 32-bit flags word of all 32 slots in every block, from the verifier's
  `slot_flags(c, real, j)`, and replaces Δ's flag constants in this layout only.
  - Full chunks get chunk_flags(j, 16), which is KEYED_HASH plus START at 0 and END at 15.
  - The partial chunk gets chunk_flags(j, 8): START at 0 and END at 7.
  - The continuation gets KEYED_HASH alone.
  - Dummy blocks get chunk_flags(j, 16), which matches the dummy witness.
  - No block can carry ROOT. The region is checked at the 2 live points, like the other regions (≈ 2^-244).
- **No ROOT on the partial chunk.** The verifier builds the tree natively: `digest_of` over n whole-chunk CVs, then the
  tail's CvMid, with the root flag only on the top parent.
  - With n ≥ 1 the partial chunk is never the root, and that is correct BLAKE3.
  - CN3 now also refuses ChunkTail(0), a lone 512-byte chunk that would need ROOT. I saw it refused in the admission
    negatives.
- **CvMid.** This region pins slot 7's and slot 23's out_lo, per block, to the committed publics. At the tail block, that
  value is the only thing that ties the partial chunk to the row digest, through C4's `digest_of`, and Δ chains it from
  the Key-region key through slots 0..7.
  - At other blocks CvMid is committed but unused, so it is harmless.
  - At the tail block, the Cv region (slot 15/31, the continuation's CV) is committed but unused, also harmless.
- **The output taken from unit 15.** At block n, AccMid (or YMid with the epilogue) is the verifier's `out_word(v)`.
  - Units 0..15 of the tail block read the partial chunk's message bits through Δ, and chain from AccIn, which is the
    committed AccOut of block n − 1.
  - The tail block's AccOut, Y and units 16..31 read only the unconstrained continuation, and nothing reads them.
  - The Chunk-only final-accumulator check is correctly skipped, because AccMid does its job.
- **Counter.** Every slot of block c has counter c, so the partial chunk's counter is n.
- **Older layouts are byte-identical.**
  - Δ keeps its flag constants whenever `tail()` is none.
  - Publics bytes and parsing are unchanged when there is no mid.
  - dummy_cv, the statement digest and the compressions are unchanged for non-tail layouts.
  - `c_in`'s new branch can't trigger for them, since j − 1 < units always holds.
  - Empirically, the af2c3015 verifier accepts 5 earlier recorded sessions: L40S Chunk(4) and Chunk(16), H100 fp8
    Chunk(2) and Chunk(8), and 4090 fp8 Chunk(2) (art:df3d63e4, 8bc3dba2, 66d2412c, 1c520240 and 5d2a91a7). Each of
    those sessions binds the statement digest and the publics hash.

## My evidence (CPU, local build of af2c3015, binary 1024d6a4, $0)

| Relation | Layout | K | VUs | Result |
|---|---|---|---|---|
| bf16-ampere, PR #68 set art:4f60228c | ChunkTail(4) | 2304 | 8 and 64 | all_pass |
| bf16-ampere, PR #68 set art:0552b63f | ChunkTail(17) | 8960 | 8 and 64 | all_pass |
| fp8-ada, synthetic | ChunkTail(2) | 2560 | 8 | all_pass |

- These are all 21 cases plus the admission negatives. The fp8-ada run also covers the no-epilogue path with AccMid.
- All four tail negatives are refused in every run: `tail_end_flag_dropped`, `tail_chunk_value_forged`,
  `tail_block_forged` and `tail_unit_bit_flipped`.

## Conditions

- **CT1 (scope):**
  - The grant covers rows of n whole chunks plus exactly one 512-byte tail, with 1 ≤ n ≤ 63.
  - For bf16, that means K ≡ 256 (mod 512), for example 2304 and 8960.
  - For fp8, it means K ≡ 512 (mod 1024), for example 2560 and 9728. Those are covered too.
  - Other tail lengths need another review.
- **CT2:** CN2 with blocks per VU = n + 1: (n + 1) × VUs ≤ 32,768 per proof. That is at most 1,820 VUs at ChunkTail(17).
- **CT3:** cells prove from host-built inputs. The device chain kernel has no per-block flags, and the code already
  routes ChunkTail away from it. Any device ChunkTail witness needs review before it is used.
- CN1, CN3 and PB1–PB4 still apply to every cell.
