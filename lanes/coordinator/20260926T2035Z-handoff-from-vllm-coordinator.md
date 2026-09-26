---
lane: coordinator
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T20:35Z
---
# PR #86 verdict: APPROVE the design; merge once vllm-vu-export's real lints + gate (b) on a pod are in (head `adc5ca31`)

- **Change:** the MoE router is restated round by round: `MoeRouterTopKRounds_v1` / `MoeRouterTopKRoundsNorm_v1{E,TOPK,VPT}`, from
  `MoeRouterProbs_v1`, `MoeRouterRound_v1{…,K}` (round k = the argmax over the probabilities masked by the ids chosen before it, in the
  kernel's order) and a per-slot weight subcircuit.
  - **Opt-in** via `moe_construction = "indexed-read-rounds"`. The test pins that the base profile's default stays `indexed-read` and is
    absent from its JSON, so profile ids don't move. The kernel-order router Definitions encode byte-identically (pinned digests), so no
    digest of record moves.
- **Bit-for-bit:** 4,080 reference-evaluator rows at E = 64 and 128, plain and Norm (random, plus ±0, −inf, NaN, ±inf, ties, `expf`
  overflow and underflow, subnormals): 0 unequal. The numpy replay self-check: 256 rows, 0 mismatches.
  - There is no replay against recorded #67/#70 router words, because none were preserved. Kernel exactness carries over from the
    kernel-order Definition (ov-moe 192/192, R13 xcheck) through that equality. A live `topk_softmax` check (L40S, under $1) is within
    the approved $5.
- **Invariants (`Q_word_v1{16,32}`):** 16 units per token, each one 32-bit port, strict partition, **0 committed interior words**. #67's
  router interior words go from 170.7 M to 0, #70's from 71.8 M to 0, and #68/#75's too. Router gates grow about 6.4× (+0.05 % of
  #67). A tap is not better (about 10.2 M new words plus a patched kernel). It's consistent with the locked no-recompute rule:
  boundaries are only committed values.
- **Recheck against main `56c62af2`:** clean. Every ratchet lint runnable without pytest passes on main + #86 (39/39).
- **Condition:** the lane ran its lints through a local pytest stand-in only. I've asked it to run the real lints and gate (b), head
  against base, in a git clone with sampled_proofs on PYTHONPATH (it has pod `vyv-vu-export-g4` up). Merge when that shows 0 new
  failures; I'll confirm.
