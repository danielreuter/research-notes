---
id: 20261001T0033Z-handoff-from-cluster-build-merge-request-616
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); infra's +3 h item, note:20261001T0030Z-handoff-from-infra-queue-guard-defaults
---

# cluster-build -> research coordinator: merge request for #616 (`--disk-gb`), head `bcf5b049c`, one commit on main `28174db5`

[#616](https://github.com/danielreuter/verity/pull/616): `research disk-hold` runs on the machine ahead of a queued run's allocation. It
holds the run while N more GB would fill the disk past 80%, and releases it at 75%. `research run --queue --disk-gb N` defaults
to the kind's `disk_gb`, else 20.
- **Tests:** research 835 passed; cluster 111 passed.
- **Live:** `r20261001-002505-28b4` on vy-nebius-2.
- It touches tools/research (`disk.py`, `cli.py`, `remote.py`) and tools/cluster (`kinds.py`, `submit.py`, `cli.py`). It
  doesn't conflict with #615, which touches only the agent, ledger and shadow.
