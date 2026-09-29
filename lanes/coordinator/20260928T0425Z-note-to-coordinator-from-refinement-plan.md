---
cursor:
  subagentId: "bc-159ce83b-d3da-5f5d-921a-fae1057fcddd"
---

lane: coordinator · kind: note · from: refinement lane (bc-159ce83b) · to: the Project coordinator; cc research
coordinator (bc-8ece7cde) · created: 2026-09-28T04:25Z · repo: danielreuter/verity · about: the refinement plan,
`docs/refinement-plan.md`

# Refinement plan: the headline

- **Theorem:** if `Flock.verify` accepts a record and its two proofs, the compiled model's table run after the link
  points accepts, played with the proofs' messages and the record's coins.
  - That run is `tableAfter`, the piece `tableC` and `sessionB` are built from.
  - The theorem is pointwise, per run, through a new relation `Game.Plays` (a typed message tape and a coin tape).
- **By morning:**
  - seam theorems (R1, now [#209](https://github.com/danielreuter/verity/pull/209));
  - `Plays`, with the transcript toolkit and element seams (R2);
  - zerocheck and lincheck (R3, likely);
  - ring switching (R4, likely).

  That is about a quarter of the refinement.
- **Not by morning:**
  - Ligerito, about half the refinement, including the final check's batched basis;
  - the Merkle openings, and the assembly with the record's checks;
  - the statement decoding, which waits on #199 and #205;
  - salted `hm96` leaves, which need a model change;
  - the probabilistic transfer.

  **A full end-to-end machine-checked proof is not achievable by tomorrow morning.** The rest is two to three more nights
  of one lane.
- **No misalignment found** between the model and the executable in a step-by-step trace of every phase.
- **One proposal:** skip the computable-`Arith` differential test. It can't run the model's final check on real
  sessions, and R1 and R2 prove the seams it would test.
