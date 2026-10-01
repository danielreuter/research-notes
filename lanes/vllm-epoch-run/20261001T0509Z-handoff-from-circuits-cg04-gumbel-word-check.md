---
id: 20261001T0509Z-handoff-from-circuits-cg04-gumbel-word-check
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: cov-cg04 (Gemma-2 B1 Gumbel 256/32) fails closed at the Build's word check. Label it a fail with this cause

- **The run:** `r20261001-043541-8b30`, rc 13. The manifest's word check raised `QueryRuleViolation: Q_word_v1{X=16,W=32,R=no-recompute}: 1
  violation(s): GumbelTopPTokenSelect_v2{V=256000,S=32}: too-large, 32 Call(s) under …` (the log truncates the rest). Gemma-2's 256k vocab
  makes the Gumbel TokenSelect Call too wide for W=32.
- **The fail is specific to B1:** cov-cg14 (B16 Gumbel 256/32) built fine, and Gumbel at B1 passes for vocabs up to 152k.
- **What to do:**
  - Label cg04 `fail` with the cause "word check: GumbelTopPTokenSelect_v2 V=256000 too large for Q_word W=32".
  - Expect cg03 (B1 i1024 Gumbel) to fail the same way.
  - Don't rerun either until a Definition fix lands. This one is circuits', a served-sampler Definition, and it's on circuits' backlog.
