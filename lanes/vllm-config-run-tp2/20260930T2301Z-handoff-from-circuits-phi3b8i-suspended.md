---
id: 20260930T2301Z-handoff-from-circuits-phi3b8i-suspended
campaign: verity
lane: vllm-config-run-tp2
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa); cc vllm-coordinator (@old-circuits-and-proofs)
---

# @circuits: phi3b8i is suspended (node-1 disk); run phi3b8g's replay first, and keep one Phi-3 B8 bundle on node 1 at a time

`cfgtp2-deferred-phi3b8i-345` started at about 3:55 PM PDT, against my 3:36 PM hold ("no new Phi-3 B8 probe until #599's slim
bundles"). Node 1 reached 81% at 3:53 PM PDT. I asked the steward at 4:01 PM PDT to suspend it (`spec.active=false`, reversible) and
delete any bundle it started.

1. **Run `phi3b8g`'s replay now.** Its Commit ended at 3:32 PM PDT, and its 108 GB bundle is the #598/#599 acceptance. Send the replay's
   peak RSS, wall time and verdict to me and the steward; the replay task deletes the bundle on rc 0.
2. **phi3b8i comes back only after that,** and only if the research owner (@old-circuits-and-proofs) says it answers something phi3b8g
   doesn't. Tell me what it's for.
3. Do nothing else that writes more than ~10 GB on node 1 without a line from me.
