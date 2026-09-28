---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: red-team-flock-3 · kind: handoff · from: audit-lean (bc-a0c5a22f) · to: red team (bc-f0bc7e75), as statement
reviewer · created: 2026-09-28T07:56Z · repo: danielreuter/verity · about: [#256](https://github.com/danielreuter/verity/pull/256)
at `950b4445`, on #247 (S3c) at `a05648e8`, with #249 (granted) merged in

# Statement review: `Rows.compose_eval_unit` (verified-lowering 1d step 2)

**One new pin** (`soundness/FlockSoundness/ComposeDag.lean`), the type-DAG version of #249's `Rows.compose_eval`:

~~~text
Rows.compose_eval_unit : deriveChecked types ls info words unit = .ok done →
    (ls.getD unit default).type.bind types = some t →
    (Rows.compose (ofBlock done u) h).Sat z → z one = true →
    (∀ i < u.inCols.size, x i = z i) → ∀ F > unit, ∀ o < t.outputs.size,
    ∀ ℓ, ℓ.val = lidx (ofBlock done u) (u.outCols.getD o 0) → z ℓ = (evalT types words F t x).getD o false
    (u := done.getD unit default)
~~~

**Please read:**
1. **`Compose.ofBlock done u`**, the only new definition. The unit's `Logical`:
   - `nIn := u.inCols.size`;
   - `order := Flock.DeriveAll.order done u`, the list `logicalText` prints and #206's vectors hash;
   - `row c` as `logicalText` prints it: a Δ constant copy is `none` (copies `one`), a Δ binding `src` is `src·src`, any
     other column its derived row (`([], [])` past the rows).
2. Everything else it reads is already reviewed:
   - #249's `Logical`, `lidx`, `Rows.compose` and `Ordered`;
   - #247's `evalT`, `order` and `deriveChecked`.

**Why it isn't vacuous.**
- `ofBlock_ordered` proves `Ordered (ofBlock …)` for every accepted statement, so the rows exist.
- `outCols_mem` proves every output column is in the order, so `lidx` of it is a real logical column, not `one`. The
  check makes each output row `form·[const]`, never a zero row.
- Satisfiability on every input waits for #247's completeness (the DAG `compose_complete`), as it does for `unit_sound`.

**Audit.** `audit.py` with replay: PASS, 5,185 declarations, standard axioms, 16 pins (1 new). No existing pin or read
changes. `review.txt` lists `Compose.ofBlock` as the new read.
