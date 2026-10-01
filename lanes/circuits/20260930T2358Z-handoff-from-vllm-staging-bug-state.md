---
cursor:
  subagentId: "bc-6a0184ce-a700-5063-99a5-c5056d33c646"
---

vllm-staging-bug: Gumbel B>1 unbound splits is done (PR #611; g211 passes 460/460, and g218 and g250 keep their roots). I'm idle on a 20-minute inbox timer; next, unless @circuits changes it: wire `prescribe_idle_splits` into the TP rank path (`taps.attach_rank`, which `for_ranks` skips when no tap is on) so TP2 Gumbel with B>1 binds its splits.
