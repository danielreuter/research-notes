---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: backend GPU sweep (bc-ea1c2c4f) and constant-API rollout (bc-613ddf45)
created: 2026-09-28T01:00Z
---

# M0's circuit prover on main: PR (a) is [#192](https://github.com/danielreuter/verity/pull/192), head `adcf38bf`

**Branch:** `cursor/flock-m0-prover-4d6a`, head `adcf38bf4a4bd7aacffdd04d2c9539f6c061deda`. It is #83 `73a273d4` merged with `main`
`df3bc5e1` (train K), plus naive inline table reads. It goes to the research coordinator the moment `check` passes, which is
running now. If `check` forces a fix, the head moves, and I'll post the new one here.

**What differs from #83:**

- **Inline table reads.** `ir_lower.layout` lays each `gf2` table read out as plain rows of the unit, with no slot type. A
  class whose unit reads a MUFU table now stages and proves through `circuit.compose` like any other.
  - For #182: drop `class_statement`'s `"lookup" in cc.circuit.kind` refusal.
- **`tc_units`.** `tc_units(prim=None)` accepts `AmpereBF16TcDot16_v1` or `_v2` (and Hopper), and refuses two step ids in one
  target. This is the lowering lane's resolution, so #182's local conflict with #140 is gone.
- **The glue moved to PR (b).** The multi-table statement (`flock_live::glue`, `flock_live::tables`, `verity_flock.tables`, the
  `glue` feature) is in (b), branch `cursor/flock-m0-glue-4d6a`, stacked on (a). Nothing in the circuit prover reads it: build
  with `--features sha512` (plus `seed-injection` for selftests), with `glue` only on (b).
- **Pins.** Every template's circuit pin changed from #83, because train K's lowering makes smaller unit circuits. For
  example, the tensor-core step unit goes from 8,623 to 8,260 ANDs. The PR body lists them all. Re-stage anything you
  pinned against #83.
- **The selftest's input-flip case** now tampers when a block holds one unit (your 20:50Z finding).

## Update 02:55Z: (a) was final at `adcf38bf`; (b) is #193 at `b47f8009`

- **(a) [#192](https://github.com/danielreuter/verity/pull/192) stays at `adcf38bf`.** Its `check` passed, the red team
  granted it, and it's with the research coordinator for tonight's merge.
- **(b) [#193](https://github.com/danielreuter/verity/pull/193) is at `b47f8009de8b3b0d86f3d9225e5bbcbecd9bcd0b`,** stacked
  on #192. Its `check` passed too, and it's handed off to merge right after (a).
  - Build with `--features sha512,glue` only if you need `flock_live::tables`.
  - The red team's grant is scoped: nothing may cite `verity/flock-tables` until that statement has its own review.
