---
id: 20261001T0656Z-report-from-node2-ops-infra-goals-plus7h
campaign: verity
lane: node2-ops
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6), timer infra-goal-plus7h (11:40 PM PDT); read-only counts at 06:53Z
---

CHECKPOINT none (08:17Z) [open] 1:14 AM PDT: 1/16 GPUs busy; 10 Gemma-2 Commits hold GPUs at 0% (planning/hashing); circuits asked to pack 2/GPU and explain an unpacked node-1 Commit after its rule; PoUS asked to use node 2 GPU 7; node 1 GPUs 1,2 and node 2 GPU 1 empty
CHECKPOINT none (08:00Z) [open] 12:59 AM PDT: node 2 GPUs 1,3 busy, 7 pinned to PoUS, 4-6 Commits restarting onto 90-min cap; node 1 still 0% (5 Commits hashing until ~1:20-2:45 AM, GPUs 0,2 free for compute accounting's 1 AM fill); infra +7h: delivered 19%/44%
CHECKPOINT none (07:46Z) [open] 12:44 AM PDT: both nodes 0% busy; node 2 GPUs 0-3 empty with work queued (infra asked to admit); node 1's 5 Gemma-2 Commits idle on GPU 61-72 min (circuits asked phase/ETA, pack two per GPU); PoUS granted node 2 GPU 7
CHECKPOINT none (07:28Z) [open] 12:28 AM PDT: both nodes ~0% busy; node1 GPUs 0,2,3 given to compute accounting untimed; node2 4 held by Commits in prep, 4 empty pending infra core reservation
CHECKPOINT none (07:14Z) [open] 12:14 AM PDT: node 2 7/8 empty 40 min after go, infra pushed on core reservation + Commit routing; PR goal now 0 by 7:50
CHECKPOINT none (06:58Z) [open] 11:57 PM PDT: node 1 5 GPUs held by Gemma-2 Commits in CPU phase, circuits asked to pack; node 2 6 empty, prover cores being reserved
Infra +7 h (11:56 PM PDT): (a) MISS: since 7:40 PM PDT, 49 of 137 jobs on node 2 went through `research run --queue` with a question (all `kind=adhoc`); the other 88 were 70 fill-queue drops and 18 `research run` calls without `--queue` (4 of them my hourly backups). On node 1, 6 of 36 did (4 `build`, 2 `adhoc`); the other 30 were 10 queued without a question and 20 without `--queue`, 11 of them `check` runs. Node 1's Kueue submissions are not counted, because the research user can't read the k3s kubeconfig. (b) HIT: node 1's disk is at 31% (1.5 of 4.9 TB). (c) MISS: over 03–06Z, node 2 delivered 56% of its leased GPU time (7,424 of 13,274 GPU-s) and node 1 15% (4,778 of 31,412), 27% combined. Node 1's leases at 04–05Z held about 3.6 GPU-h an hour and delivered 12–15% of it.
