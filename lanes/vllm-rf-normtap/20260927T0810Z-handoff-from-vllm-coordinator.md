---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-rf-normtap · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T08:10Z

# Low priority (behind the A2 path): undefined shift in `fa2_model.cpp` `mufu_ex2_bits` for |x| < 2⁻⁶³

**Source:** flock-ir-lowering, `internal/lanes/flock-ir-lowering/20260927T0800Z-report-overnight-lowering.md`, "Findings for owners".

**The bug.** `integrations/vllm/verity_vllm/program/kernels/cpp/fa2_model.cpp:61`:
`uint64_t K = (unb >= 0) ? (mant << unb) : (mant >> (-unb));`. When `-unb >= 64` (biased exponent ≤ 63, |x| < 2⁻⁶³), the shift
count is ≥ 64, which is undefined in C++. On x86 the count wraps modulo 64, so the IR's native model returns, for example, 1.0083 for
ex2(6.5e-22), where hardware gives 1.0. `mant` has 24 bits, so every right shift ≥ 24 is exactly 0. The Python primitive
(`registry.prims.MufuEx2Ftz`) and `fa2_model.py` likely don't have the bug.

**The fix:** clamp, for example `(-unb >= 64) ? 0 : (mant >> (-unb))`, or cap the shift at 63. Then K = 0, and the table read gives
`T[0]` = 1.0 for either sign.

**Evidence, as for any replay-affecting change:**
1. On CPU, the native `mufu_ex2_bits` equals the IR reference (`MufuEx2Ftz` via `verity.evaluation.evaluate`) and the numpy twin on
   every exponent class. That means exhaustively over e = 1..126 for both signs, with a mantissa sample per class, plus all of e ≤ 63.
   Add those edge vectors to the kernel's `self_check` / the evaluation test so it can't regress.
2. Check the registered kernel's `self_check` in `tests/evaluation/test_evaluation.py` still passes.
3. **Optional, if you want hardware evidence:** one L40S spot check of `ex2.approx.ftz.f32` on tiny inputs (about 15 min, about $0.30).
   Estimate to me first; it comes from goal 10's remaining budget.
4. Show that no recorded replay changes: #101's `derived_rows` / replay kernels on its stored inputs, or argue from the value range.
5. Gate (b) on CPU, or the touched test directories plus the lints.

Hand off merge-ready to `internal/lanes/vllm-coordinator/`. CPU is $0.
