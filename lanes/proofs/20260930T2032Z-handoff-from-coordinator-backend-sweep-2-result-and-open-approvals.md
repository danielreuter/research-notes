---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
id: 20260930T2032Z-handoff-from-coordinator-backend-sweep-2-result-and-open-approvals
campaign: verity
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: old-circuits-and-proofs (bc-8ece7cde)
---

# backend-sweep-2 (bc-62b7c7a1) finished its task: the sweep is GPU-light. Two root-approved follow-ons are yours to assign

**Result** (as of 1:27 PM PDT):
- **The sweep:** Llama-3.2-1B's passing sm_120 config (`llama32-1b__bf16__rtxpro6000__tp1__b1__i1024__o128__mixed__greedy__bi-eager`) was cut into 2,578 shapes (`r20260930-172942-e0ce`). 182 are queued and 142 done, with no failures.
- **First shape** (the K = 2,048 GEMM coordinate, on M0's #554 prover key `4d568a3cb558b005`): accepted (`r20260930-180937-ab3f`), GPU selftest 43/43, and `gpu_proofs_match_cpu` and `gpu_paths_agree` both passed.
- **GPU fill:** node 1 GPU-busy was 15.6% over 10 minutes and 11.2% over 60 minutes; actual utilization was 1–2%.
  - Each shape's proof takes 0.08–1.0 s of GPU, but a job holds its GPU for minutes, mostly start-up.
  - The whole Llama sweep is about 2 GPU-hours of real proving. The postmortem's +25–40 GPU points assumed #101's 525 GPU-hours, which were extrapolated proving cost.
- **Still running on node 1:** the feeder (tmux `backend-sweep-2-feed`, CPUs 96–127). It pauses while `provers` has pending work, so 12–24 hours remain for Llama. The next models are set up in order: smollm2-135m (already cut), smollm2-360m, tinyllama-1.1b, qwen3-4b, gemma2-2b, phi3-mini, olmoe-1b-7b, mistral-7b (batch 8), qwen3-30b-a3b.
- **Code:** branch `cursor/backend-sweep-2-2ced` @ `18ceb459`, no PR: `backends/flock/pod/73-sweep-shape.sh`, `sweep_feed.py`, and a stage-only option in `class_statement.py` / `70-class-sweep.sh`.

**Approved by root at 12:04 PM PDT, but not started.** The worker finished before reading my 12:08 PM PDT handoff:
- **(a)** Prove the 460 sampled units of every passing vLLM deployment (58 so far): a few GPU-hours.
- **(b)** Whole-row proving for the K = 2,048 GEMM coordinate: about 14 GPU-hours, stopping once the measured cost agrees with the extrapolation within 5%. This is the one piece that actually fills GPUs.

**Your call, since new proof-remit work goes to your workers:** assign (a) and (b) to your own worker, or tell me to resume backend-sweep-2 for them; it already has the build, the ready-file path and the feeder. Also decide whether its branch becomes a PR.
