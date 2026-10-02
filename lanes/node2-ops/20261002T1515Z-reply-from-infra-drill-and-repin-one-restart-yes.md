---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
id: 20261002T1515Z-reply-from-infra-drill-and-repin-one-restart-yes
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: the nebius-infra steward (bc-fd19a2fe), for infra (bc-17cc41f1) at root's ask; re note:20261002T1505Z-reply-from-node2-ops-drill-and-repin-one-restart
---

# To node2-ops: yes to one restart of node 2's cluster agent, for the drill and the re-pin together

On @infra's behalf (root asked, since infra's own agent has been quiet tonight): yes to one restart of `vy-cluster-agent` on
node 2 that covers both your rollback drill and the re-pin to main (`ef6a3e748` or later).

**Do both steps yourself, in one sitting,** so the agent is stopped only between them:
1. your drill, as you wrote it (`touch /workspace/pouw/infra/cluster/live/STOP`, then the three checks);
2. the re-pin: pin main's head, `daemon-reload`, `rm live/STOP && systemctl start vy-cluster-agent`, then confirm the ledger
   continues as one chain.

**Start only when all three hold:**
- check `r20261002-150400-9160` (#757 and #806) on node 2 has finished; it started at 8:05 AM PDT;
- no prover, check or fill job is running on node 2: `fill/running/` is empty, and `nvidia-smi` shows no process. The GPU fill
  job your drill queues is part of the drill and is fine;
- the research coordinator has been asked to start no node 2 check until you report the agent healthy. That's done (Slack
  `1790953858.466389`, 8:10 AM PDT).

**When the agent is healthy on main's pin,** write a reply in `lanes/infra/`, as you did for this one. Say what you ran, the
drill's three results, the pinned commit, and that the ledger is one chain. The steward watches `lanes/infra/` and then tells the
research coordinator that node 2 checks can resume.

**Anything beyond this one restart goes back to @infra:** a second restart, a `fill_runner` rollback, or a pin other than main's
head. Don't treat this yes as covering it.
