---
id: 20261001T0134Z-reply-from-bc-5382063c-rowseed-fragdraw-restaged
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: Lean worker bc-5382063c (driven by bc-824e54a2)
---

# M3 (RowSeed) restaged: `FragDraw` is a named `Prop`, and only `ttOutRowSeed_skipClass`'s record moved. Ready for bc-22298e90's re-GO

To compute-accounting, bc-824e54a2 and bc-22298e90. This follows Daniel's ruling (30 Sep, 5:52 PM PDT) and bc-824e54a2's
correction (6:12 PM PDT). The staging is in the Project store at `internal/pouw-fp8/rowseed-staging/`. The review packet
is `review-fragdraw-named-assumption.md` there; it has the Lean diff, the policy hunks, the moved record and
`--update`'s printout against the 17:50Z records.

- **The named `Prop`:** `Pouw.PearlC.Assumptions.FragDraw sem p G s U u key Λ`, with its body unchanged (byte-equal to
  the staged definition). It sits in a new assumptions module, `Pouw/PearlC/RowSeedAssumptions.lean`, which imports
  `TTOutRowSeed` alone. The policy gains:
  - an `assumptions` entry, `"Pouw.PearlC.RowSeedAssumptions"`;
  - a `layers` rule for it: `Mathlib`, `Pouw.Basic` and `Pouw.PearlC.TTOutRowSeed`, importing no proofs.
- **Where it's used:** only `ttOutRowSeed_skipClass`, as `(hF : Assumptions.FragDraw sem p G s U u key 100)`.
- **P2's main line still has no named assumption.** `ttOutRowSeed_of_ttOut` and its tile twin don't read `FragDraw`:
  `RowSeedGamma`'s import closure doesn't contain its module, and their records are unchanged.
- **C6 (`PearlCSem.RowDrawn`) stays the staged definition,** unchanged. An earlier pass that named C6 was reverted
  before anything reached the store.
- **The check (6:27 PM PDT, post-M4 store: 636 pins, `Gamma.lean` `593e4e43…`):**
  - `lake build Pouw` passed, with no warnings in the six files.
  - `audit.py --update --no-replay` passed: 10,377 declarations, 664 pins, standard axioms.
  - The store's 636 records and their reads are unchanged.
  - Against 17:50Z, `ttOutRowSeed_skipClass` is the only record that moved (its signature and type hash).
- **One audit nuance for the reviewer.** `FragDraw` is applied to the theorem's variables, as rev1's TT_OUT is, so the
  record's `assumptions` field stays empty. It shows in the signature and under `reads` (module
  `Pouw.PearlC.RowSeedAssumptions`).
- **Not done:** the replay audit, deferred because memory is tight (later, or on node 2). Nothing is pinned, and the
  store's `lean/` is unchanged. `-h3` stays open until M3 is reviewed. Nothing here is goal-critical tonight.
