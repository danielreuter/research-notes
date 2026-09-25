---
lane: coordinator
kind: handoff
from: red-team-flock
created: 2026-09-25T21:20Z
---

# red-team-flock: verity/flock-pure-block/v2 (bf16-hopper) is GRANTED WITH CONDITIONS at NON_ZK_PROOF. The whole-proof bound is 2^-195.4 per 8,192-VU proof, and 2^-193.4 over a 32,768-VU batch of 4 sub-batches. I labelled the H100 plateau result art:ca6029c1. Route (a) is resumed next.

Report: `lanes/red-team-flock/20260925T1107Z-report-red-team-flock.md`, section "flock-pure-block/v2". My rerun of the
producer's CPU selftest at d3e96304 passed 18/18 at 8 and 64 VUs (run r20260925-210925-a744, art:ac1aeeeb). Pods
terminated at 21:14Z; about $0.15.

## What I checked
- **Statement (pure_block.rs @ d3e96304): HOLDS.**
  - One block per (VU, chunk) holds 32 keyed-BLAKE3 compressions (16 each for x and W) and the 32 pinned units.
  - Δ copy rows cover the chaining, the block_len/flags constants (KEYED_HASH, START, END), the unit operand bits
    (the message bits, in the right half and slot) and the in-chunk accumulator chain. XOR toggling on the input rows
    is correct. Empty rows force zero. The statement digest covers Δ, the netlist sha and the layout.
  - The six public regions (key, counter, CV, AccIn, AccOut, Y) sit on the right in-block bits.
  - Each region is opened at two OS points drawn after Commit, in both reps. The points are live and fixed before any
    Flock coin (the E0 and R5 gate is in this lib).
  - Commit publics are checked natively before the points: the chunk CVs through keyed parents to the verifier's own
    row digests. AccIn(v,0) = 0, and AccOut(v,c) = AccIn(v,c+1) is one committed word. Y at c = 2 equals the verifier's
    own output word.
  - Dummy blocks are pinned to zero key, counter and CV and to the dummy unit's outputs.
- **Lowering flock-unit-io/v1: HOLDS.**
  - The regenerated netlist matches PINS da1bbe2c.
  - All 7,681 rows are topological: no forward references, 33 assertion rows. So the witness is unique given the
    inputs.
  - My differential test ran 400 random units against `verity.ml.tc` (tc_dot and f32_to_bf16), including subnormals,
    zeros, large and small exponents and extreme accumulators: 0 mismatches.
  - The producer's own self_check samples only exponents 96–159, and should be widened.
- **R1–R8, F2, F3: HOLD** (the same lib as flock-link, with E0). The prover-only commit e8eedd80 (the device-side
  witness) doesn't touch the verifier path.
- **Bound:** Fast100 × 2 at m = 35 gives 2^-97.72 per rep and **2^-195.44** per proof. The region claims add about
  2^-243 (Schwartz–Zippel over two points). The batch is a union over its sub-batches.

## Conditions
- **PB1:** a result counts only if it names the verifier source commit and binary sha, and its statement digest and
  verifier path equal d3e96304's (code-identical is fine). art:ca6029c1 has `software.backend.commit: "unknown"`.
- **PB2:** the security block reports the union over sub-batches: at N_subbatches = 4 that is 2^-193.44, not the
  per-proof 2^-195.5.
- **PB3:** the non-producer replay (verify-flock-pure) labels `verified`. The verifier pod is producer-operated.
- **PB4:** evidence records carry `link_mode` exchange, `require_link` true, and the cell's Σ per sub-batch, from a
  verifier serving its own regenerated instance files.
- **Dependency (Daniel's hash convention):** Flock-CUDA's Merkle trees are SHA-256. Counted at q²/2^256 = 2^-128, the
  bound lands at about 2^-128 and just misses 2^-128. At the current convention it's 2^-193.4.

Labels written on art:ca6029c1: `proof_class=NON_ZK_PROOF` and a `finding` (conditions), both by red-team-flock with
`--ref` pointing to this handoff. Later results on the same statement (such as the 65,536-VU sweep) need the same
label, once PB1 holds for them.
