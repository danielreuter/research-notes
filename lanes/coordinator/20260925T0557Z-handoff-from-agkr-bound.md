---
lane: coordinator
kind: handoff
from: agkr-bound
created: 2026-09-25T05:57Z
---

# agkr-bound revised estimate v2 (non-algebraic commitment, your 0546Z): recommend a verifier-checked IRS/SHA-256 commitment; needs a core-scheme decision

This supersedes the design part of 0540Z and 0550Z, which assumed Poseidon2.

## Which design, and why

**In-circuit SHA-256 or BLAKE3: not realistic for A-GKR.**

- The operands are about 25 MB per 4096 VUs, which is about 393k BLAKE3 compressions (or SHA-256 blocks).
- Each is about 56 G-functions (BLAKE3) or 64 rounds (SHA-256) of 32-bit add/xor/rotate. In A-GKR's depth-1, lookup-based
  style that is about 2.5k committed limbs and about 900 byte-XOR lookups per compression, per unit.
- For comparison, BF16 today has 264 columns and 86 queries per unit. The cost would be about 10× BLAKE3 and about 25×
  SHA-256 in witness and LogUp.
- Every layer also spans all wires (0550Z), so t.total grows about 10–30×.
- It would need days of gadget work: carries, rotations, the chunk and tree modes.

**Recommended: the commitment is checked by the verifier outside the circuit and bound to the proof's committed columns.**
This is exact, not a spot check. A plain one-word-per-leaf Merkle root (today's `verity.commitments.merkle`) **cannot** be
bound this way without the verifier reading every word: any linear check needs all the words, and spot-opening leaves only
catches a changed word with probability s/N. The committed object needs distance.

- **Scheme.** C_x is the SHA-256 Merkle root, with `verity.commitments` leaf/node framing and a new schema such as
  `irs-babybear-sha256/col/v1`, over the n = 4k columns of RS(M_x):
  - M_x is the frozen x words (VU-major, flat) laid out as an m × k matrix: k = 4096, m = 1536 for BF16.
  - Each row is Reed–Solomon encoded at rate 1/4 over BabyBear. This is the same code A-GKR's Ligero already uses.
  - Likewise for C_W, and for C_y if y must be private. Otherwise y stays public with a `merkle` root checked outside, as in
    B-Ligero.
  - It is non-algebraic (SHA-256); only the code is algebraic.
- **Binding.** The transcript absorbs C_x and C_W before the GKR challenges. Then:
  1. Draw σ ∈ BabyBear^6.
  2. The prover sends u = Σ_a σ^(k·a) · M_x[a, :], a vector of k extension elements, about 98 KB.
  3. The verifier opens t = 192 columns of RS(M_x) with SHA-256 paths and checks RS(u)[j] = Σ_a σ^(k·a) · col_j[a]. This is
     the Ligero linear test.
  4. The A-GKR functional gains Σ_flat σ^flat · X[word flat] = Σ_c σ^c · u_c.
  - Because flat = 1536·v + 16·i + j′, the coefficient is (σ^16)^unit · σ^j′. That is exactly the rank-1 unit × column shape
    of the operand binding I have already implemented (`prover.add_bind`, `verify.rs` `bind_u`). Only the coefficients and
    the source of b change: b comes from u, not from x.bin.
  - The verifier never sees an operand word.
- **Cost.**
  - Prover: one m × k extension-field matvec per operand, plus gathering t columns and their paths from the committer's
    cached tree. I estimate +1–5% t.total.
  - Verifier: one NTT of length 16384 over the extension field (the Rust verifier has `ntt.rs`), plus about 192 × 1536
    words and paths per commitment. I estimate +0.1–0.3 s.
  - The committer (RS encode plus a SHA-256 tree over 16384 leaves of about 6 KB) runs once per frozen set, outside the
    proof.
- **Soundness.** It adds one IRS proximity term per commitment, the same form and parameters as A-GKR's own Ligero term
  (2^-130.19 at t = 192). The powers-of-σ combination adds about m·n/|F| ≈ 2^-161 (correlated agreement for curves).
  - With x and W: 3 × 2^-130.19 ≈ 2^-128.6. With x, W and y: 2^-128.2. Both stay at or above 2^-128. Alternatively,
    t = 200 for the input openings gives margin.
  - The computational side is SHA-256 collision resistance. It gets a named term, not a new assumption class.
- **Variant.** The core commitment could instead be one of A-GKR's own Ligero matrices: the operand columns committed as a
  separate matrix whose root is C_x. The binding would then be automatic, but it is more invasive in `ligero.py` and ties
  the core scheme to one backend's layout.

## Decisions needed (not mine to make)

1. **A new core commitment scheme** in `packages/verity` `verity.commitments`: the IRS-encoded SHA-256 column Merkle above.
   The existing SHA-256 schemes (one word per leaf; `leaf/v1` tensor leaves) cannot be bound exactly without the verifier
   reading the operands.
   - This touches every backend's "same full relation". B-Ligero would bind it with its own Ligero linear test, which is
     cheap. SP1 would have to recompute RS plus SHA-256 in-guest, which is expensive.
   - The alternative is "in-proof SHA-256/BLAKE3 hashing" at 10–30× for A-GKR.
2. **Scope and time.**
   - Implementation: the scheme's reference code in core (standard library only, slow but correct), the vectorized
     committer, prover and Python verifier changes, a Rust verifier with SHA-256 paths, RS(u) and b, soundness, pins and
     negatives. About 4–6 agent-hours.
   - Measurement is cheap because the overhead is small: about 0.5 h and $0.5–2 per SKU including bootstrap.
   - Cost: about $5–7 on an A100 (or about $3 on a 4090) plus about $5 for rows. That fits the remaining ~$12.8, but not the
     12:00Z FINAL for five rows. A100 BF16 plus one FP8 row by 12:00Z is possible but not safe.
   - Options:
     - **(a)** approve the scheme, and extend FINAL by about 3 h for five rows;
     - **(b)** approve the scheme, and do development plus A100 BF16 (plus FP8 if time allows) by 12:00Z;
     - **(c)** park.

Still `blocked`, polling about every 10 minutes. There is no pod. If you answer (a) or (b), I start on a 4090 or A100 at once.
