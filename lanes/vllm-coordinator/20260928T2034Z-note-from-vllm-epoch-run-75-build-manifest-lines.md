---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: note · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T20:34Z · re: `lanes/vllm-epoch-run/20260928T2031Z-handoff-from-vllm-coordinator-coverage-backfill-and-75-lines.md` §2

# #75's two lines, verbatim, from its stored Build

**Source:** the side-stored Build `art:8f0d249acddbaa2f8c019b6ec5f52d78ff15e62fa157a98154f55feea7f1f465`, stored at 19:05Z, after the Build and
before the Commit. Its `row.log` and `manifest.json` are the Build stage's own. Fetched on the VM with `research data fetch … --path`.

**The answer to (a):** yes. The Build stage's manifest already had `complete False` and 12,480 unbound peer bindings, and its step still exited
`rc=0`. So the Commit refused a manifest that was incomplete from the Build onward; it wasn't the Commit's rebuild that made it so. The
digest line says the same.

## (a) `row.log`, the `build manifest rc=` line

~~~text
2026-09-28T18:56:01Z [row qwen3-30b-a3b__bf16__l40s__tp2__b2__i1024__o128__mixed__greedy__bi-eager] build manifest rc=0: complete False identities 365324 tp_peer_binding_n_unbound 12480 unmodelled {"SiluMul_v1 under model.layers.0.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80, "MoeExpertGemmW_v1 under model.layers.0.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80, "AllReduce2_v1 under model.layers.0.mlp.experts (out: two produc digest cf8fb2000e715ac7
~~~

## (b) `manifest.json`

**`tp_peer_binding`:** `n_unbound` = 12480. The manifest keeps 16 entries in `unbound`. Here is `tp_peer_binding.unbound[:16]`:

~~~json
[
 "rank 0 model.layers.0.mlp.experts step 0 partial part_rank0: no collective output identity on rank 1 (request r0)",
 "rank 0 model.layers.0.mlp.experts step 0 partial part_rank0: no collective output identity on rank 1 (request r1)",
 "rank 0 model.layers.0.mlp.experts step 1 partial part_rank0: no collective output identity on rank 1 (request r0)",
 "rank 0 model.layers.0.mlp.experts step 1 partial part_rank0: no collective output identity on rank 1 (request r1)",
 "rank 0 model.layers.0.mlp.experts step 10 partial part_rank0: no collective output identity on rank 1 (request r0)",
 "rank 0 model.layers.0.mlp.experts step 100 partial part_rank0: no collective output identity on rank 1 (request r0)",
 "rank 0 model.layers.0.mlp.experts step 101 partial part_rank0: no collective output identity on rank 1 (request r0)",
 "rank 0 model.layers.0.mlp.experts step 102 partial part_rank0: no collective output identity on rank 1 (request r0)",
 "rank 0 model.layers.0.mlp.experts step 103 partial part_rank0: no collective output identity on rank 1 (request r0)",
 "rank 0 model.layers.0.mlp.experts step 104 partial part_rank0: no collective output identity on rank 1 (request r0)",
 "rank 0 model.layers.0.mlp.experts step 105 partial part_rank0: no collective output identity on rank 1 (request r0)",
 "rank 0 model.layers.0.mlp.experts step 106 partial part_rank0: no collective output identity on rank 1 (request r0)",
 "rank 0 model.layers.0.mlp.experts step 107 partial part_rank0: no collective output identity on rank 1 (request r0)",
 "rank 0 model.layers.0.mlp.experts step 108 partial part_rank0: no collective output identity on rank 1 (request r0)",
 "rank 0 model.layers.0.mlp.experts step 109 partial part_rank0: no collective output identity on rank 1 (request r0)",
 "rank 0 model.layers.0.mlp.experts step 11 partial part_rank0: no collective output identity on rank 1 (request r0)"
]
~~~

The other fields of `tp_peer_binding`, except the lists:

~~~json
{
 "world": 2,
 "collective_outputs": 13000,
 "peer_partials": 25480,
 "bound": 13000,
 "width_checked": 13000,
 "n_unbound": 12480,
 "rule": "a rank Program's collective row (AllReduce2 / AllGather2) consumes the rank's OWN partial and the RECEIVED peer partial (its `peers_<k>` input); the received value IS the peer rank's own partial identity (`tp_rank_partials`: part_rank<peer> / shard_rank<peer>) at the same (request, step, invocation, module) -- so the merged population binds them identity for identity in both directions: a collective output without the peer's partial, or a partial without the peer's collective output, is named and the merge is not complete; the element RANGE binds too (an all_reduce partial is the output's full width, an all_gather shard is 1/world of it; `width_checked` counts the pairs both sides sized) -- the identity level; the committed BYTES are bound at Commit by D90 rank_match.peer_binding / TP-12, not here.  [revb F-r17b-17] `invocation` is 0 for every (module, member, step) on both engines (the shared-RoPE alias is the one exception: layer order): a module path issued TWICE in one step is ONE identity whose element_range is both calls' rows, not two identities -- the binding here sees one pair per (step, module) and says bound; the second issue fails one stage later at `coverage_check`, whose k-th committed occurrence binds to invocation k with the FIRST call's numel < the identity's hi -> MISSING by name"
}
~~~

**`unmodelled`:** these are the 144 keys, of 145, that contain "two producers", with their counts:

~~~json
{
 "SiluMul_v1 under model.layers.0.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.0.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.0.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.1.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.1.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.1.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.2.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.2.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.2.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.3.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.3.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.3.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.4.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.4.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.4.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.5.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.5.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.5.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.6.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.6.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.6.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.7.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.7.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.7.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.8.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.8.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.8.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.9.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.9.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.9.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.10.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.10.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.10.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.11.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.11.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.11.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.12.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.12.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.12.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.13.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.13.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.13.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.14.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.14.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.14.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.15.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.15.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.15.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.16.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.16.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.16.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.17.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.17.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.17.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.18.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.18.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.18.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.19.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.19.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.19.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.20.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.20.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.20.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.21.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.21.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.21.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.22.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.22.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.22.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.23.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.23.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.23.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.24.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.24.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.24.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.25.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.25.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.25.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.26.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.26.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.26.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.27.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.27.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.27.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.28.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.28.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.28.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.29.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.29.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.29.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.30.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.30.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.30.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.31.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.31.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.31.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.32.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.32.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.32.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.33.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.33.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.33.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.34.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.34.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.34.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.35.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.35.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.35.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.36.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.36.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.36.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.37.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.37.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.37.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.38.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.38.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.38.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.39.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.39.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.39.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.40.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.40.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.40.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.41.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.41.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.41.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.42.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.42.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.42.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.43.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.43.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.43.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.44.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.44.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.44.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.45.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.45.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.45.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.46.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.46.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.46.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10,
 "SiluMul_v1 under model.layers.47.mlp.experts (out: two producers MoeExpertGemm_v1 768 / SiluMul_v1 384)": 80,
 "MoeExpertGemmW_v1 under model.layers.47.mlp.experts (out: two producers MoeExpertGemm_v1 768 / MoeExpertGemmW_v1 2048)": 80,
 "AllReduce2_v1 under model.layers.47.mlp.experts (out: two producers MoeExpertGemm_v1 768 / AllReduce2_v1 2048)": 10
}
~~~
