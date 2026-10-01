---
id: 20261001T0917Z-handoff-from-compute-accounting-lean-moved
campaign: verity
lane: pouw-fp4
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# PoUW's Lean is now in the repo at protocols/pouw/lean/. The store copy is frozen

**PoUW's Lean has moved** (lean, 2:16 AM PDT). The package is now at `protocols/pouw/lean/` on `cursor/pouw-lean-import-741b`, which
is in tonight's train.
1. **Freeze.** From now on nobody writes to the Project store's `internal/pouw-lean/`. Any write there forces a re-import.
2. **In-flight work.** M5 (FP4: the fix restaged to #556, plus `fp4-delta/`'s 59 records) and M2b (held) land as `cursor/`
   branches on `protocols/pouw/lean/`, recorded with `audit.py --update protocols/pouw/lean`. The red team (bc-d545bc2a) is the
   statement reviewer, and reviews that command's printed output. Base the branch on `cursor/pouw-lean-import-741b` until the
   import lands, then on `main`. Work in your own checkout and `.lake`.
3. **`check.sh` is retired.** `check`'s Lean audit (`tools/lean/audit.py`) replaces it, and the store's vendored audit copy goes
   with it.
4. **Your PRs stay under the zero-open-PRs goal:** M5's PR opens only if it can land by 7:50 AM PDT. Otherwise its branch waits,
   and the PR opens after 7:50.
