---
id: 20261001T0403Z-handoff-from-824e54a2-migration-addendum-rowseed
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: PoUW FP8/FP4 Lean coordinator (bc-824e54a2), for its worker bc-5382063c
---

# Migration handoff addendum: RowSeed (M3), written for bc-5382063c

bc-5382063c (RowSeed), which bc-824e54a2 drives, has posted no migration handoff, and the 7:40 PM PDT deadline has passed. This covers its state from the store and its 6:34 PM PDT report.

- **Branches and PRs:** none. It works in the Cursor store's staging.
- **In flight:** nothing heavy. Its replay audit is parked for memory, and no node-2 job is queued.
- **Half-done state:** `internal/pouw-fp8/rowseed-staging/` holds the README, `rowseed-pins.json` (28 records), the review packet `review-fragdraw-named-assumption.md`, and `Pouw/PearlC/{TTOutRowSeed,RowSeedGamma,RowSeedCode,RowSeedFragment,RowSeedSkip,RowSeedAssumptions}.lean`.
  - `FragDraw` is the named `Prop` `Pouw.PearlC.Assumptions.FragDraw` (Daniel's 5:52 PM PDT ruling), in `RowSeedAssumptions.lean`, with an `assumptions` entry and a `layers` rule. Only `ttOutRowSeed_skipClass` reads it.
  - **All 28 pins are GO** (bc-22298e90, 6:43 PM PDT).
  - **VM-only:** `/tmp/p1work/` holds private build copies, which can be rebuilt from the store plus the staging.
- **Next step:** the kernel replay audit (`check.sh` scale, about 5.7 GB; a node-2 one-shot if the VM is short), then the M3 store merge. The merge adds an `assumptions` entry, so it needs an exact policy prediction, not M4's unchanged-policy check. `-h3` stays open until M3 is merged.
- **Traps:**
  - The P2 main line (`ttOutRowSeed_of_ttOut`, `ttOutTileRowSeed_of_ttOutTile`) takes no named assumption. The skip-class line takes `FragDraw`.
  - C6 (`PearlCSem.RowDrawn`) is a definition, cited beside the skip-class line.
  - 11 of the records read `SaltDead` through `devAt`, so re-run `--update` on the current store.
  - `Gamma.lean` must be `593e4e43…`.
