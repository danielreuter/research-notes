---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
lane: stratified-law
kind: handoff
from: flock-verifier
created: 2026-09-27T17:00Z
---

# flock-verifier → stratified-law: the Lean sampler and U2 for `stratified` are final at #167 `ebc94ac5`

[#167](https://github.com/danielreuter/verity/pull/167), onto `main`, follows your 15:50Z encoding with no amendment. It is
built on `main`, which already has #142's shared-row files, so one head covers A4's files and the stratified law.

## What it does
- **The command:** `flock-verify draw --program P --partition Q --stratified K` prints `DRAW {law, population, k, strata, units}`.
  - The verifier derives the strata itself: `Q_template_instance(s)` v0, grouped by descriptor id, adjacent ranges merged, in
    order of first unit, with your `k_s` rule. Any other query is refused.
  - Each stratum runs `subset k_s n_s` on its own stream of operating-system bytes, `2 k_s · w(n_s) + 64` long. When a
    stream runs out, that stratum alone is extended and rerun.
  - For tests, `--stream-file F` cuts the given bytes into consecutive per-stratum segments.
- **U2 for `stratified`** follows your §4 list exactly.
  - `draw-test FILE --program P --partition Q --stratified K` also holds each draw's law and population to the verifier's
    own, like `check_draw`.
  - In `verify`, a drawn session's stratified strata must be the verifier's own derivation when it holds the program and
    partition.
- **Unchanged:** the uniform `subset` and `bernoulli` laws.

## Agreement with #164 `83cc459c` on #161 `5412c9cb` (`backends/flock/verifier/stratified_agree.py`)
- **A4 P6,** your six-template program at A4's sizes:
  - under `stratified:1024`, the strata are exactly your table: `k_s` = 1, 933, 2, 1, 1, 89, and 1,027 units drawn;
  - `audit.core_law` on the Lean-derived law gives a count bound of 91,063 at 2⁻²⁰, a bound of 286 for a 287-unit
    stratum, and escape 0 for a wholly wrong template.
- **Everything else agrees:**
  - 44 programs and 135 draws: the law equals `derive`'s, the units equal the sampler written out in Python, and
    `check_draw` accepts every draw;
  - 1,931 mutated draws get the same U2 verdict from both;
  - 89 refusals agree;
  - operating-system inclusion frequencies are within 1.84 standard deviations of `k_s / n_s`.
- **Upstream regression:** all 16 sets agree at this head.

## One leniency in core, for you
- `check_draw` accepts a stratum's `"k": true` when its `k_s` is 1. Python's `True == 1` passes both `strata_problem`'s
  rule check and the `law_of(draw) == law` equality.
- U2 refuses it, and the script reports it as `core_takes_a_boolean_stratum_k`.
- A fix: `_int(s["k"])` in `strata_problem`.

## Not in #167
- A check that a member session's `subset` share is exactly its stratum of the union draw. Your §6 keeps that in the audit
  record. I can add `--union-draw` to `verify` if you want it on the Lean side too.
