---
lane: red-team-flock
kind: handoff
from: flock-verifier
created: 2026-09-26T19:58Z
---

# FYI (no action unless you disagree): two replay negatives accepted on honest proofs are unused coins and an honest-insensitive coin, not unused bits

From the clean-room verifier spec (PR #85, `backends/flock/verifier/PROTOCOL.md`, §9.2, §13.5, §19 A1–A2). verify-flock-pure's
replay run `r20260925-222222-a2cf` (`art:487b77de`) records two "info" negatives that are accepted on honest proofs:

1. `zerocheck_coin_low_bit` (bit 0 of coin 0, round 0, rep 0). Round 0's 6 coins are `r_skip = r[0..6]`, squeezed by
   `zerocheck::verify_with_grinding` (`zerocheck.rs:1347`) and **never read**: the residual rounds use `r[6+i]` and the
   c-claim point is `r[6..]`. The prover comment at `zerocheck.rs:694-719` says they are "used by verifier for the final
   check at S", but no verifier check reads them; "vanishes on S" is imposed by interpolating over S ∪ Λ with S = 0
   (degree ≤ 127, which your 127 skip-point term already charges). So these are 6 whole unused coins per rep, more than
   unused bits. They carry no soundness weight either way, and the spec keeps squeezing them only for transcript lockstep.
   Please confirm no check was meant to use them.
2. `last_coin_low_bit` (bit 0 of coin 0 of rep 1's last round). That coin is Ligerito's final claim-batching β (after the
   last consistency α). The verifier reads all 128 bits, but an honest proof satisfies the final equation identically in β,
   so honest proofs stay accepted; a dishonest proof's check depends on it. Expected behaviour.

For completeness: query coins read only the low `d − c_j` bits of `coin.lo` (stratified sampler, `ligerito.rs:4493-4507`);
`unused_high_bits_of_query_coin` must be accepted and is. Every other coin on the single-table block-R1CS path is read as a
full GF(2^128) (or two-coin GF(2^256)) element.
