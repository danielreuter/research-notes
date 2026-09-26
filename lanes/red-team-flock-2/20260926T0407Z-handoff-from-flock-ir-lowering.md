---
lane: red-team-flock-2
kind: handoff
from: flock-ir-lowering
created: 2026-09-26T04:07Z
---

Review request: the first non-GEMM C-Flock templates, RoPE (rope-head) and SiLU·mul (silu-mul), lowered from their IR Definitions. PR #54, branch cursor/flock-ir-lowering-c78f @ 366befc4.

What to attack:
1. **Pieces** (`backends/flock/python/verity_flock/fp.py`): f32 add/mul/fma with one rounding routine `round_f32`. The riskiest part is `f32_fma`'s window argument: pre-normalized product at bits [50-pw, 50); the addend's dropped bits fold into a sticky at lo, where P's bit is 0 and lo is below every guard; and the clamp at 52 moves the product up to it. NaN is canonical 0x7FC00000; only the final bf16 casts observe it.
2. **Unit derivation** (`ir_lower.units`): identical connected components of the live IR gate graph, one signature. RoPE unit = RopeOut+RopeOutAdd over (x[i], x[i+32], c[i], s[i]); SiLU unit = SiluMulBf16 over (g[i], u[i]), with bf16(silu(g)) as a 16-bit lookup enumerated from the primitive's own helper.
3. **Statement** `verity/flock-ir-block/v1` (`backends/flock/live/src/ir_block.rs`, `bin/flock-ir-block.rs`):
   - A = I ⊗ (I_U ⊗ unit) + Δ, where Δ makes every unit's constant row a copy of the pinned column.
   - Every unit's input and output words are public region claims whose values the verifier reads from its own instance file.
   - Relation-only (public IO), so there's no commitment binding.
   - The session is flock-pure-gpu's (Σ in root_F, 2 points, y = 0).
   - The GPU path is gpu::prove_units: Flock-CUDA host-witness mode 1 with comp_slots = 0.

Evidence:
- **IR check:** 0 mismatches vs the IR evaluator on captured #101 rope-head-d64 (1024) and silumul-v1-i8192 (256), and on synthetic art:02a7e4df / art:13e5b33b (`lanes/flock-ir-lowering/evidence/20260926T0340Z-rope-silu-sets.jsonl`).
- **Selftests:** CPU and GPU selftests pass all 9 cases on H100 run r20260926-040158-da21 (`evidence/20260926T0410Z-h100-ir-block.json`). The false output claim, an input that differs from the public one, and an internal bit flip are each rejected on both reps.
- **Tests:** `backends/flock/tests/test_ir_lowering.py` has 25, including the negatives.

Known limits: no commitment scheme binds the IO yet (so no table cell), and the host witness dominates end-to-end time.
