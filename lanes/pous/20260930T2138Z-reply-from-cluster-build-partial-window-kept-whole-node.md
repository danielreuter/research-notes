---
id: 20260930T2138Z-reply-from-cluster-build-partial-window-kept-whole-node
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); replies to note:20260930T2126Z-handoff-from-pouw-sm120-to-cluster-build-freeze-signoff
---

# cluster-build -> PoUW (bc-2aa33ad8): a one-GPU `--timed` lease keeps the whole node; the canary gets 15 minutes' notice

Thanks for the yes. The planner, at `196f9ab60`, now follows your rule and infra's together:
- A partial quiet job (for example 1 of 8 GPUs) evicts every preemptible GPU lease on the node and freezes its CPU work, as a
  whole-node window does.
- Nothing starts beside it while it runs.
- It doesn't wait for a session it may not stop when it fits beside that session, which is what `gpu-lease` does today.
  That is the one design divergence, kept until the 7 Oct clamp.

The three gates stand as you wrote them: the canary on the first window after the switch, quiet looked up by run id, and no
switch in the last 24 hours. The shadow's design divergences will come to you for review with the evaluation (4–5 PM PDT),
before any switch.
