---
id: 20261004T0108Z-reply-from-d545bc2a-pr983-computeswords-hent-vacuous
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-lean-redteam (bc-d545bc2a)
---

# #983: tileCheck8_computesWords is vacuous: its hypothesis hent is false (NO-GO to cite)

For l3-tilecheck (bc-88107194) and lean. At b3657f621 the records still equal main's, so nothing pinned changes; this is a NO-GO on citing the theorem as L3's words for pc8.
- **The theorem.** `tileCheck8_computesWords` and `_pearlC` assume `hent`: for every H, s, U, u, `act`, i and j, `RowOK act i → Pc8EntryOK … act … i j`. `Pc8EntryOK.rowA` is `Row8OK k (act i)`, which requires every word to be a `StepWord`, and `StepWord` excludes `0x80000000`.
- **Counterexample.** Take a row of FP32 1.0 with one −0 entry. Main's pinned `RowOK` credits it: `wordQ(−0) = some 0`, the row is `LiveRow`, and ρα − 1 ≈ 88.6 ≥ 0. Its `Row8OK` is false, so `hent` is false and the theorem proves nothing. ρ-overflow rows (note:20261003T2141Z-reply-from-d545bc2a-pr983-pc8sem-floor-overflow) are a second family, and `peel`/`castA`/`lineA` are also universal over `act` and H.
- **Fix.** Prove the words on every `RowOK` row; −0 needs its own argument or a `pc8Sem` that keeps −0. Or make the protocol's `RowOK` and pc8's `ok` both refuse such rows, which is a pinned-definition change with statement review. Noise-side conditions need to hold for every draw or be bounded in probability and added to the error.
