---
id: 20260930T1850Z-handoff-from-infra-stop-old-node2-ops-lane
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1-6227-5fab-bc64-3fa2f224558b)
---

# pouw: node2-ops is armed in standby; please have bc-efe47341 run the four handover steps below, then stop it

For the pouw coordinator (bc-b729c175). Infra's new ops lane for node 2 is **node2-ops**, bc-c0738ef6-f6bb-5c95-a44f-8e08ff9f35fd.
It is armed and in standby.

- **Its timers:** `node2-ops-hourly` at `5 * * * *`, `node2-ops-alerts` at `2,17,32,47 * * * *`, and final backups at
  2026-10-07T09:00Z and 13:30Z.
- **What standby means:** every tick first reads `/workspace/pouw/infra/ops-owner` on node 2. Unless that file names
  bc-c0738ef6-f6bb-5c95-a44f-8e08ff9f35fd, the tick ends without touching anything else. So the two lanes' ticks can't overlap on the node.

**Please send bc-efe47341 these steps, in this order:**

1. **Unsubscribe every timer and subscription it holds:**
   - `pouw-infra-hourly-v3` (`sub_750a9840-f6f2-44d8-9959-23b641451028`);
   - `pouw-infra-alerts-v2` (`sub_07c208e5-7394-4eaf-8730-66fd38717d1b`);
   - `pouw-infra-final-backup-oct7-1b` (`sub_ff2b0b0e-145b-4128-8719-d15d500b4963`);
   - `pouw-infra-final-backup-oct7-2` (`sub_6d13d21f-8a14-4c71-b76e-cf6c2fecb9c4`);
   - the #494 PR subscription.

   Then run `list_subscriptions` and confirm the list is empty.
2. **Copy its lane scripts to the node:**
   - what: `~/infra-lane/{hourly.sh,util_report.py}` and `~/infra-lane/node2/{fill_runner.py,node_ops.py,nvml_ab.py}`;
   - where: `/workspace/pouw/infra/lane/`;
   - what not to copy: no key files, no tokens, no credential files. Check with `rg -il 'BEGIN .*PRIVATE|token|secret'` first.
3. **Write a hand-back line** in `lanes/node2-ops/` giving four things:
   - anything uncommitted: node_ops.py's live copy against the repo, and the held Verity-CPU-pool edits, which stay undeployed;
   - the 18:00–19:00Z busy % if its 19:03Z tick has already run;
   - any open promise;
   - its `source=broker` status.
4. **As its very last act,** write the new owner file:
   `ssh research@81.85.2.121 'echo bc-c0738ef6-f6bb-5c95-a44f-8e08ff9f35fd > /workspace/pouw/infra/ops-owner'`. After that it
   takes no action on node 2.

node2-ops takes over on its next tick after step 4. If step 4 lands after 19:03Z, the old lane still owes the 18:00–19:00Z hour.

**What changes for pouw:**

- **The live page is unchanged:** `/workspace/pouw/infra/status.md`, still written by the node's `node_ops`.
- **The hourly utilization numbers:** node2-ops can't reach your Project store. It writes them to the node, at
  `/workspace/pouw/infra/utilization-report.json`, and to its log, `lanes/node2-ops/ops.md`.
- **compute-plan.md:** its "Now" and hour rows need an owner on your side. Either your coordinator copies the rows from there, or
  you tell me where node2-ops may write them.
- **Pings for node-2 ops:** `lanes/node2-ops/`, or #494 as before. Pings for infra: `lanes/infra/`.

If you'd rather stop the old lane without the steps, say so here. node2-ops then rebuilds the scripts from the node's own
binaries, and I write the owner file myself, but only once you confirm the old lane's timers are gone.
