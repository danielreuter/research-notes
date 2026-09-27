---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: finding · status: adopted (Daniel, 2026-09-26) · repo: danielreuter/verity · branch `cursor/flock-soundness-8569` · PR #89

# Why Flock's Merkle trees move to SHA-512 (decision-time analysis)

Decision-time material behind `backends/flock/verifier/lean/soundness/DESIGN.md` §1 (why SHA-512; the hash-width
analysis). The compiled theorem stated for the adopted design is `ASSUMPTIONS.md` §1.2, derived in `DESIGN.md` §2.
(Section numbers were renumbered on 2026-09-26, when `ASSUMPTIONS.md` was split into it and `DESIGN.md`.)

## The three bounds with SHA-256 trees (Daniel's question: does collision resistance clear 2^-128?)

`t` is the number of SHA-256 evaluations the adversary makes. The statistical term is
`ε_stat = tableError ≤ 2^-195.5`.

| Model | Covers | Bound | Clears 2^-128? |
|---|---|---|---|
| Collision resistance, straight-line reduction | Provers that know the tables they commit to: each commitment is the Merkle cap of a table the prover holds | `ε_stat + Adv_CR(B)`, with `B` one run of the prover plus a comparison of the opened columns with the tables. With the generic bound `Adv_CR ≤ t²/2^256`, this is `2^-195.5 + t²·2^-256`. | **Yes**, for `t` up to about 2^64 hash evaluations. The statistical margin is untouched. |
| Collision resistance, rewinding (the only known argument for arbitrary provers) | Every prover | Run the prover twice from the same commitment to extract a consistent table. This gives `Pr[inconsistent opening] ≤ √(N·Q·Adv_CR)` per committed level (`N` = codeword length, `Q` = queries). At level 0 for m = 33, `N·Q = 2^28.8`. So the bound is `t·2^-113.6` even with the most optimistic `Adv_CR ≤ t²/2^256`. | **No**, for every `t ≥ 1`. The square root sits on the hash term, where the 67.5-bit statistical margin cannot absorb it. |
| Random-oracle model (VCVio's Merkle extraction) | Every prover | `ε_stat + t²/2^257 + t·(cap entries)/2^256` | **Yes**, for `t` up to about 2^63.5 |

The SHA-256 round digests had a tight collision-resistance bound for every prover: the reduction includes the coin
server, which sees the live bytes, so a mismatch with an equal digest is itself a collision. The adopted design
removes them: the server keeps the round bytes.

At `t ≥ 2^65`, SHA-256 misses 2^-128 in every model, the random-oracle model included, so Daniel's range of 2^80–2^100
needs wider hashes whichever model is chosen. The project's convention agrees:
`verity_numerical.security.accounting.hash_collision_bound` charges `q²/2^h` at `q = 2^64`, and A-GKR moved its Merkle
tree to SHA-512 for this reason (`backends/gkr/gpu/sha512_cuda.py`).

## What the alternatives give

- **More repetitions:** no help. Every rep opens the shared level-0 table, adding about 0.4 bit per extra rep to the
  rewinding term.
- **Rewinding more than twice:** a k-run reduction finds more collisions but runs k times longer. Under the generic
  bound the gain cancels.
- **Tight standard-model extraction** needs other primitives: somewhere-statistically-binding or somewhere-extractable
  hashes, built from LWE or DDH. They are impractical at this scale.
- **Sending the verifier the committed tables** makes binding information-theoretic, but costs about 2.3 GiB per table
  at m = 33, twice the witness, so the proof is no longer succinct.
- **SHA-384 trees** clear 2^-128 by rewinding only up to `t ≈ 2^47`–`2^53` (m = 35 to 22).

## Cost of SHA-512 against SHA-256 in Flock

Flock's in-proof Merkle trees are computed and checked natively, not in a circuit.

- **Prover.**
  - The level-0 tree at m = 33 hashes about 2.1 GiB per table: 2^21 columns of 1 KiB, plus nodes.
  - On NVIDIA GPUs SHA-512 costs about 1.5× SHA-256 per byte, since 64-bit arithmetic is emulated. hashcat on an
    RTX 4090 does about 22 G SHA-256 compressions/s against 7.5 G SHA-512 compressions/s, and a SHA-512 compression
    covers twice the bytes.
  - That is a few milliseconds more per table, well under 2% of a 0.5–1 s GPU proof.
  - On CPUs, where SHA-256 has SHA-NI and SHA-512 usually has no instructions, it is about 2× per byte, so the Merkle
    share of a CPU proof roughly doubles.
- **Proof size.** 64-byte siblings double the hash part, about 36% of a proof: 6,126 hashes in the m = 32 example of
  spec §8.3. Proofs grow from about 544 KB to about 740 KB per rep.
- **Verifier.** Lean has no hash instructions either way. A SHA-512 compression costs about 1.25× a SHA-256 one and
  covers twice the bytes, so hashing time stays about the same (a few ms).
- **In-circuit.** This applies only if Merkle checks were ever verified inside a circuit (recursion, for a SNARK
  variant), or to the statement's own data hashes.
  - Per compression (Bristol Fashion): 22,573 against 57,947 AND gates, 2.6× per compression and 1.3× per input byte.
  - In Flock's power-of-two slots: 2^15 against 2^16 rows per compression, the same rows per input byte. Per
    Merkle node (two compressions each) that is twice the rows.

## Consequences of the decision outside this lane

- PROTOCOL.md (PR #85, lane `flock-verifier`) specifies SHA-256 trees (§14) and round digests (§6), following
  upstream. Both change: SHA-512 leaves and nodes (64-byte digests and siblings), and the coin server keeping each
  round's bytes, which the replay compares.
- Upstream's Rust verifier, used as the CI cross-validation, and the provers (Rust and CUDA) need the same tree hash.
- The statement's own data commitments (frame-v3 roots, row digests, Halevi–Micali leaves hashed in the circuit) are
  tight collision-resistance terms. At `t ≥ 2^65` they too need a hash of at least 288 bits. That is a
  commitment-scheme decision, separate from the verifier's.
