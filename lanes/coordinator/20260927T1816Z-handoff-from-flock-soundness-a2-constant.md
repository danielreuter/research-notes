---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: handoff · from: flock-soundness (bc-9e538dc5) · created: 2026-09-27T18:16Z · repo: danielreuter/verity · about: PR #127, #163, #170, #171, #173

# flock-soundness → coordinator: A2's constant is fixed in all four held PRs; A1's removal is on top, ready for re-audit

## New heads, all pushed

| PR | Branch | New head | What changed |
|---|---|---|---|
| [#127](https://github.com/danielreuter/verity/pull/127) | `cursor/flock-link-options-8569` | `f1c90b1f` | A2's statement (`Assumptions.lean`, `ASSUMPTIONS.md` §3, `DESIGN.md` §3) and its numbers |
| [#163](https://github.com/danielreuter/verity/pull/163) | `cursor/flock-expected-time-8569` | `b5009bc9` | the constant in `link_mass_le` and `flock_batched_linkSoundE` (#127 merged in) |
| [#170](https://github.com/danielreuter/verity/pull/170) | `cursor/flock-link-qs-8569` | `972d5111` | the Q_s numbers of record (#163 merged in; Lean identical to #163's) |
| [#171](https://github.com/danielreuter/verity/pull/171) | `cursor/audit-link-composed-f568` (audit-lean's) | `23b2df6e` | `linkBoundE`'s constant (#163 merged in). One commit of mine, at your request; audit-lean is told. |
| [#173](https://github.com/danielreuter/verity/pull/173) | `cursor/flock-a1-proved-8569` | `16785b18` | A1 removed (#170 and #171 merged in, so `FlockLinked.lean` is covered too) |

Merge order: #127, #163, #170, #171, #173. Every push was a fast-forward; no history was rewritten.

## The corrected assumption (for the red team, bc-f0bc7e75, the named statement reviewer)

**A2.** For one explicit finder (a game `g` played by a fixed strategy `s`, outputting `out b` after `cost b` SHA-512
evaluations, counting `t` for each run of the prover):

~~~lean
(prob (fun b => ∃ x y, out b = some (x, y) ∧ x ≠ y ∧ H x = H y) g s).toReal ≤ expect cost g s / 2 ^ (256 : ℝ)
~~~

It was `/ 2 ^ (256.5 : ℝ)`. The Prop is still stated per finder, and only the link theorem uses it.

- **Why 2^256.** A random oracle with `N = 2^512` outputs obeys `Pr ≤ E[Q]/E[τ_N]`, which is sharp.
  - `τ_N` is the number of distinct inputs hashed until the first collision.
  - `E[τ_N] = √(πN/2) + 2/3 + o(1) ≈ 2^256.33`, so `T/2^256` holds with 0.33 bits to spare.
  - I checked the scoping lane's proof: `Pr ≤ Σ a_i w_i` with `a_{i+1} ≤ a_i(1 − w_i)` and `Σ a_i ≤ E[Q]`, then Chebyshev's sum inequality with weights `∏(1 − w_j)`.
- **Why not 2^256.5.** `min(1, q²/2^513) ≤ q/2^256.5` holds only for a budget fixed in advance. Hashing until the first collision beats `T/2^256.5` by 1.13.
- **Why not the sharp `√(π/2)·2^256`.** It would give back 0.33 bits, with no margin under the ideal bound. It is noted as a later option.
- **CDGSY24 gives no SHA-512 constant.** I read ePrint 2024/1434: Theorem 2 is Kilian's expected-time soundness in terms of an abstract expected-time binding error. So the docs now cite CDGSY24 for the notion only, and state that the constant is ours.
- **Unchanged:**
  - the strict-time comparison row, whose `q/2^256.5` is the fixed-budget bound;
  - the knowledge term's `Adv₀`, which is strict-time;
  - `δ_tree`, the compiled theorem and the random-oracle column.

## Re-derived numbers of record

Every expected-time figure moves by exactly 0.5 bits.

| | Before | Now |
|---|---|---|
| Link term (#170's record) | `t·Q_s(8N₀/e)/2^256.5` | `t·Q_s(8N₀/e)/2^256` |
| Audits A–D | `t·2^-218.9`, `-209.9`, `-209.9`, `-206.9` | `t·2^-218.4`, `-209.4`, `-209.4`, `-206.4` |
| Audit B at `t = 2^80` | `2^-129.9` | `2^-129.4` |
| Lifetime at `2^-128`, A–D | `N·t ≤ 2^78.9` to `2^90.9` | `N·t ≤ 2^78.4` to `2^90.4` (audit B `2^81.4`) |
| With `N_s` (#127's form), audit B | `t·2^-205.6` (`2^-125.6` at `2^80`) | `t·2^-205.1` (`2^-125.1`) |
| With `N_s`, lifetime | `2^66` to `2^87` | `2^65.4` to `2^86.7` |

- **Where they are updated:**
  - `DESIGN.md` §3 (both tables, the `t = 2^80` line, the constant, the finder and the proved theorem);
  - `ASSUMPTIONS.md` §1.4, §3 (A2) and §7;
  - the lifetime doc, `docs/lifetime-soundness.md`: the Headline with a correction note, §1, §3's table, §4, §5's coverage table and levers, and §9;
  - my lane report's levers section.
- **The gap the doubled terms sit under** is 19 bits with `Q_s` (unchanged, 19.9) and 24 bits with `N_s` (was 23).

## Checks

- **#163 `b5009bc9`:** `lake build` passes, and `Check.lean` has 223 entries, all standard axioms.
- **#171 `23b2df6e`:** `lake build` passes, and there are 229 entries, including `flock_batched_count_linked`, `_drawn_linked` and `_placed`, all standard.
- **#173 `16785b18`:** `lake build` passes, and there are 231 entries, all standard. `pytest tests packages/verity/tests/claims backends/flock/tests backends/numerical/tests/bench/test_views.py` gives 227 passed, 13 skipped.
- **`ASSUMPTIONS.md` size:** 48,815 bytes on #127, 49,021 on #170 (131 bytes left) and 48,124 on #173.

## Also fixed

**`flock_batched_linkSoundE`'s docstring formula was corrupted in #163.** In `\frac`, `\rho` and `\rm`, the escapes had become form feeds and line breaks, from a non-raw Python string in an earlier edit. It compiled, but the text was wrong. It is repaired in #163's head, and I checked every Lean and Markdown file in the stack for control characters and broken TeX.

## A1 removal (#173), which also needs audit

- **What it does.** It deletes `hMCA` (A1) from every theorem: 60 binders and their call sites in 26 files, #171's `FlockLinked.lean` included. The proof is `JohnsonMCA.lean`, `mcaError_le_bchks25`, from DKT26 in ArkLib #907 at our pin. The details are in #173's description.
- **The statements change**, so they need the red team's review. Each theorem loses `hMCA`, and `prCoin_mca_le` now takes a `Fin n` domain.
- **#130's soundness pins will need re-recording** once both land.
- **Table 1:** Flock's MCA basis is now `machine-checked`, so the Flock configurations no longer cite `rs-proximity-johnson`.

## New store folder

- I created `internal/lanes/proximity-gap-scoping/` for my reply to the scoping lane, which asked for replies there.
- It holds `20260927T1816Z-handoff-from-flock-soundness.md`.

## Next

- **The η retune waits for the scoping lane's bridge lemmas.** I'll fold it into #173's change set, as you said. My reply to them gives the integration points.
- **Then the RoPE lowering.**
