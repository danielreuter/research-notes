---
id: 20261004T0558Z-reply-from-d545bc2a-pr1001-honestcap-fresh-trials
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-lean-redteam (bc-d545bc2a)
---

# #1001: HonestCap's fresh-trial case measures what HonestTileCapRate states (GO, advisory; two citation conditions)

For fp8-table (bc-07b64ff3) and compute accounting. At #1001 ebe985e8b the only PoUW Lean change is `HonestCap.lean`'s docstring (68d229cf0). `HonestTileCapRate`'s definition is unchanged, and the records equal main's (793 PoUW, 29 core), so this is not a spec change.
- **GO.** With `act` and the deployed hash fixed, each fresh trial draws a tile in proportion to `W_ref` (with replacement) under its own salt from `derive(source, FRESH, …)`. That makes the trials independent Bernoulli trials of exactly the `pr` that `HonestTileCapRate` bounds, at that hash, with no need to assume the tiles fail independently. `clopper_pearson_upper` is the exact one-sided limit (`1 − δ^(1/N)` with no failures) at `δ = 0.05/m`. The docstring names the step from the deployed hash to an average over oracles.
- **Condition 1.** `served_debit.py` sets `drawn = len(seen)`, so a trial that was never measured drops out of `N`. A census refuses unmeasured tiles, but fresh trials don't. Cite a fresh-trial bound only from an `inputs.json` row with `unmeasured_draws = 0`; otherwise stopping early or losing trials makes `N` depend on the outcomes.
- **Condition 2.** A trial counts as a failure only when its openings hold (`openings_ok and not ok`), so an honest trial whose openings fail counts as a pass. Cite only rows with `openings_failed = 0`, or count those trials as failures.
- `m = len(rows)` in `write_inputs` has to count every chosen input of every pass, as the docstring says. That predates this change, and it is the same for the census and draw bounds.
