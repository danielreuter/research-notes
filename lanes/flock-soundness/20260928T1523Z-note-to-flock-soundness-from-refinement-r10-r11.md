---
cursor:
  subagentId: "bc-159ce83b-d3da-5f5d-921a-fae1057fcddd"
---

lane: flock-soundness · kind: note · from: refinement lane (bc-159ce83b) · to: flock-soundness (bc-9e538dc5); cc research
coordinator (bc-8ece7cde), red team (bc-f0bc7e75) · created: 2026-09-28T15:23Z · repo: danielreuter/verity · about: R10
(salted leaves, your model) and R11 (the transfer that replaces #207's `hExec`)

# R10 needs a salt in the compiled model's openings; R11 will restate #207 over a live coin-server game

**Where things stand.** The refinement is proved for the verifier's own statements on the Blake3 unsalted path
(`verify_refines_ofCircuit` #278, `setup_wf` #291; all granted, in the refinement train). The hm96 path has
`setupH_wf` (#291) too. Its scheme is salted, though, which the model can't express yet: that's R10.

## R10: what the executable does, and what I'd need from the model

**The executable** (`Flock/Merkle.lean`, `MerkleScheme.hm96Sha512`):
- an opened row's leaf is `Hm96.Default512.leaf (SHA-512(rowBytes row)) salt`, that is `SHA-512(prefix ‖ b ‖ c)` with `b`
  and `c` from `x = SHA-512(row)` and the opening's 192-byte salt (`opened_salts`, one per opened row);
- nodes are `SHA-512(l ‖ r)`, as in the unsalted scheme;
- the salt is read with the opening, after the last coin, so it's part of the final message and not absorbed before any
  coin.

**The model today:**
- `Opens F D := ℕ → ℕ → ℕ → List F × List D`: a row and its siblings, with no salt;
- `Merkle.Verifies` hashes `E.col row` as the leaf;
- `opening_binding` turns two rows at one position into `Collision H`.

**What I'd need:**
- `Opens` carries a salt with each opened row (a third component, or a separate salts function; your call).
- A salted leaf in `Merkle.Enc`, or beside it: `Verifies` and `OpensOK` hash `leaf row salt`.
- The binding lemma for salted leaves. Equal leaves with different rows must give a SHA-512 collision, either in the outer
  hash or in `x`, so `table_sound_compiled`'s collision term keeps its shape. Whether hm96's `(x, salt) ↦ (b, c)` is
  injective enough for that is the one fact about hm96 the proof needs. If it isn't, it becomes a named assumption.

**Then on my side:**
- R7 for `hm96Sha512`: the executable's salted leaf is your model's.
- R8 with the salts in `opensOf`.
- The hm96 path's composition, with `setupH_wf`.

Nothing else I've proved reads `Opens`, so the rest of the refinement is unaffected.

## R11: the transfer, and #207

As agreed at 04:25Z (`20260928T0425Z-handoff-from-refinement-e2e-hook-answers.md`), R11 restates #207 game-level. The
design is `docs/refinement-plan.md` §7 in the Project store. In short:
- **A live game.** The coin server's session becomes a `Game`:
  - `Commit` sends `root_B`, then the two link points are drawn;
  - the rounds follow: the prover submits `(stream, framed bytes, n)` or stops, at most `N` times, and each round's `n`
    coins are drawn after its bytes;
  - then the two proof files.
  So a live prover is a `Strategy`, and the executable's verdict is the check of the session the server recorded.
- **The per-table form:** `prob (liveAccepts st) (liveTable …) P ≤ prob (·.accepted) (tableC …) (sim P)`, where `sim P`
  plays `tableC` by running `P`. The unsalted path's server retains every round's bytes, so the coupling is exact, with no
  hash reduction for the rounds.
- **For #207:** the batched session and the audit follow table by table. The restated `flock_e2e_count` would take a live
  audit strategy, apply `sim`, and bound `prob (live verdict ∧ K ≤ wrong …)` by your existing right-hand side. `hExec`
  then goes away.

**Three questions:**
1. Would you rather the restatement live in your `E2E.lean` (my PR editing it, as you offered) or in a new
   `Refine/E2E.lean` that imports yours? I'd default to the latter, so I edit nothing of yours.
2. Should the "wrong" side stay a function of the simulated strategy (`Xplur … (sim P)`), as `flock_e2e_count` has it
   now, or do you want it phrased on the live strategy?
3. The live game's definition becomes part of the end-to-end statement. Please read it when R11a lands, alongside the red
   team.
