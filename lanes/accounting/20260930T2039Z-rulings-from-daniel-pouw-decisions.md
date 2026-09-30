---
id: 20260930T2039Z-rulings-from-daniel-pouw-decisions
campaign: pouw
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd), recording Daniel's rulings of 20260930T2036Z (relayed by verity-top)
---

# Daniel's PoUW rulings (1:36 PM PDT, 30 Sep): drand quicknet is the beacon, `-h2` goes on the served path, and registered weights use the keyed 8-block rotation

Daniel approved compute-accounting's three recommendations ("Compute accounting's items all look good"). They are no longer open.

1. **Beacon: drand quicknet.** This is the League of Entropy's threshold BLS on BLS12-381, unchained, with 3 s rounds.
   - It keys the salt and Pearl-C's audit draw. The draw uses a later round than the one the commitment follows, as
     `pearl_c_work.draw` already requires.
   - Its trust is that fewer than t of the group's n operators collude, and that BLS signatures are secure.
   - `beacon-unpredictability` moves off C: the assessor rates it A or B for the named beacon (`docs/pouw/assumptions.md`,
     the beacon table).
2. **`-h2` on the served path: yes.**
   - #596 (`-h2` on the served graph path) proceeds, and so does #572 (the `-h2` switch in the sm_120 pipeline).
   - It is rated A, and served prefill goes from 1.68× to 1.62×.
3. **Registered weights: the keyed 8-block rotation (rung 3).**
   - It applies to FP8 v1 and v2 now, and to Pearl-C4 once #580 enforces the F1′ fix.
   - The curated list stays as the fallback (`docs/pouw/approved-weights.md` §4).

**Still open: per-row seeds (`-h3`).** They wait on M3's (RowSeed's) statement review, and on whether its per-row draw condition is
a named assumption.

The sources are the old store's `docs/pouw/assumptions.md`, `hashing-accounting.md` and `approved-weights.md`, in
`art:8bd64630bc06c23d5095996d2f198ce4bd557413722ad94bd3ca3c1a949e42e9`.
