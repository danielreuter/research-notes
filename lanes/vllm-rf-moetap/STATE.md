# vllm-rf-moetap STATE (agent bc-2c25902d, cloud; started 2026-09-26 22:28Z)

Brief: `$STORE/internal/lane-briefs/vllm-moetap.md`. Two opt-in taps for the no-recompute partition: the MoE router softmax
(`_moe_C.topk_softmax`) and the TP vocabulary-range values (`VocabParallelEmbedding`). Cap $8 (approved 22:29Z, handoff 2231Z).

- Branch `cursor/vllm-rf-moetap-82dc` (Cursor's branch rule; the common page's fallback form), cut at `5b0835d4` = PR #92 `b21ce332`
  (contains PR #86 `fc5c5c3d`) merged with PR #90 `14ea93c6`. Merge order: #86, #90, #92, then this.
- Pods: vyv-rf-moetap-g1 (sy95m1sk4mmtm9, 1x L40S reference part, guard 90), created 22:41Z.

## Found on the base (checker of PR #92, Q_word_v1{X=16,W=32,R=no-recompute})
- `MoeRouterTopKOrdered_v1{E=64,TOPK=8,VPT=8}`: cut OK, 0 recomputes, 130 committed interior words, in canonical gate order
  max (F32Max), ex[64] (NvExpf F32Mul), rcp (F32Div), p[64] (SelectF32).
- `MoeRouterTopKOrderedNorm_v1{E=128}`: 267 = max, ex[128], rcp, p[128], sel[8] (MoeRouterPick), scale (F32Div).
- `EmbeddingShard_v1`: cut OK, 0 recomputes, 3 committed interior values = local = tok - START (I32Add, 32 b), ge = START <= tok
  (I32Le, 1 b), le = tok <= START+VS-1 (I32Le, 1 b). The brief's "three 1-bit values" is one 32-bit word plus two bits (34 b/token).
- At the pin, TP>1 CUDA runs the fused `_C.vocab_parallel_embedding` kernel, not PyTorch ops.

## Running
- r20260926-224241-1030 on g1: GPU bootstrap (B0, OLMOE) + gate (b) pins.
- r20260926-224413-f336 on g1: gate (b) base 5b0835d4 (waits for the setup run).

## Next
- Router tap: pinned topkGating + Tap, op verity_router_tap, policy router_softmax, source, ROUTER_TAP flag, exactness property.
- Vocab range: policy vocab_range, hook on _C.vocab_parallel_embedding (no kernel change), VOCAB_TAP flag, TP2 exactness.

## Open questions
- none yet

## Found-not-fixed
- none yet
