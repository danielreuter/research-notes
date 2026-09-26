---
lane: flock-soundness
kind: handoff
from: flock-verifier
created: 2026-09-26T21:11Z
---

# The Lean verifier your theorems should be about: `Flock.verify` on branch cursor/flock-verifier-spec-7ab3 (PR #85), module map and conventions

The executable verifier of record is at `backends/flock/verifier/lean/` on branch `cursor/flock-verifier-spec-7ab3` (PR #85,
tip `1e75394b`). It is Lean 4.34.1 (pinned in `lean-toolchain`), has no dependencies, and forbids `native_decide`,
`implemented_by`, `extern` and `unsafe` (test `backends/flock/tests/test_lean_verifier.py`). The spec it implements is
`backends/flock/verifier/PROTOCOL.md`; §20 maps sections to modules. It accepts the honest circuit-statement session and
rejects R-BREAK. It also agrees with upstream on 23 re-digested proof mutants (`art:f1f3c2aa`).

**Proposal.** Put your theorems in a second library, `FlockSoundness`, in the same Lake project, importing `Flock`. Then
they are about exactly the definitions that run. I keep the executable definitions and their names stable. I will announce
every change to a definition below in a handoff before it lands. If a restatement would make a proof easier (`List`
instead of `Array`, a fold instead of a `for`, a `Vector n`), tell me and I will make the executable definition that shape.
Then you do not need a second copy with an equivalence proof.

**What to state soundness about** (all total; errors are `Except String`, `V := Except String`):

| definition | file | what it is |
|---|---|---|
| `verify : Setup → String → Array ByteArray → V Unit` | `Verify.lean` | the verdict: `.ok ()` is Accept. Record checks S1–S14, S8, S17, then `verifyRep` for rep 0 and 1, then S18 |
| `verifyRep` | `Verify.lean` | one rep: `decodeProof`, the PCS parameters, then in `TM` the four stages below, then S15 (every round consumed) and S16 (cap = root_B) |
| `Setup` | `Verify.lean` | the statement as the pipeline sees it: `m`, `kLog`, the digest, a `CircuitFold`, the extra claims at the link points |
| `bindAndZerocheck` | `Piop.lean` | §9: returns `ZcOut` (z, ρ, r_rest, v_a, v_b, v_c) |
| `lincheck` with `CircuitFold.fold α lw ρ_in` | `Piop.lean` | §10. `fold` must equal `α·A_0ᵀe + B_0ᵀe` for `e[s + 64u] = lw[s]·eq(ρ_in, u)`; that equation is the interface to the statement |
| `abcClaims` ++ the statement's extra claims | `Piop.lean`, `Statement.lean` | §11, §16.2 |
| `ringSwitch`, `basis` | `Opening.lean` | §12: the claim checks, T, and `b̂` |
| `ligerito`, `merkleCheck`, `positions` | `Ligerito.lean` | §13–§14 |
| `Transcript`, `TM := StateT Transcript V`, `squeeze` | `Transcript.lean` | §6. The only coin source is the record: `squeeze` returns `rounds[k].coins` after `SHA-256(pending) = rounds[k].sha`. The interactive soundness model is that each round's coins are uniform and independent of everything framed before them |
| `F128`, `F256`, `phi8`, `eqTable`, `lagrange` | `Field.lean`, `Piop.lean` | GF(2^128) in GHASH form (x^128 + x^7 + x^2 + x + 1), `inv 0 = 0`; K = F[u]/(u² + u + x⁻¹); `eqTable` is LSB first (index bit j ↔ r[j]) |

**Level-3 facts I will prove (my lane), which your level 4a can assume.** The field arithmetic is a field (`F128`,
`F256`). `merkleCheck` accepts only openings of the cap. The session binding (S13, S16, S18) forces both reps onto one
root. `Stmt.fold` equals the multilinear extension of `I ⊗ A_0 + Δ` for every pinned circuit, and each pinned circuit
is correct against its reference function (the lowering theorem).

**Opaque to proofs (setup only, not the PIOP):** `canon` is `partial` (canonical JSON, used only for the digest, Σ and
`Hello`). The hash internals (`Sha256.hash` padding, `Blake3.Hasher`) and `Circuit.parse` use `while`. Hashes enter the
soundness argument only as assumptions (§17.2: SHA-256 collision resistance for Merkle and the transcript binding).
Every stage of the PIOP and the opening uses bounded `for` loops only.

Known gaps you may meet: lookup slots are refused, so the SiLU cell is not covered yet. The legacy module (pure-block and IR
frame) is not written. PR #83 renamed its byte tags (`verity/flock-circuit`), and the verifier will take them as
statement parameters.
