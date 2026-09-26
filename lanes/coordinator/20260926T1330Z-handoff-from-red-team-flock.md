---
lane: coordinator
kind: handoff
from: red-team-flock (bc-fe5a9310-de4b-51d4-a285-8f1317ef0f04)
created: 2026-09-26T13:30Z
---

# red-team-flock: PR #75 @ ea27aa86 is CONFIRMED. The verifier side is unchanged, the claim cap can't admit an over-cap statement, and the ChunkTail grant stands with CT1–CT3

I reviewed it from the coordinator's `pr75-ea27aa86.bundle`. On the pure-block path, the PR's own commits (366e357e,
ea27aa86) touch only three files: `cuda/prove_chunk.cuh`, `pure_block.rs` and one line of `flock-pure-gpu.rs`.

**The verifier is unchanged.**
- Region list, Δ, the statement digest inputs, Publics bytes and parsing, and the verifier / replay code are all
  untouched.
- `tail_chain` went from `into_par_iter().flat_map_iter` to a sequential `flat_map` over the same 64-VU groups, in the
  same order, so it computes the same values. It feeds `c_in`, which the prover and replay use for publics. It is now
  precomputed by `prepare`, called in `main` before every command.
- Empirically, with my CPU build of ea27aa86:
  - ChunkTail(4) at K 2304 selftest: all_pass, 0 failures.
  - The L40S Chunk(8) session (art:86780ca6), recorded under e09c19a5, replays accepted, so the older layouts are
    byte-identical.

**The claim cap can't admit an over-cap statement.**
- `PureStmt::new` asserts 2 × regions ≤ `MAX_EXTRA_CLAIMS` = 64. That panics at statement build, before any session, on
  every path, verifier included.
- The CUDA side keeps its own bound: the Rust `link_cb` returns −1 when the claim points exceed `max`, and
  `prove_chunk.cuh` refuses `n_extra` < 0 or > `max_extra` (return 202) before touching `x_raw`. Nothing can overflow the
  buffer.
- The cap is prover-side capacity only. The verifier checks every region claim regardless, so going over the cap can only
  cost completeness, never soundness.
- The largest layout today has 9 regions (18 claims: ChunkTail with the epilogue).

**The two new unit tests pass on my build:** `region_claims_fit_the_gpu_prover` and
`tail_chain_from_rayon_workers_completes`.

**CT3 still holds:** `flock-pure-gpu` still builds ChunkTail witnesses on the host. `device` is false for tail layouts,
and only the GPU Ligerito prover runs on the device.
