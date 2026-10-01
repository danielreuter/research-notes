---
id: 20261001T0102Z-order-from-compute-accounting-d7d4b0d1-rate-w1-complete
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# To the assessor bc-d7d4b0d1: rate `w1-complete/sm120` when the W1 off-pipe results land; a Grok 4.7 worker is writing the microbenchmarks (Daniel, 6:00 PM PDT)

**What Daniel ruled.** At 6:00 PM PDT Daniel replaced the GLM 5.3 plan with Grok 4.7. A fresh compute-accounting worker,
**bc-9221952f** (notes lane `pouw-w1`), writes and runs your W1 off-pipe microbenchmarks on node 2.

**What the worker measures.** Your `w1-complete/<device>` section's three unsearched areas:
- L2 atomic and TMA bulk reductions, and texture filtering;
- a SASS-only opcode inventory;
- the predication and branching rule.

The GPU work is about 30 GPU-min of preemptible 8-min chunks, and the SASS inventory runs as a `gpus=0` job.

**Its results** go to `lanes/accounting/<stamp>-report-w1-offpipe-results.md`, with an `art:` id.

**Your part:**
1. **Don't restart the coding.**
2. **If you have partial code or notes** from your 2:45 PM PDT attempt, write their paths in a reply here, so bc-9221952f can
   reuse them.
3. **When the report lands, rate `w1-complete/sm120`:** B, or the new γ consequence if an off-pipe path undercuts the 8-W1 pre-add
   floor. Update `ratings.md` and the assumptions table, and reply here with one line: the rating, and what it does to v1 (0.519%)
   and v2-hot (0.689%).
