---
lane: coordinator
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-26T18:55Z
---

# The total tc_dot16 unit does not fit flock-pure-block's 2^13-row unit slot. No cell has run; step 1 needs a layout decision

The 18:20Z restart asks me to put the total `tc_dot16` into the GemmCoordinate pure-block unit. All 9 queued cells are sm80
BF16 (`bf16-ampere`), so this is the one unit to change.

- **The constraint.** A pure-block unit is one 2^13-row block (`pure_block::UNIT_LOG = 13`, used in about 38 places in Rust
  and in the CUDA region copies). Its fixed rows are:
  - 640 IO rows;
  - one 128-row word for `c_out` and one for `y16`;
  - the constant row;
  - padding to 128 before `c_out`.
  So a unit can hold at most **7,168 ANDs plus assertions**.

| unit (bf16-ampere, groups 8+8, W 25, F −132, F2fpBf16 epilogue) | ANDs | rows | fits 8,192? |
|---|---:|---:|---|
| today's finite census unit (`unit.unit`, 33 assertions) | 7,131 | 8,065 | yes |
| `fp.tc_dot16`, as the IR lowering uses it | 8,700 | 9,601 | no |
| my compact total unit (`evidence/total-unit/total_proto.py`) | 7,520 | 8,449 | no (352 ANDs over) |

- **The compact total unit** saves 1,180 ANDs over `fp.tc_dot16`:
  - it classifies each operand once (e_any, e_all, m_any), and the decode reuses those bits;
  - it drops the finite stand-in masking (`_finite_or_zero`). Any NaN or infinite operand or accumulator already forces a
    special result, so the finite path's value never reaches the output.
- **Checked (`total_check.py`):** equal to `verity.ml.tc.total.tc_dot_total(AMPERE_BF16_M16N8K16)`, and y equal to
  `f32_to_bf16_hw_word`, on 12,800 bit-sliced cases, 0 mismatches.
  - The cases include NaN, ±inf, signed zeros, subnormals and max-finite operands and accumulators.
  - 4,200 of them have finite results, drawn with near exponents.
  - It is not wired into `lowering.py`; there's no pin, and no GPU run.
- **Options:**
  - **(A) UNIT_LOG 14:** a 2^14-row unit slot in `pure_block.rs` and the CUDA prover. That's flock-gpu-link's code. It
    changes every layout's block geometry, since units are placed at `(unit_pos0 + u) << UNIT_LOG`, so it is a new
    statement. With it, even `fp.tc_dot16` as-is fits, and it would share the IR lowering's unit. It needs a red-team
    pass; after that the cells can run.
  - **(B) Cut 352 more ANDs** from the compact unit.
    - That means touching the census's `group_sum` / alignment network, which isn't mine to change without the census
      owner. The special-value logic that is mine costs about 390 ANDs in total, so nothing is left to trim there.
    - Alternatively: a netlist format where only the last unit of a VU carries `y16`. That is also a Rust change.
  - **(C) Keep the finite unit as an explicit named choice.** The rule allows that only above a 10× cost, and total is
    about 1.05× here, so this isn't allowed.
- **My recommendation:** (A), done by flock-gpu-link. Then I wire the unit under `verity/flock-pure-block-total/v1`
  (`domain="total"`, NaN/inf selftests and negatives), and get red-team-flock's review before the 9-cell queue runs.
- **Pods:** none created, $0 spent.
- **Also:** the lane branch is on GitHub at 755a397e.
