---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-normtap (agent bc-12c2f2d9)
created: 2026-09-27T01:52Z
---
# Finding: FA3's IR disagrees with its kernel on rows whose running max is -inf at an unmasked key block

The MS plane (PR #102) is on track: FA2 exactness passes, #101 and gate (b) are running on the L40S, and the H100 was terminated at 01:46:13Z
after about 20 minutes. FA3 exactness found one disagreement, which belongs to the IR, not to the tap. You may want to route it to the IR
owners before my merge-ready handoff.

- **What differs.** FA3's online softmax guards `-inf` (`Check_inf`) only on its masked iterations: the first block, and the causal- or
  local-masked blocks. Its unmasked iterations run `fwd_step(..., check_inf = false)`. The FA3 IR (`AttnBlock_v2`) applies
  `GuardNegInfZero` on every block.
- **What it affects.** Take a row whose running max is still `-inf` at an unmasked block. That happens when every score so far is -inf, or
  when a NaN row's masked columns set its max to -inf.
  - The kernel's `max_scaled` is `-inf * scale = -inf`; the IR's is 0. Measured, see Evidence.
  - Read off the kernel source, not measured separately: for an all--inf row, the block's P (`exp2(s * scale - max_scaled)`) and its
    rescale are NaN in the kernel and 0 in the IR.
  - The default FA3 build has the same kernel behaviour; the MS tap only makes it visible.
- **Evidence.** Run `r20260927-012825-34ba` (H100, preserved).
  - Guarded FA3 record `d8c5c7e2…`: 18 of 20 cases are ok. The two that fail are `edge_rows` at hd 64 and hd 128.
  - hd 64: 16 of 684 MS words differ. hd 128: 24 of 556. Every differing word has row_max `0xFF800000` and MS `0xFF800000` (IR: 0). The
    reference evaluator agrees on its sample: 1 of 64 and 3 of 64 differ.
  - Everything else in the guarded record passes: ROW word 3, stream equal to the default build, closedness, and the negatives.
  - The default FA3 record `b9d61818…` is ok, 20 of 20.
- **FA2 has no such gap.** FA2 always guards. The FA2 L40S run `r20260927-012901-955c` has default `668baecb…` 64 of 64 and guarded
  `338c7caa…` ok: 547,438 MS words all equal the IR, with softcap 28 of 28 and all 8 edge cases ok.
- **Finite bf16 inputs don't reach it.** A row needs every score to be ±inf or NaN, so it takes overflowed or non-finite Q or K.
- **Fix options, not mine to choose.**
  - Model FA3's `Check_inf` per iteration in `AttnBlock_v2`. The FA3 statics would then need each block's masking class.
  - Or accept that FA3 exactness excludes -inf-max rows in unmasked blocks.
- **Scope.** I'm leaving the property's verdict as it is: FA3 guarded `ok: false`, with the differing words counted in
  `ms_mismatch_neg_inf_max`. #101 is FA2 and unaffected.
