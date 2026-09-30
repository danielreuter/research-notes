---
id: 20260930T2241Z-handoff-from-proofs-one-swap-with-gumbel
campaign: verity
lane: proofs-rows
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Owner's yes, 3:40 PM PDT: one swap of 73-sweep-shape.sh carrying hardlink + prune **and** the Gumbel unit reporting; the stage/prove split goes to backlog

The research owner (bc-8ece7cde) approved this in Slack thread `1790800227.516129`:
- **Include** the Gumbel reporting from your `MODE=sampled` summary in the same swap: `sampled_units`, `units_proved`,
  `units_not_proved`, and `units_excluded` with why, plus `fully_provable`.
- **One swap** of `73-sweep-shape.sh` in the sweep2-feed tree: shell only (no `.py`), with the old file kept as `.bak`.
  Deploy it together with the hardlink and prune step.
- **Swap soon.** The script is read at job start. The gate prove `a-llama32-1b-07b84a-p` is pending in `provers`; if it
  hasn't started when you swap, it gets the new fields, and otherwise deployment 2 onward does.
- **Don't deploy** the stage/prove split (`STAGE_ONLY`, `REQUIRE_STAGED`). With (b) stopped it's backlog, so leave it out of
  the swap. Your measurement chunk `split-prove-f1e4d147-m1` can be deleted from backfill (your own Job).
- The diff goes to `lanes/backend-sweep-2/` for PR #601, as before.
