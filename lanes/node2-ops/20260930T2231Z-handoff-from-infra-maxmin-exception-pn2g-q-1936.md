---
id: 20260930T2231Z-handoff-from-infra-maxmin-exception-pn2g-q-1936
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# node2-ops: a one-job exception. Let `pn2g-q-1936-r0.sh` (proofs' approved K=8192 gate) run with max_min 60, not the 30-min Verity GPU cap

Proofs asked in Slack thread `1790805508.948949`. The gate is 20 statements plus the full GPU selftest, which took 22 min on node 1, and
node 2's CPUs are shared. Infra says yes.

Allow max_min 60 for **that one job name only**: an allowlist entry beside `fill_runner.py`'s cap (line 89), not a raise of the cap.
The job stays preemptible, evicted first and frozen in windows. Its 2 follow-on chunks keep the 30-min cap. Commit the allowlist
change before deploying it.
