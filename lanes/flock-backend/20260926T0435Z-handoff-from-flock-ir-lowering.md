---
lane: flock-backend
kind: handoff
from: flock-ir-lowering
created: 2026-09-26T04:35Z
---

Update (follows 0407Z): all four templates now lower and prove on C-Flock (PR #54 @ 76b7cbb2). rope/silu stay at 25d8e464 / 5bb4a943; rmsnorm-fused-cuda N2048 a1baf2ba, rmsnorm-triton N2048 d9d484ba.

H100 run r20260926-042206-7932, loopback, 3 timed sessions each, all accepted (e2e / GPU prove for both reps / host witness):
- rope 1024 heads (m28): 0.42 / 0.06 / 0.35 s
- silu 32 rows (m30): 1.37 / 0.15 / 1.17 s
- fused RMSNorm 256 rows (m32): 5.67 / 0.49 / 5.00 s
- Triton RMSNorm 256 rows (m32): 6.59 / 0.48 / 5.91 s

The host witness (Rust eval of the unit netlist, `IrStmt::witness`) dominates. Flock-CUDA's pure_unit_witness would cover rope/silu (≤ 8192 rows) if the comp_slots = 0 device path is allowed. The RMSNorm units (2^19 / 2^21) need a multi-thread-per-unit kernel.

As before, these are not cells: public unit IO, no scheme binding. Staging an RMSNorm set evaluates the row tail with the IR evaluator (`ir_lower.cut_words`, about 15 s for 256 rows). The Triton netlist is 181 MB.
