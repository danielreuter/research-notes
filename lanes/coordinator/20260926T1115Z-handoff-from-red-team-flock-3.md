---
lane: coordinator
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-26T11:15Z
---

# red-team-flock-3: attention (goal 1) GRANTED WITH CONDITIONS at NON_ZK_PROOF; 11 of 16 L40S cells checked and labelled NON_ZK_PROOF, the rest follow as they land

This note copies `lanes/flock-ir-lowering/20260926T1115Z-handoff-from-red-team-flock-3.md`. The full review is in
`lanes/red-team-flock-3/20260926T0958Z-report-red-team-flock-3.md`.

- **The grant:** `verity/flock-ir-frame/v3` on #101's `attention-head/d64-bn128/sm80-fa2-bf16` (AttentionHead_v3{T}, one
  statement per T), at PR #54 22dc6320 and 0839742b.
  - The unit netlist, the Rust tail and the composition show 0 mismatches against the IR:
    - 2.0e7 adversarial tensor-core vectors;
    - all 2^32 inputs of ex2, invsum, guard and f2fp;
    - all 1,024 captured heads and 3,024 adversarial heads.
  - The five frame-v3 additions hold. 19 prover-side, 34 load, 4 restatement and 3 T/set-confusion negatives are all
    refused.
- **Labelled NON_ZK_PROOF** (each verifier-staged file passes `cell_check.py`): T=1 art:97407c51, 2 art:a24437b6,
  3 art:1e1c2a5f, 4 art:308df7ad, 128 art:7c3c5497, 129 art:d1963e64, 130 art:73a507ee, 131 art:349645c1,
  132 art:11f80605, 256 art:b0eaffa3, 257 art:07f55572.
- **Decision-relevant for the headline (AC3):**
  - The verifier evaluates the softmax natively on public words: max, exp2, sums, rescale, rcp and the output cast. That is
    4–11% of the head's scalar ops, and all its transcendental work. So attention is "tensor-core steps proven, softmax
    checked natively". I recommend a footnote, as for RMSNorm's tail, rather than a lower count; the proof and the native
    check together are a sound statement of the whole head.
  - Each cell covers one T. A served head counts only through a cell at its T; say so for any extrapolation.
- **Hygiene (F1):** the T=1 and T=4 cells ran at 22dc6320, whose statement digest still hashes a v2 TAG. It is cosmetic.
  flock-ir-lowering is re-running both at 0839742b; I'll label the re-runs as well.
- **red-team-flock-2 is FINAL.** Per the launch, a note that I took this review is also in its lane folder.
- **Pod:** dq3xclby5ni4ic, terminated at 11:03Z after custody, about $0.32. The rest is CPU on the VM.
