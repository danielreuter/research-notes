---
id: 20260930T2128Z-handoff-from-infra-template-drift-and-monitors
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# kueue-fold: stop stale node-1 templates tonight, and add idle and unleased GPU monitors on node 1

Daniel called the stale 9:20 AM template "very important to prevent from happening". Until the kind registry
(`note:20260930T2128Z-handoff-from-infra-job-kinds-registry`) replaces node-local templates:
1. **Drift check:** every 15 minutes, compare node 1's `/workspace/jobs/dispatch/infra/nebius/sky/` (jobs/, submit.sh, kueue.yaml)
   against `origin/infra/nebius`. Alert on any difference in `lanes/infra/` and the dispatcher's lane. Better still, have the
   dispatcher render templates from a git checkout pinned to a commit, and record that commit on each submit. Infra refreshed
   the templates at 2:15 PM PDT (backups are `*.bak-20260930T2115Z`).
2. **Idle GPU:** tune Grafana's "pod holds a GPU at 0%" rule to under 10% busy for 5 minutes. It already routes through the alert sink
   with the owning lane from `lanes.tsv`; make sure the kind or job name is in the alert.
3. **Unleased GPU:** a GPU process on node 1 that no admitted pod owns. Compare DCGM's per-pod series, or the compute apps, against
   Kueue's admitted workloads. Alert on it.

Priority: after the Build offload and the weights staging, and before the node-1 executor. Tonight if you can.
