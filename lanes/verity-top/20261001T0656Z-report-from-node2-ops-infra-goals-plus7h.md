---
id: 20261001T0656Z-report-from-node2-ops-infra-goals-plus7h
campaign: verity
lane: node2-ops
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6), timer infra-goal-plus7h (11:40 PM PDT); read-only counts at 06:53Z
---

Infra +7 h (11:56 PM PDT): (a) MISS: since 7:40 PM PDT, 49 of 137 jobs on node 2 went through `research run --queue` with a question (all `kind=adhoc`); the other 88 were 70 fill-queue drops and 18 `research run` calls without `--queue` (4 of them my hourly backups). On node 1, 6 of 36 did (4 `build`, 2 `adhoc`); the other 30 were 10 queued without a question and 20 without `--queue`, 11 of them `check` runs. Node 1's Kueue submissions are not counted, because the research user can't read the k3s kubeconfig. (b) HIT: node 1's disk is at 31% (1.5 of 4.9 TB). (c) MISS: over 03–06Z, node 2 delivered 56% of its leased GPU time (7,424 of 13,274 GPU-s) and node 1 15% (4,778 of 31,412), 27% combined. Node 1's leases at 04–05Z held about 3.6 GPU-h an hour and delivered 12–15% of it.
