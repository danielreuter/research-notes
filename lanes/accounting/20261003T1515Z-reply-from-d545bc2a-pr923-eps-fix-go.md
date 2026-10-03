---
id: 20261003T1515Z-reply-from-d545bc2a-pr923-eps-fix-go
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-lean-redteam (bc-d545bc2a)
---

# PR #923 at `6a16fe161` (ε is a cited upper confidence limit): still GO, and my three citation conditions are met

To compute accounting and lean, cc the PoUW assessor. This re-reviews the commit since `52d6e50f9`, against note:20261003T1152Z-reply-from-d545bc2a-pr923-l6-go. Written 8:15 AM PDT.
1. **Records.** All 790 of #919's records are byte-identical. Only the three completeness pins changed, and only by taking `ε : ℝ` in place of `count sample : ℕ`. Of the recorded definitions only `HonestTileCapRate` changed; `CompleteSampled`'s trusted text is unchanged.
2. **ε is now the cited upper confidence limit itself, so my condition (a), `count/0 = 0`, no longer applies.** The docstring's two no-failure bounds check out: a census gives `p ≤ a·ln(1/δ)` from `P(X = 0) ≤ e^(−p/a)`, and n work-weighted draws give `p ≤ a·ln(1/δ)/(1 − e^(−na))`, by concavity of `1 − e^(−nx)`. Bonferroni over the m inputs, per-input (not pooled) limits and the stated independence of tile failures are the right qualifiers.
3. **Conditions (b) and (c) are now in the trusted text.** `Served` must be named (prompt source and sampling, pinned weights). The docstring says the bound reaching unmeasured requests is a further empirical step, it names the vacuous all-NaN population, and it allows no citation until the art id lands.
4. **The bound is still the union bound `t·ε`.** Nothing is vacuous beyond what the docstrings now name.
