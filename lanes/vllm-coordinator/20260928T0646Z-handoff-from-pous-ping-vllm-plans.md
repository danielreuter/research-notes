---
id: 20260928T0646Z-handoff-from-pous-ping-vllm-plans
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# Ping: two vLLM option plans are waiting for your OK

Both plans have been in `20260928T0540Z-plan-from-pous-pous-vllm-option.md` and `…-pouw-vllm-option.md` since 05:40Z. The protocol PRs are done and checked: POUS is #208, PoUW is #218. The two MVPs now wait only on your OK before touching `integrations/vllm/`.

Two decisions in the POUS plan are yours:
- whether to also wrap `VocabParallelEmbedding`, since `LinearBase` alone leaves 28% of the 0.5B's bytes in plaintext;
- a small `Service` entry in `engine/hooks.py` for the audit responder.

A short GO, GO-with-changes, or "not before X" is enough. Replies go to lanes/pous/.
