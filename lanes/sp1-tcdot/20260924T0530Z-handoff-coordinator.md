# Scope: TC_DOT must cover all five targets; today's chip matches none of them (fp8 E4M3 on the Ampere pipeline)

User (05:21Z): SP1-stock and SP1-precompile, populated for all targets.

What the fork's own header says (`crates/core/executor/src/tc_dot.rs`): one 16-element tile step `D = C + A·B`, fp8 E4M3
operands with Ampere GroupSum semantics (25-bit adder); "SEMANTICS CAVEAT: real fp8 tensor cores exist only on Hopper
(QGMMA) with different constants; this 'fp8 Ampere' contract is the bf16 Ampere pipeline fed with fp8 products." (Ada sm_89
has FP8 too.) So no Table 2 row is proved by the chip as it stands.

Parameterise the chip rather than copying it. Priority:
1. bf16 operands on the Ampere pipeline (A100 BF16 row, `tc-ampere-bf16`): the closest change (operand decode).
2. fp8 E4M3 with the 14-bit adder and K=32 grouping: Ada (4090 FP8 row, fp8-ada) and Hopper (H100 FP8 row, fp8-hopper).
3. bf16 on Hopper (H100 BF16 row).
4. NVFP4 with block scales (5090 row), last.
Source of truth for the constants: `backends/numerical/python/verity_numerical/checker/params.py` (`Params.from_model`:
AMPERE_BF16_M16N8K16, HOPPER_E4M3_K32, ADA_E4M3_M16N8K32; find the Hopper BF16 model) and `checker/reference.py`. Oracle:
each variant must reproduce every y of the row's frozen instance set bit-exactly; each variant needs soundness tests and
negatives. Cells are proved on the row's own device (one extra pod per target while a variant proves, terminated after).
Budget raised to $25. If the GPU prover cannot prove the chip at all, say so early (handoff to the coordinator): it decides
whether this variant can fill any cell.
