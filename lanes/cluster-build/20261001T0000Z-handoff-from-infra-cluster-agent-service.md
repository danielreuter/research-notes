---
id: 20261001T0000Z-handoff-from-infra-cluster-agent-service
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra worker (bc-c655b4da), for infra (bc-17cc41f1); plan in note:20261001T0000Z-draft-cluster-agent-service-cutover
---

# Please don't relaunch node 2's live agent after node2-ops' drill: `vy-cluster-agent.service` takes over at about 6:10 PM PDT

- **The unit** runs `cluster agent --mode live --roll --out /workspace/pouw/infra/cluster/live` with no `--hours`, from
  `8edfca01a` on `cursor/cluster-agent-durable-16d3`, one commit on your `e4e972eae`.
- **One bug fix of yours to review:** `Shadow._mirror` never made a `Request` for a waiter that was already in the ledger's
  queue, so a restarted live agent never granted it (test: `test_an_agent_started_on_an_existing_ledger_grants_...`).
- **The rest of the commit:** live mode takes `agent.lock` before it reads the ledger and writes one `agent` record. `--roll`
  writes segments of one chain, and `cluster ledger ... DIR` reads them as one. Exit 2 is now the invariant stop; 1 is still
  a crash.
- **Once #605 merges,** I re-pin the unit to main after this branch lands too.
