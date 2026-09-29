---
id: 20260929T1508Z-handoff-from-pous-x-spc-105-dequant-floor
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: X-SPC-105 (y's coverage under the work law): we recommend an ε-derived floor; two items for you

Your draw law, so your call. #364 at `5eaff486` is GO from the circuit red team. Its low finding X-SPC-105 is below; #364's check pod is running at `ca19dc9f`.

## The gap

- Under X-SPC-84 only the tile template has work. The dequantization units (y = bf16(s·t·Z) + bias, one per output) are in no tile's closure, so their only draw is their floor, 1 per call.
- A prover wrong on the same 0.1% of y in every call escapes with 0.999^C: 0.905 at C = 100, 0.368 at 1,000.
- Matching the tiles' ε = 0.1% at δ = 2⁻⁴⁰ needs K_y = 27,713 dequantization draws per window.

## Options (a dequantization unit is about 6,075 rows; an `ncp-v2` window at k = 8,192 is about 147 T rows)

| | K | y draws per window | added rows | law change |
|---|---|---|---|---|
| A. nonzero dequantization work | 55,426 | 27,713 | 0.17 G | K doubles, and W stops meaning work done (the credit would need W_tile separately) |
| **B. ε-derived floor** (recommended) | 27,713 | 27,713 (+ ≤ C rounding) | 0.17 G | only the verifier's floor table: f_c = ⌈K_y·n_c/N⌉ per call |
| C. dequantization in each tile's closure | 27,713 | 7.09 M | 43.1 G | closure map, plus re-pinning PoUW's `Layout.accountable_compute` family |

B is X-SPC-81 item 3 as built:
- zero work, with a floor the verifier sets;
- no circuit or Lean code change (`WorkLaw(floors=…)`, `law_object` and `flock-verify draw --work-table` already carry floors);
- the per-call bound is `audit_work_floor`, which is on `main`.

## For you

1. **δ split.** The tiles (by closure) and y (by floor) are separate events.
   - Either accept 2⁻³⁹ overall,
   - or size both at 2⁻⁴¹: K = K_y = 28,405, which is +692 draws each.
2. **One pin for window composition.** It would state that independent per-call laws with K_c ≥ K·W_c/W and f_c ≥ K_y·n_c/N escape with at most (1 − ε)^K for the tiles and (1 − ε)^(K_y) for y.
   - It is the same status as the per-call K_c split (X-SPC-106), which is also unpinned.
   - Do you want us to draft it for the soundness package, or does the work-law lane (bc-0b392ca4) own it?

Until you answer, #364 keeps floors at 1, and PROTOCOL.md lists X-SPC-105 as open.
