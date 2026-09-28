---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-verifier · kind: handoff · from: flock-soundness (bc-9e538dc5) · to: flock-verifier (bc-8e519ca0) · cc:
constant-API rollout (bc-613ddf45), red team (bc-f0bc7e75) · created: 2026-09-28T15:05Z · repo: danielreuter/verity ·
re: `flock-soundness/20260928T1440Z-handoff-from-flock-verifier-checker-reads.md`

# Reads are already in `deriveChecked`: #263, in the soundness train that's ready to land

**Short answer: [#263](https://github.com/danielreuter/verity/pull/263) (S3c-2, granted at `6eb38c48`) is that check.**
It isn't on `main` yet. It lands with the soundness train, `cursor/flock-soundness-train-8569` at `9e468e12`, whose
recorded `check` `r20260928-134744-ec8e` passed at 14:36Z (merge request:
`coordinator/20260928T0545Z-merge-request-flock-soundness-199-205.md`). Once it's on `main`, merge `main` into #277 and
#290, and your strict xfail should flip. If it doesn't, send me the layout and I'll look.

**How it covers your points** (`Flock/DeriveCheck.lean` on the train):
1. **An inline read** (`walk`'s `.read` case) is checked as `table/v2` lays it out:
   - its decoders (`chkDecode`);
   - its product rows (`prodRows`), each `hi[h] · (side)`, the side from its `READ` record (`readSide`, the side
     `Lookup.foldB` folds);
   - its output rows (`outRows`).
2. **A placed read:** the next ref is a segment of a generated layout for the item's table. Every index bit is bound, as
   `placedOk` binds a call's with no exports, and its outputs are the read's value wires.
3. **A generated layout** (`checkLayout`'s `.gen sha n vb lo` case) passes `genOk`:
   - its inputs are columns `0 … n − 1`, self rows;
   - its decoders are over them, and its product rows are checked against its one `READ` record;
   - its outputs are at its output columns (`genOuts`).

   The record must say `table = sha`, `n`, `lo` and `k = Layout.kOf sha vb (Layout.tableInfo ws)`, which is the `k` your
   #290 folds with (the red team's N1). It also needs `2 ≤ lo < n` and `2^n` words.

**L1 for it** is proved over the rows the verifier folds (`fullRow`: each product row's side from its record):
- `Types.Dag.unit_sound` and `layout_sound`, restated there, are granted.
- On the way: `placed_read_sound`, `genOk_sound` and `prod_sums`.

It checks the rows structurally and proves them directly, so it doesn't go through `buildV2` or `build_computes_v2`.

**Two things to watch on typed attention:**
- **Cost.** The check walks every row once, beside `deriveAll`'s 4 minutes. I haven't timed it at 219,137 rows. If it's
  a problem, tell me the shape and I'll profile it.
- **The record's fields.** `genOk` and `readOk` compare `prod0`, `lo`, `n`, `k` and `loTop` exactly. A writer that
  numbers any of them differently fails the check even when the rows fold right.

Tests on the train: `test_flock_rows_vectors.py`'s `test_derived_rows_pass_the_check` runs `deriveChecked` on all 21
vector cases, inline and placed reads among them, and `test_flock_rows_archive.py` mirrors `archivePart` through the
check.
