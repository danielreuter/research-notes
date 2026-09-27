---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Lane brief: vllm-rf-moetap (the router-softmax tap and the TP vocabulary-range mask, opt-in)

**Launch as** a Cursor cloud agent in `danielreuter/verity`, base branch `main`, with this prompt:

> You are vLLM refactor lane `vllm-rf-moetap`: two of the taps the no-recompute partition needs. First read
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md` and do its section 1. Then read
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-cloud-common.md` (it overrides the setup page for vLLM
> lanes: the no-waiting rule, the gate (b) git-clone procedure, `sampled_proofs` on PYTHONPATH, and **the partition checker with 0 recomputes
> in every review**), then your brief `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-moetap.md`. Write your
> first checkpoint (`research notes checkpoint vllm-rf-moetap open "..."`) within 10 minutes.

## Context
The rule (Daniel, locked; `$STORE/docs/project-context.md`): no recompute. Every gate is in exactly one unit, and every value crossing a unit
boundary is committed. `$STORE/docs/fine-query-plan.md`, "The tap list", names the values serving doesn't commit yet. Norm scales are done
(PR #90), and the guarded max goes to lane normtap. Yours:
1. **The router softmax**, f32, 2E + 2 per token (the E exponentials, the E probabilities, the max and the reciprocal, plus the extra values for
   Qwen3's renormalization), in vLLM's `_moe_C.topk_softmax` (`topkGatingSoftmax`). These are the values the committed-softmax router (PR #86,
   `MoeRouterTopKOrdered_v1`, `moe_construction = "indexed-read-ordered"`) commits. Rows #67, #68, #70 and #75.
2. **The vocabulary-range mask**: three 1-bit values per token on the TP rows' `EmbeddingShard_v1`, in vLLM's `VocabParallelEmbedding`.
   Rows #70 and #75.

## Requirements
- **Opt-in, off the record path:** one config flag each (like `NORM_TAP`). With it off, every Program, manifest, root, leaf id and verdict is
  unchanged.
- **Router tap:** a separately built tapped op (PR #90's norm-tap pattern: sha-pinned source from vLLM `d9105ea80` + a `Tap` template
  parameter), swapped in through `engine/hooks.py`. **Exactness property:** the router outputs (ids and weights) are bit-identical to the
  installed `topk_softmax`, every token's 2E + 2 values are written, and they equal the ordered router's committed values in the IR bit for
  bit. E = 64 (OLMoE, top-8) and E = 128 (Qwen3-30B, with renormalization), edge cases (ties, −inf, NaN).
- **Vocabulary mask:** vLLM computes it in PyTorch ops, so check whether a hook in `engine/hooks.py` can capture the exact bits without a
  kernel change (preferred). Exactness: the captured mask equals the IR's `EmbeddingShard_v1` mask on every token, per rank.
- **Partition checker** on the affected Definitions (the ordered router, `EmbeddingShard_v1`) with these values acquired: strict partition,
  committed boundaries, width, **0 recomputed gates**. Include the output in the merge-ready handoff.
- **Stacking:** PR #86 must merge first (the router construction). Branch from main once it's in, or from #86's branch.
- **Don't** touch the query of record, the re-baseline epoch, or `GumbelTopPTokenSelect` (vu-export is fixing the sampler).

## GPU: none until the coordinator confirms the root's approval
Code and CPU tests come first. **Create no pod until a coordinator handoff in your notes dir says the estimate is approved.** Estimate:
- the router tap on one L40S, about 2.5 h: build, exactness at E = 64/128 on synthetic logits, and a small live check. About $3. No full MoE row
  (#67/#68 need ≥ 256 GB and about 5 h).
- the vocabulary mask on a 2x L40S, about 1–1.5 h: a small TP2 model through vLLM, mask captured and compared per rank. About $3. No full #70/#75
  row.
- gate (b) on a small CPU pod, about $1.
- **Lane cap: $8.** Stop and ask before passing it.

## Finish
A merge-ready handoff to `lanes/vllm-coordinator/` (exactness, the checker output, gate (b)), READY.md, pods terminated, FINAL.
