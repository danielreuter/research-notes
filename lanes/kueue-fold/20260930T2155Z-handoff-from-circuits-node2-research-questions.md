---
id: 20260930T2155Z-handoff-from-circuits-node2-research-questions
campaign: one-pool
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa); for kueue-fold and n2-commits (bc-698052e1)
---

# circuits → kueue-fold / n2-commits: each node-2 Commit names its research question; cov-g217 waits for the owner's yes

Daniel's rule (2:53 PM PDT): every overnight job has its research owner's yes and names the research question it answers. For the first
batch in `20260930T2150Z-handoff-from-circuits-node2-commits-first-batch.md`:

- **Approved (the 2:39 PM review):** the 8 Qwen2.5 #557 reruns, *"does the served biased linear (Triton + bf16 bias, `GemmBias_v2`)
  replay bit-exact for Qwen2/2.5 on sm_120?"*, and the Commit-ready Phi-3 / TinyLlama / SmolLM2-360M / Llama rows (*the sampler or
  batch path each checks*). Carry the question in each job's record (e.g. `RESEARCH_QUESTION` in the env) with the environment check.
- **`cov-g217` (the cross-node run-root check) waits for @old-circuits-and-proofs' yes** (asked 2:53 PM PDT, Slack 1790805213.401649).
  Start with the Qwen reruns; their own 460-unit replays check them. If the yes comes, run `cov-g217` next; I'll say in `lanes/kueue-fold/`.
- Nothing else goes to node 2 for circuits without a line from me.
