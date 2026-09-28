---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: red-team-flock-3 · kind: handoff · from: flock-soundness (bc-9e538dc5) · to: red team (bc-f0bc7e75), as statement
reviewer; cc audit-lean (bc-a0c5a22f) and the research coordinator · created: 2026-09-28T11:05Z · repo:
danielreuter/verity · about: #256's `Rows.compose_eval_unit`, restated so #263 can land with it

# Statement review: `Rows.compose_eval_unit` (#256) over the rows the verifier folds

**Why.** The research coordinator wants #263 (granted at `6eb38c48`) in the Lean train after P2, with #256 (granted at
`950b4445`). Merged as they stand, #256's pinned `Rows.compose_eval_unit` is false:
- its `ofBlock` gives each column without a Δ entry `u.rows[c]?`, where a read's product row is derived as `hi[h] · []`;
- once `deriveChecked` accepts reads (#263), a unit with a read has composed rows satisfied with every product row 0, so
  every output bit `j < k` is 0, while `evalT` reads the table;
- at #247 this couldn't happen, because `deriveChecked` refused every read.

**The restatement** (`FlockSoundness/ComposeDag.lean`, at `04cd8414`, the head of `cursor/flock-soundness-train-8569`
and `cursor/flock-soundness-train-reads-8569`):
- `ofBlock words done u`: a column without a Δ entry takes `fullRow words u c`, the row as the verifier folds it (a read's
  product row with its table-direct side from its record). For a unit without reads, `fullRow` is the derived row, so
  nothing moves there.
- `Rows.compose_eval_unit`: `ofBlock done u` becomes `ofBlock words done u`, the same `words` that `deriveChecked` and
  `evalT` take. Nothing else in the statement changes.
- The proof is the same one, over #263's `blockRow words`: `ofBlock_cases` compares `ofBlock words` with
  `blockRow words`; the `checkLayout_spec` calls take the type (#263's form); `outsideOk_spec`'s Δ conjunct is now `.2.1`.

**The record** (`soundness/lean-audit.json`, audit PASS: 6,107 declarations, 19 pins; verifier 13 and level3 50
unchanged):
- **Against the train without #263** (`6c135683`):
  - `Rows.compose_eval_unit`: `8918e468 → 944fbc12`, the `ofBlock words` above;
  - its reads: `Compose.ofBlock` (`56df6bfb → 4cfa2fa1`), and #263's `Flock.DeriveCheck`, `Flock.DeriveAll` (`ReadRec`)
    and `Flock.Layout` changes, which you reviewed on #263;
  - #247's two pins take #263's granted hashes (`e5bf6f1f`, `eb48d8bd`);
  - #249's `Rows.compose_eval` and every other pin are unchanged.
- **Against #263's own record:** all 13 of its pins hold, except `Game.Lock.mono`'s grouping (#207's, as at #207's grant)
  and `Stmt.InRange` (#271's, granted).
- **#206's vectors:** 46 passed (the mirror through the checked `archivePart`, the check on all 21, the flat tests).
- **Recorded `check`** `r20260928-111145-bcfe` on `04cd8414` is running, due about 11:58Z.

**What to check:**
- that this `Logical`, with the product rows' B sides, is the one 1d composes and 1e folds (your N1 on #263, and note 2
  on #247);
- that nothing else in the train reads `ofBlock` (only `ComposeDag.lean` does).

**The alternative,** if you'd rather not review it now: the train lands without #263, at `6c135683`
(`cursor/flock-soundness-train-a-8569`: the six, #271 and P2), and #263 with this restatement follows in the next train.
