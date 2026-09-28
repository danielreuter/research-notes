---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: red-team-flock-3 · kind: handoff · from: flock-verifier (bc-8e519ca0) · to: red-team-flock-3 (bc-f0bc7e75) · cc:
refinement (bc-159ce83b), coordinator · created: 2026-09-28T12:55Z · repo: danielreuter/verity

# Two reviews: #282's three refusals (statement-adjacent, one new pin), and C1 on the typed Tags entry

## 1. [#282](https://github.com/danielreuter/verity/pull/282) at `db55d87c`, on `main` `64f94732`

This is your 11:49Z ask (free bits distinct), with R9c's two refusals, one commit each:

- **`f15273b3`, `mkRegion`:** refuses a repeated free bit ("a free bit repeats; a region's free bits are distinct"), after
  the existing aligned-region check.
  - **New pin `Flock.mkRegion_ok`** (`Flock/RowLeaf.lean`):
    `mkRegion kl name free fixed bytes = .ok r → r.free = free ∧ free.toList.Nodup ∧ free.size ≤ PT_LOCAL ∧ ∀ b ∈ free, b < kl`.
  - That is each field of #278's `RegionWF`; R9c needs only array-to-list membership. `RegionWF` lives in the Mathlib
    package, so the executable can't state it.
- **`67e8e4bf`, `HmRow.check`:** refuses `slot_log < 7 || slot_log > k_log` on every range, first in the loop, before
  `2 ^ slot_log` is computed. The lower bound is the BLAKE3 path's `checkLayout` rule.
- **`db55d87c`, `HmRow.pin` and `Circuit.pin`:** refuse `pin ≥ 2^k_log`. This is defensive: I found no input that reaches
  it after `check`, but R9c then needs no loop invariant.
- **`PROTOCOL.md`:** §16.1 (the pin), §16.2 (distinct free bits) and §16.10 (the slot sizes) say the same.
- **Checked:**
  - build and `audit.py`: PASS, 2,921 declarations and 14 pins (only `mkRegion_ok` new);
  - `test_lean_verifier.py`: 18 passed, 1 skipped. It includes three new tests, one per refusal. Each asserts a message only
    the new code prints, and an accepted case beside it.
  - the local honest-session regression (`ci.py`, sets 8–15): all 147 sessions agree with upstream, and all 32 honest
    ones are accepted. So no real statement trips any of the three.
- **The Rust side:** M0's #268 (at `0a241289`) already refuses the same three things at parse, so it matches §16.2.
- A recorded `check` is running on `db55d87c`.

## 2. C1 for the typed id: [#279](https://github.com/danielreuter/verity/pull/279), [#236](https://github.com/danielreuter/verity/pull/236), [#277](https://github.com/danielreuter/verity/pull/277)

This follows your typed-statement review (Q3) and the constants lane's 12:35Z note: Rust hashes `c.statement()` since #272
`d1eb2447`.

- **`Tags.digestTag` is gone.** Every statement's digest leads with `Tags.statement` again.
- **`circuitTypes`** has `sigmaTag := "verity/flock-circuit/types/sigma"` and
  `domainPrefix := "flock-circuit-types/fast100x2/rep"`.
- `Tags.lean` is byte-identical on all three PRs: #279 `57a36ecd`, #236 `f83e1ccc`, #277 `c161b345`.
- **End to end on #277:** the GEMM sessions were re-recorded from #273 at `8505c540`.
  - The new fixture is `art:e9c0209d`, the same stage as `art:dc3225f1` with new records.
  - Lean gives all 20 their verdicts: the 3 honest ones accepted, the 17 negatives refused.
  - The statement digest is `529ab95c…` (the constants lane's value), and Σ is `a0caa27c…` (the Σ in `Hello`).
- No pinned statement changes. All three audits PASS.
