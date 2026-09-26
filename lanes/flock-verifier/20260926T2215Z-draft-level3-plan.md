---
id: 20260926T2215Z-draft-level3-plan
campaign: flock-verifier
lane: flock-verifier
kind: draft
status: open
repo: danielreuter/verity (PR #85, branch cursor/flock-verifier-spec-7ab3)
origin: flock-verifier
---

# Level 3 of the Flock verifier of record, in a16z's assurance stages (plan)

This plan follows the security stages of Thaler, "The path to secure and efficient zkVMs" (a16z, 2025). Stage 1 is the
protocol, stage 2 the verifier implementation, stage 3 the prover. The soundness lane (level 4a) adopts the same stages
(Daniel, 2026-09-26). `PROTOCOL.md` §17.4 is the maintained table; this note is the working plan behind it.

## Where each stage sits

| stage | claim for the Flock verifier of record | owner |
|---|---|---|
| 1a PIOP | zerocheck (univariate skip), lincheck (verifier-computed fold), ring switching and the region claims are a sound PIOP for F2 block R1CS | flock-soundness |
| 1b PCS | Ligerito binding and proximity (the paper's results as named axioms); **Merkle binding** | flock-soundness; Merkle is mine |
| 1c Fiat–Shamir | not used, since coins are interactive. Its slot is **session binding** | mine |
| 1d constraints = semantics | **lowering** (every pinned circuit computes its reference function, and is total) and **assembly** (fold, regions, Δ) | mine |
| 1e glue | `verify` accepts ⇒ outputs = f(inputs) and rows hash to the public roots, except with probability δ; no ZK claim | flock-soundness, from my lemmas |
| 2 implementation | the executable is the definition, so no second implementation has to be matched. **Field arithmetic**, decoders, hash code, runtime trust | mine |
| 3 prover | out of scope (upstream's prover); honest-session acceptance is tested | — |

The recursion caveat, adapted: a stage counts as complete for a statement only when every constraint system in its block
is covered. That means the row leaf's compression circuit, every expanded circuit (unit, tail stages) and every lookup
circuit.

## Work items (theorem shapes; names are proposals)

- **L3-F, field (stage 2).** `F128` with `+`, `*`, `inv` is GF(2)[x]/(x^128 + x^7 + x^2 + x + 1). That means the
  carry-less multiply, reduction and Karatsuba equal polynomial multiplication mod g, and `a * inv a = 1` for `a ≠ 0`. Then
  `F256` is GF(2^128)[u]/(u² + u + x⁻¹), and `phi8` is a ring embedding of GF(2^8). This is small, has no data, and comes
  first.
- **L3-M, Merkle (stage 1b).** For any `MerkleScheme` (SHA-256 or SHA-512, with the node and leaf as given), two accepted
  openings of one position with different rows yield an explicit collision of the scheme's hash, by an extractor that is a
  Lean function. The proof is by induction on the path and needs no random oracle. The HM96 leaf's binding (PR #88 §4) is
  the same shape, one level down.
- **L3-S, session binding (stage 1c's slot).**
  - (a) R2: in an accepted run, every squeeze returned round k's coins only after the framed bytes equalled the retained
    bytes, or hashed to the recorded digest when bytes are not retained. So the prover's messages before coin k are
    determined by the record, unconditionally with retained bytes and up to a SHA-256 collision without them.
  - (b) R1: S13, S16 and S18 imply both reps' caps equal `root_B`.
  - (c) The statement digest, cap and link points precede every Flock coin (Z1, §9.1, S14).
  - These are mostly definitional.
- **L3-A, assembly (stage 1d).**
  - `Stmt.fold α lw ρ` equals the naive `α·Aᵀe + Bᵀe` for A, B the placed slot matrices plus Δ. This is the tensor
    factorisation lemma.
  - `regionValue` equals the multilinear extension of the region's known bits at its point.
  - Every Δ pair enforces the copy it names on a satisfying witness ("both" gives `z_i = z_src`; "A only" with the pin at 1
    gives the same).
- **L3-L, lowering (stage 1d, the long pole).**
  - For each pinned circuit P with reference f: every satisfying witness has outputs f(inputs) (soundness), and a witness
    exists for every input (totality).
  - Method: a certified checker, proved over all circuits in the kernel, run by the verifier on its pinned files at setup.
    A circuit it cannot certify is refused. So no proof evaluates a pinned file in the kernel, and no proof uses
    `native_decide`.
  - Per circuit kind:
    - **Lookup slots.** The two-level one-hot circuit has one generic proof over any table; the table is pinned by its
      SHA-256.
    - **Expanded circuits** (units, tail stages from `verity_flock.ir_lower`, our code). A Lean port of the lowering is
      proved correct per IR op. The setup check requires the pinned circuit to equal the port's output (translation
      validation by recompilation).
    - **Row-leaf compression circuits.** The target leaf is HM96 on SHA-512 (Daniel: SHA-512 on every commitment path), so
      the SHA-512 compression circuit is the one that matters. Proposal: the verifier's own generator, proved against
      FIPS 180-4, produces it. It is published as the pinned file the prover loads, so no reverse-engineering of upstream's
      builder is needed. Today's BLAKE3 circuit (upstream data, 44M nonzeros) gets translation validation only if it
      survives the re-baseline.

## Order

1. L3-F and L3-M: small and self-contained. L3-M is parametric in the hash now that the scheme is a parameter.
2. L3-S: definitional.
3. L3-A: the fold and region lemmas.
4. L3-L: lookups, then the IR lowering port, then the SHA-512 compression generator. This depends on PR #83 and PR #88
   publishing the target leaf and circuit formats.

## Tooling decision

The executable stays dependency-free: that is the running binary's trust surface, and `test_lean_verifier.py` enforces it.
Proofs go in a second Lake package, `backends/flock/verifier/lean-proofs/`. It requires Mathlib at a pinned revision
(polynomials over ZMod 2, finite fields, probability for 4a) and the executable by path. So the theorems import the very
definitions that run. I am proposing this to flock-soundness in a handoff.
