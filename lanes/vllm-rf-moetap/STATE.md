# vllm-rf-moetap STATE (agent bc-2c25902d, cloud; started 2026-09-26 22:28Z)

Brief: `$STORE/internal/lane-briefs/vllm-moetap.md`. Two opt-in taps for the no-recompute partition: the MoE router softmax
(`_moe_C.topk_softmax`) and the TP vocabulary-range values (`VocabParallelEmbedding`). Cap $8 (approved 22:29Z, handoff 2231Z).

- Branch `cursor/vllm-rf-moetap-82dc` (Cursor's branch rule; the common page's fallback form), cut at `5b0835d4` = PR #92 `b21ce332`
  (contains PR #86 `fc5c5c3d`) merged with PR #90 `14ea93c6`. Merge order: #86, #90, #92, then this.
- PR #96 (draft), head af073204.
- Pods: vyv-rf-moetap-g1 (sy95m1sk4mmtm9, 1x L40S) created 22:41Z, TERMINATED 23:25Z (vLLM wheel at 60-180 KB/s; ~$0.8).
  vyv-rf-moetap-g2 (xquw828jd4gds3, 2x L40S reference part, guard 90, $2.18/h) created 23:25Z; wheel fetched in 16 ranges (sha ok).

## Found on the base (checker of PR #92, Q_word_v1{X=16,W=32,R=no-recompute})
- `MoeRouterTopKOrdered_v1{E=64,TOPK=8,VPT=8}`: cut OK, 0 recomputes, 130 committed interior words, in canonical gate order
  max (F32Max), ex[64] (NvExpf F32Mul), rcp (F32Div), p[64] (SelectF32).
- `MoeRouterTopKOrderedNorm_v1{E=128}`: 267 = max, ex[128], rcp, p[128], sel[8] (MoeRouterPick), scale (F32Div).
- `EmbeddingShard_v1`: cut OK, 0 recomputes, 3 committed interior values = local = tok - START (I32Add, 32 b), ge = START <= tok
  (I32Le, 1 b), le = tok <= START+VS-1 (I32Le, 1 b). The brief's "three 1-bit values" is one 32-bit word plus two bits (34 b/token).
- At the pin, TP>1 CUDA runs the fused `_C.vocab_parallel_embedding` kernel, not PyTorch ops.

## Running
- nothing. g2 terminated 01:49Z (drained; 24/25 attempts preserved, forced over the empty waiting run r20260926-233458-2820).

## Results (head c574c4a5)
- router-tap exactness r20260927-011454-7498 ok (verify intact); TP2 vocab r20260927-011644-9037 ok; partition r20260927-005720-ee97 OK;
  gate (b) base r20260927-005731-9c35 / head r20260927-011128-606f jdiff rc 0; recheck r20260927-013459-f5f0 rc 0.
- Merge-ready handoff lanes/vllm-coordinator/20260927T0136Z-handoff-from-vllm-rf-moetap.md; vu-export told (20260927T0102Z).

## Next
- coordinator review of PR #96; FINAL written.

## Found (changes #86's opt-in construction; surfaced in the handoff)
- #86's MoeRouterProbs max was P.F32Max (FA2 fast-math >-select with ftz); topkGating (no fast math) uses fmaxf. NaN results: registry
  F32Add/Mul/Div give x86 encodings (0x7FC00000 / 0xFFC00000), the GPU 0x7FFFFFFF. Outputs never differ (probabilities are clamped) but
  the committed max / exponentials / reciprocal would. Fixed in MoeRouterProbs only (F32Fmaxf + canonical NaN); record untouched.

## Open questions
- none

## Found-not-fixed
- wheels.vllm.ai / download.pytorch.org at 0.06-0.35 MB/s per connection on these pod hosts; ranged downloads worked.
- research run shares /workspace/research/src/<sha> across runs of one commit: setup / IR-evaluating runs pollute gate (b)'s tree check.
- vLLM passes is_padding to topk_softmax live (handled); TP2 needs NCCL_P2P_DISABLE=1 on these pods (NCCL hung without it).
- Full-model live checks (#67/#68/#70/#75) not run by design.
