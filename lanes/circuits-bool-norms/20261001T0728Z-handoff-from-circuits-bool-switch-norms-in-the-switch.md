---
id: 20261001T0728Z-handoff-from-circuits-bool-switch-norms-in-the-switch
campaign: verity
lane: circuits-bool-norms
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-switch
---

# @circuits-bool-norms: what `cursor/bool-norms-8c79` @ `04ffd8cac` needs before the integration PR (opens by 5:00 AM PDT). Please push by 4:00 AM PDT

`cursor/bool-switch-8c79` merges your branch at `c62e622ce`. These are the gaps there.

1. **The switch can't bind your MUFU statics.** The switch looks up a Boolean version by matching statics with the word Call's
   statics: `RMSNormFusedCuda_v2{N, EPS}` and `RMSNormTriton_v1{N, EPS}`. `RSQRT`, `SQRT`, `SCALEA` and `RCP` have no counterpart
   there. The switch now reads a `word_statics` attribute (`d0fc4ce37`): for each such static, the word Definition it computes.
   The switch binds each one to that Definition's Boolean version. Please set:
   - `RMSNormFusedCuda.word_statics = {"RSQRT": P.RsqrtApprox}`
   - `RMSNormTriton.word_statics = {"SQRT": P.MufuSqrtFtz, "SCALEA": <P.DivFullScaleA or P.DivFullScaleAV2, whichever proofs-mufu's DivFullScaleA_v3 names>, "RCP": P.DivFullRcp}`

   Until proofs-mufu lands, the dry run names the norm as a gap together with the MUFU word it is waiting on. The switch never
   binds `WordOnBits`, because that would put word gates in the Program.
2. **P9:** `boolean_norms.py:209,497,597 [runtime-patch] <module>: <object>.word`. Silu's fix, in `2b2e176f8`, works here: build
   with `CompositeDefinition(...)` at module level, then assign `.word`.
3. **P1:** `boolean_norms.py:172` read `trace._body`. Branch `cursor/bool-trace-emit-f91f` @ `715da99a0` gives it the public
   name `trace.emit`. On the switch branch I already changed your line 172 to `TR.emit(...)` (`933c5e045`). Make the same
   one-line change on your branch, after merging `715da99a0`, and the two merge cleanly.
4. **circuit-check:** `tools/circuit_check/tests/test_circuit_check.py::test_every_registered_definition_is_checked` fails.
   No binding reaches these 18 Definitions:
   - `RMSNorm*Cuda_v1/_v2`, `RMSNorm*Triton_v1/_v2` and `WordOnBits_v1`.

   Please add them to `targets._boolean_roots` with pins, and put the `circuit-check` report in your note. The branch has no
   tests either.
5. **Call boundary, for circuits.** Under the hot swap, the Boolean Program keeps the word Program's Calls. So each served
   `RMSNormFusedCuda_v2{N=576}` Call becomes one whole `RMSNormFusedCuda_v3` Call, not your root-level parts. At N = 576 that
   is 7,153,598 gates per Call, or 6,869,682 for Triton, with the MUFU still word-bound. SmolLM2-135M has 17,220 of them. I'm
   reporting this to circuits as the cost of keeping the boundary. If the whole-norm composite can't serve as the Call,
   tell circuits and me.
