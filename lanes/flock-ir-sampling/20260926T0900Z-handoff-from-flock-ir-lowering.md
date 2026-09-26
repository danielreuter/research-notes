---
lane: flock-ir-sampling
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T09:00Z
---

# flock-ir-lowering: what the piece library and IR walker gained for attention, and what you can reuse for GumbelTopPTokenSelect (PR #54 branch, f4cd5d4e)

No action is needed; this is so we don't collide in `fp.py` / `ir_lower.py`.

- **`fp.py`:** one addition, `tc_dot16(C, acc, a, b)`: `AmpereBF16TcDot16` on every encoding, 8,623 ANDs, matching the IR on 6,000 vectors. Nothing else in `fp.py` changed. If you add pieces there, please append them in their own section, and send me a handoff if you touch `round_f32`, `f32_add`, `f32_mul`, `f32_fma` or `lookup` (the four granted templates' pins depend on them).
- **`ir_lower.py`:**
  - New pieces: `PIECES["AmpereBF16TcDot16_v1"]`.
  - New tail primitives: the FTZ f32 ops, `F32Max`, `GuardNegInfZero`, `MufuEx2Ftz`, `Fa2InvSum` and `F2fpBf16`, with Rust ports in `live/src/ir_tail.rs` differentially tested (300,000 vectors, 0 mismatches). MUFU tables are pinned in `TABLES` / `ir_tail::TABLE_SHA256`, and `write_tables` writes them.
  - `tc_units(target)`: units = every gate of one primitive, ports in operand order. It supports public input leaves (read as cut words and hashed by the verifier), zero leaves (a constant word the IR pads with), and outputs the tail computes. If sampling needs "every X gate is a unit, the rest native", generalizing it is probably easier than `units()`.
  - Every netlist now carries `LEAVES` (IR6) and, when cut, `CUT`; the pins cover both.
- **Frame:** `verity/flock-ir-frame/v3` (`ir_frame.py`, `live/src/ir_frame.rs`) takes rows with a short last chunk, public ports, zero leaves and tail-computed outputs; `plan_tc` is attention's placement. Sampling's vocabulary-wide rows will probably want their own planner beside `plan` / `plan_tc`.
- **Spine test:** `backends/numerical/tests/bench/test_cell.py`'s "unsupported template" example is now `gumbel-top-p-token-select` (attention is lowered). When your template lands, switch it to another unlowered one, or drop the case.
