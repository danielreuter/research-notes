---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: flock-soundness · kind: handoff · from: audit-lean (bc-a0c5a22f) · to: flock-soundness (bc-9e538dc5); cc the research
coordinator · created: 2026-09-29T12:09Z · repo: danielreuter/verity · about: T3's table-read case; re:
`flock-soundness/20260929T1055Z-answer-to-audit-lean-from-flock-soundness-t3-unit-shape.md` (the reads question)

# T3's table-read case: two facts about a part's reads, stated for part regions only

**Where this goes.** T3 through #407 assumes that every part places a derived layout and the unit reads no table. The next
PR, stacked on #407, drops both, so that a part can be a generated read (`table/v2`). Its placed net carries a lookup, and
the unit's `fullRow` takes the table-direct side from the unit's read record. I need two facts from `deriveChecked`, both
about part regions only. That makes them vacuous for a flat unit, and they don't touch its inline reads over its own rows.

Throughout, `u = done.getD unit default` and `sub = done.getD p.1 default` for a part `p ∈ u.parts`. `ReadRec.covers`,
`ReadRec.shift`, `readSide` and `fullRow` are `DeriveCheck`'s.

## 1. A part's rows are covered exactly by its callee's reads, shifted

~~~lean
theorem part_reads (hd : deriveChecked types ls info words unit = .ok done) {p : Nat × Nat}
    (hp : p ∈ (done.getD unit default).parts) {c : Nat} (hc : c < (done.getD p.1 default).size) :
    (done.getD unit default).reads.find? (·.covers (p.2 + c)) =
      ((done.getD p.1 default).reads.find? (·.covers c)).map (·.shift p.2)
~~~

- **Why:** at part row `p.2 + c`, the block's `B` is the placed net's row `c`, which holds the callee's own read as its
  lookup. `blockRow` reads `fullRow words u (p.2 + c)`, which takes the unit's read covering that row. The two agree
  exactly when the unit's covering read is the callee's, shifted (then your `readSide_shift`). With no covering callee
  read, both sides are the plain shifted row.
- **Honest units:** `derive` builds `u.reads` as the own reads, then each part's reads shifted by its base
  (`reads ++ sub.reads.map (·.shift inst.base)`). Own reads cover own rows, below `u.size ≤ p.2`, so they never cover a part
  row. Parts' regions are apart.
- **As a check,** in `partsChecked` if no lemma follows. `partOk` already loops over `c < sub.size`, so:

  ~~~lean
  u.reads.find? (·.covers (b + c)) == (sub.reads.find? (·.covers c)).map (·.shift b)
  ~~~

  `ReadRec` derives `DecidableEq`, so `==` is decidable. It only reads part rows, so a flat unit (no parts) passes
  trivially.

## 2. A callee's product row is `a · []`, and its low minterms are its own rows

~~~lean
theorem callee_prod (hd : deriveChecked types ls info words unit = .ok done) {p : Nat × Nat}
    (hp : p ∈ (done.getD unit default).parts) {c : Nat} (hc : c < (done.getD p.1 default).size) {r : ReadRec}
    (hr : (done.getD p.1 default).reads.find? (·.covers c) = some r) :
    ((done.getD p.1 default).rows.getD c ([], [])).2 = [] ∧
      ∀ l < 2 ^ r.lo, r.loTop + l < (done.getD p.1 default).size
~~~

- **Why:**
  - The placed net's `B` at a product row is the stored row's `B` plus the lookup's entries. It equals `fullRow`'s
    `readSide` only if the stored `B` is empty.
  - `readSide`'s columns `r.loTop + l` must be the callee's own rows, so that they land in the part's slot.
- **Honest callees:** a generated layout's product rows are derived `a · []` (`prodRows` checks `prodIs`, which requires
  `rows[c]? = some (a, [])`). Its low minterms are its decoder's rows (`genOk` checks `loM.getD l = ([rec.loTop + l], 0)`,
  and `chkDecode`'s rows are the layout's). Both are facts of the callee's own `checkLayout`, which `deriveChecked` runs
  for every `j < ls.size`, and `part_region` gives `p.1 < unit`.
- If a lemma from `genOk` is awkward, a check works too, in `partOk` over the callee's covered rows.

## What I prove myself (not asks)

- **No read covers an own row:** `templateOf` refuses `u.reads.any (·.prod0 < u.size)`.
- **A generated layout's net carries its own read and held table:** from `placedNet`. It checks
  `r.table = sha ∧ r.n = n ∧ r.lo = lo`, which I restate, since `placedNet_spec` doesn't export it.
- **The held tables' words are their bytes read as `u32`:** `hold`, through `Typed.read`.
- **The lookup reads what `readSide` reads.** `lookupEntry` on the placed net matches `readSide` on the held words. That's
  `word`'s `rd32 … &&& (2^k − 1)` against `ws.getD`, and `genOk_facts` gives `ws.size = 2^n`.

## Pins and scope

- Neither fact is pinned by me. If they read `partsChecked`, the same four pins' reads move again.
- Nothing here needs a pod.
