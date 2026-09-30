---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: finding (coverage gap) · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-30T09:20Z

# Top-p sampling fails the strict word check on Llama's 128k vocabulary

**The cell:** `llama32-1b__bf16__rtxpro6000__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager`, run `r20260930-085223-cdf6`, pre-merge `2847317c`, labelled `fail`.

**What happened:**
- The Build derived in 236 s.
- `manifest build` then raised `QueryRuleViolation: Q_word_v1{X=16,W=32,R=no-recompute}: 1 violation(s): GumbelTopPTokenSelect_v2{V=128256,S=32}: too-large, 32 Call(s)` (`query/word.py` `check_calls`, from `pipeline/manifest.py` `word_check`).
- So no required-value manifest was built, and there was no Commit.

**The gap:**
- One stochastic top-p select over the full vocabulary is too large to be one word-check unit at W=32.
- Greedy cells of the same model pass: Llama-3.2-1B B1 at 460/460.
- I haven't run a check to see whether the limit scales with V. If it does, every top-p cell whose vocabulary is Llama-sized or larger fails the same way: Llama 3 (128k), Qwen2.5/Qwen3 (152k) and Gemma 2 (256k).
- The smaller-vocabulary families (TinyLlama 32k, SmolLM2 49k, Pythia 50k) may fit.

**Next:** I'll run a small-vocabulary top-p cell (SmolLM2-135M) to find where the limit sits. Deciding how to fix it (split the select into a cut, a Definition change, or another query) is yours.
