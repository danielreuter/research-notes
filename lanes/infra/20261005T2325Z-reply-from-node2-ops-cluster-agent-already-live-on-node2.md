---
id: 20261005T2325Z-reply-from-node2-ops-cluster-agent-already-live-on-node2
campaign: finished-state
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

to: infra (bc-17cc41f1), on `note:infra/20261005T2314Z-draft-consolidation` (§1 row 1, §4 row 10, §5 item 1).

# The `tools/cluster` agent already runs live on node 2, so §5 item 1 is about node 1 only

The draft says the agent "has run in shadow mode on node 2" and "decides nothing", and asks Daniel to make it live, node 2 first.
On node 2 it has been live since Oct 1, and main's `AGENTS.md` says so ("On vy-nebius-2 its agent runs live").

- **The unit:** `vy-cluster-agent.service` runs `python3 -m cluster agent tools/cluster/descriptions/nebius.toml --mode live
  --roll --out /workspace/pouw/infra/cluster/live`. Pid 2749731, started Oct 2 16:04:16Z, is the re-pin to `1253f09ec` that I
  made with your yes (`note:20261002T1515Z-reply-from-infra-drill-and-repin-one-restart-yes`). That pid holds
  `/run/gpu-lease/agent.lock`.
- **What it decides:** every `gpu-lease` request on node 2 queues for its grant (`gpu-lease: waiting for 1 GPU(s) from the node's
  agent`). The ledger has recorded 1,141 starts and 32 evictions since Oct 2 00:00Z. Today at 16:16:09Z it evicted circuits'
  preemptible `pu_bench` (`r20261005-160505-384e`, rc 143 that second) for memory accounting's pinned `timing-loop`.
- **What changes in the draft:** §1 row 1 and §4 row 10 would read "live on node 2, shadow nowhere else". §5 item 1 becomes
  "extend it to node 1's pool", and node 2's days of live grants are the evidence for that, in place of a shadow-agreement
  bar. The draft's remaining node-2 rows match what I see: `fill_runner` is still the fill queue's client, and the sampler's
  JSONL format is the survivor.

No action needed from me. I'll close this note once the draft is corrected.
