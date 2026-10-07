---
id: 20261007T1010Z-alert-from-node2-ops-n2-custody-timer-inactive
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

to: infra (bc-17cc41f1). One decision for you; the rest is done.

**Decision: node 2's `n2-custody.timer` is inactive.** Nothing has pushed node 2's local-only runs home since the stopgap loop
stopped at 16:00Z on 4 Oct, and nothing alerted. By the 09:00Z final backup, 65 ended runs were held only on node 2. Whether to
start the timer (or wire its last-push age into an alert) is yours. Runs that end from now until the node stops at 14:55Z will wait
again.

**Done in final backup 1:** I ran `n2_custody.sh` rounds by hand on node 2 from 09:06Z to 09:57Z. 66 runs: 61 are on R2 with their run
records, and 5 were held. Four had files written after their run record was taken (three interrupted `check` runs' `lean-audit.log`,
and one network accounting run's last outputs); the fifth (`r20261003-174723-7ea5`, a cancelled `check`) has an attempt on R2 that
names no run record. I preserved each residue as `evidence/v1` and moved the markers to `pushed/`; `held/` is empty. Ids and
details: `note:node2-ops-ops` (10:10Z line).

**Small mismatch in `n2_custody.sh`:** its hold text for an attempt without a run record says to label it `custody waived`, but
`research data label` refuses `custody` (not in the vocabulary). I used `note` instead.

Also left out of the final backup, for compute accounting and Daniel: the two 3 Oct `mvp-e2e/passes` (74 + 73 GB, no backup, no
retention file), which wait on the same upload question as the 6 Oct pass (`note:20261007T0915Z-report-node2-ops-final-lessons`).
