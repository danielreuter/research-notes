---
id: 20260930T2154Z-handoff-from-circuits-approved-only-with-questions
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: Daniel's rule: queue only owner-approved items, each naming its research question; no filler ("idle beats padded")

Daniel's standing rule (2:53 PM PDT): every overnight queue item has an explicit yes from circuits' research owner,
@old-circuits-and-proofs (bc-ecac3029), and every job names the research question it answers. Its 2:39 PM review is the yes for the
items it kept. **Idle beats padded.** This replaces step 5 (filler) of my 2:40 PM reorder and the ≥12 GPU-h floor: if the approved
items run out, let GPUs idle and tell me.

**Approved, with the question each job names** (put it in the item, e.g. `env.RESEARCH_QUESTION`, and in `ov.note` on its result):
1. **The 29 Commit-ready** (skip reruns of passing deployments): the question of its block below.
2. **Qwen2/2.5 on #557, ~15:** each size × B1/B8 × greedy and top-p. *Does the served biased linear (Triton + bf16 bias,
   `GemmBias_v2`) replay bit-exact for Qwen2/2.5 on sm_120?*
3. **Top-p, ~25:** each model at B1, B8, B32. *Do the top-p sampler Definitions replay bit-exact against the served sampler as the
   split schedule changes with batch?*
4. **As they unblock:** MoE (OLMoE, Qwen3-30B-A3B): *do the router and expert Definitions replay bit-exact on sm_120?* Gumbel B8
   after staging-bug's fix: *is the `splits` tap committed at B8?* Gemma-2 after coverage-defs' fix: *does the softcap/norm chain
   replay?* One 4k per model after the derive cut: *does the long-context path replay?*
5. **TP2 subset, after the GPU-less Build:** ~10 models × B1/B8 at 256/32 + OLMoE + Qwen3-30B-A3B. *Do collectives, rank splits and
   the 2-rank manifest merge replay bit-exact?*

**Not approved now:** the rest of each block (the other ~96 Qwen, the other top-p cells, the rest of the grid), and reruns of
passing deployments. If you think one of them answers a question the subsets don't, send it to me with the question; I get the owner's
yes first. Label-only unsupported cells need no GPU and stay fine.
