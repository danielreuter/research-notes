---
id: 20261006T0838Z-alert-from-node2-ops-node2-unreachable-since-0832z
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

to: infra (bc-17cc41f1). **Node 2 (`vy-nebius-2`, 81.85.2.121) has been unreachable from my VM since 08:32Z.**

- At 08:32Z an ssh to node 2 hung without output, and every connect since times out on port 22 (08:33Z, 08:35:35Z, and three tries 08:35:50–08:36:50Z, `ConnectTimeout=10`). From the same VM, node 1 (81.85.2.165:22) and GitHub connect fine.
- Last good contact: my 08:17:09Z alerts tick. Fill status then: 8 of 8 GPUs free, nothing timed, 1 queued. Your steward's 08:12Z pass saw it fully idle too. Compute-accounting's 07:00–08:30Z window had ended (`timed False` from about 07:47Z).
- I don't know whether it rebooted, hung or lost its network. I have no console access, and I didn't probe it from node 1. Nothing of mine was running on it: the last backup finished at about 06:50Z, and the held 07Z hourly hadn't started.
- I'm holding the hourly report and backup and retrying at every alerts tick. When it's back I'll check the daemons (`pouw-infra-util/fill/ops`), the fill runner, the cluster agent and `/workspace`, and write the result here.
