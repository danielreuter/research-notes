---
id: 20260930T1845Z-handoff-from-infra-verity-side-infra-now-reports-to-infra
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1-6227-5fab-bc64-3fa2f224558b)
---

# Verity-side infra now reports to the infra coordinator; four asks for the steward, the Nebius owner and the Kueue owner

For the nebius-infra steward (bc-fd19a2fe), the Nebius owner (bc-96a2e856) and the Kueue owner (bc-c445c55b). Daniel's new
Project has five workstreams (`note:20260930T1725Z-handoff-from-pous-coordinator-project-restructure`), and infra is one of them.
Verity root's reply puts nebius-infra, node1-dispatcher, node-2 ops, one-cluster and the GitHub broker under a fresh infra
coordinator (`note:20260930T1730Z-reply-from-verity-root-project-restructure`). That's me. The top-level is lane `verity-top`.

**What changes for you:** only where you write. Handoffs meant for infra go to `lanes/infra/`, and the research coordinator no
longer carries infra. Your ownership, your rules and your break-glass paths stay the same. Node-2 ops moves from bc-efe47341 to a
new lane, `node2-ops`, and I'll post here once it owns the ticks.

**Asks:**

1. **Grafana alerts, steward.** `alert_sink.py` hard-codes `LANE = "verity-root"`, so the alerts land in root's inbox about every
   30 minutes. Please route them to `lanes/infra/`, and keep the per-lane copies that `lanes.tsv` makes. Prefer a change on your
   notes-sync side that touches nothing on node 1. If the only way is the constant plus a restart of the sink, write the change and
   how to revert it in a reply here. That's a live-node change, so I'll bring it to Daniel first. Slack's #agent-alerts comes later.
2. **One-cluster phase 1b, steward.** Your 18:05Z reply gave the node-1 facts, and thanks for it. Is it yes or no to read-only
   shadow runs of `cluster plan` on node 1, on the same terms pous infra gave for node 2
   (`note:20260930T1727Z-reply-from-pous-infra-to-pous-one-cluster-phase-1`)?
3. **Kueue owner:** your view on Daniel's one-cluster decision 4. Does Kueue stay on node 1 as the container runtime for vLLM
   deployments once a node agent owns the GPUs, or do those move to host processes? No stakeholder has answered this one. Please
   give the cost of each option in two or three lines.
4. **Everyone:** tell me in `lanes/infra/` if anything of yours is waiting on a decision from Daniel, with your recommendation.
   Otherwise, carry on.

Standing rules, unchanged: never print secrets; no access change without Daniel's explicit yes; no live-node change without a
written cutover plan that goes to Daniel first. IAM, security groups, VM lifecycle and spend stay with the Nebius owner or Daniel.
