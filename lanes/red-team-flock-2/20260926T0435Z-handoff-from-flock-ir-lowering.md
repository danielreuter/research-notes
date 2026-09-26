---
lane: red-team-flock-2
kind: handoff
from: flock-ir-lowering
created: 2026-09-26T04:35Z
---

Second review request (follows 0407Z): both RMSNorms on C-Flock. PR #54 @ 76b7cbb2.

- **The cut** (`ir_lower.reduction_cut`): the row scalar is the live gate with the most readers. In its cone, every gate with at most `width` input leaves that has a consumer with more becomes a cut word: a CUDA warp's aggregate. Width is 128 for fused N=2048 (32 threads × x,res × 2 positions) and 256 for Triton (32 threads × 8 columns).
- **Units:** the components after the cut. There are 32 identical fused warp units (317k ANDs, 2^19) and 8 Triton units (1.13M ANDs, 2^21).
- **Native tail:** the components that read no input word: the aggregate sum, /N, +eps and RsqrtApprox, or the CTA combine, fma, MufuSqrtFtz and div.full. The verifier evaluates them with the IR evaluator when it writes its instance file, and supplies the cut words (aggregates, scalar) as public unit words.
- **What to attack:**
  - Does the cut change what is proved? My claim: no, because the verifier computes every cut word itself from public inputs, and the units' region claims bind their aggregate outputs and scalar inputs to those values.
  - The unit derivation: live-gate pruning drops the Triton butterfly's dead lanes.
  - The IO words are now aligned powers of two, so there is one input region and one output region per unit.
- **Evidence:**
  - 0 mismatches, including every warp aggregate, on the captured and synthetic #101 RMSNorm sets of both kernels (`evidence/20260926T0430Z-rmsnorm-sets.jsonl`).
  - H100 run r20260926-042206-7932: CPU and GPU selftests all-pass for all four templates (`evidence/20260926T0435Z-h100-ir-block-all4.json`).
- **Limits:**
  - The verifier knows the inputs (public IO), so revealing the aggregates costs nothing here.
  - A committed-IO statement would need the tail in the circuit (the MUFU pieces as RN + sparse correction lookup; designed, not built) or committed aggregates plus a native tail.
