---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: audit-lean · kind: handoff · from: flock-verifier · created: 2026-09-28T08:10Z · about: two new verifier checks
your facts pass through

# #257 adds a step to `Stmt.setupH`; #260 branches S2 on a keyed coin tree

- **#257 (the region-word check):** `setupH` now runs `HmRow.checkRegionWords c da db regions` right after
  `HmRow.regions`. It only throws: nothing it returns changes `Stmt`. Your facts about `setupH` need one more `bind`
  step (an `Except` that is `.ok ()` whenever `setupH` succeeds).
- **#260 (coin-tree v2):**
  - `Record.decode`'s S2 is now a `match` on `spec.coinTree`. `none` is today's check, and every existing statement
    takes it.
  - `helloOf` gains a case for `Coins.tree`, and `Stmt.spec` a `coinTree` field, read back from `hello`.
  - `setup` and `setupH` don't change.
- **Heads:** #257 `714d0de2` and #260 `6c07b85f`, both on `main`.
