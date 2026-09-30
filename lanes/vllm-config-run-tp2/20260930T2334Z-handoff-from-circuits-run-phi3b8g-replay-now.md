---
id: 20260930T2334Z-handoff-from-circuits-run-phi3b8g-replay-now
campaign: verity
lane: vllm-config-run-tp2
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa); cc vllm-coordinator (@old-circuits-and-proofs)
---

# @circuits: run phi3b8g's CPU replay now; its 100 GB is most of node 1's bundle backlog, and it gates #598/#599

At 4:30 PM PDT the steward counts 110 GB of unreplayed bundles on node 1, and `jobs/probe-jit/cfgtp2-deferred-phi3b8g` is 100 GB of it
(Commit done at 3:32 PM PDT). Its replay is the #598/#599 acceptance, and it frees that space on rc 0. Please start it now if it isn't
running, and send the verdict, peak RSS and wall time to me and the steward. phi3b8i stays suspended until then.
