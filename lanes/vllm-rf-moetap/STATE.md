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

## Running (g2, relaunched 00:56Z on 267e5a72 after torch/nvidia wheels were pre-installed from local ranged downloads + PyPI)
- r20260927-005612-9e5d setup; r20260927-005659-23d0 router tap build + exactness (GPU 0); r20260927-005826-6fbf TP2 vocab (after router)
- r20260927-005720-ee97 partition report; r20260927-005731-9c35 gate (b) base 5b0835d4; r20260927-005757-fa4e gate (b) head 267e5a72
- Killed by me (setup stuck on download.pytorch.org at 0.35 MB/s), 00:24Z: r20260926-234303-0db7, -234338-9343, -234359-2b8d, -234437-b4d4,
  -234519-b0c0; and earlier g1 / g2 runs listed in the report.
- 267e5a72 is local only: GitHub token in the VM's git config expired at the ~00:35Z outage; push pending.

## Next
- Router tap: pinned topkGating + Tap, op verity_router_tap, policy router_softmax, source, ROUTER_TAP flag, exactness property.
- Vocab range: policy vocab_range, hook on _C.vocab_parallel_embedding (no kernel change), VOCAB_TAP flag, TP2 exactness.

## Found (changes #86's opt-in construction; surfaced in the handoff)
- #86's MoeRouterProbs max was P.F32Max (FA2 fast-math >-select with ftz); topkGating (no fast math) uses fmaxf. NaN results: registry
  F32Add/Mul/Div give x86 encodings (0x7FC00000 / 0xFFC00000), the GPU 0x7FFFFFFF. Outputs never differ (probabilities are clamped) but
  the committed max / exponentials / reciprocal would. Fixed in MoeRouterProbs only (F32Fmaxf + canonical NaN); record untouched.

## Open questions
- none

## Found-not-fixed
- none yet
