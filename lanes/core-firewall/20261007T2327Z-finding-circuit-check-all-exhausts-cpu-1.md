---
id: core-firewall/20261007T2327Z-finding-circuit-check-all-exhausts-cpu-1
campaign: proof-service
lane: core-firewall
kind: finding
status: open
repo: danielreuter/verity
origin: bc-8416bc72 (proofs)
---

# `check`'s `circuit-check --all` grew to 610 GiB on vy-nebius-cpu-1, twice, and the node went down both times

Two recorded checks of `cursor/core-lean-firewall-2f22` on vy-nebius-cpu-1 (755 GB, 192 cores) ended with the node:

| check | at | its session's memory | node |
|---|---|---|---|
| r20261007-210302-7fe5 (6c6b5654d) | 47 min in | 221 GiB at 21:43Z, 355 GiB at 21:47Z, 610 GiB at 21:50:19Z | journal ends 21:50:17Z; back 22:07:55Z |
| r20261007-221020-37af (b5c604de0) | 64 min in | 228 GiB at 22:48Z, 448 GiB at 22:58Z, 609-611 GiB 23:03-23:15Z | shutdown 23:15:01Z (SIGHUP, SIGTERM to the runner); back 23:17:50Z |

Memory is the run's own session scope (`resources.jsonl`, `cgroup.memory_current_bytes`), not the host's. In the second run
the growth is `circuit-check --all -q --jobs 23` (pid 9400, started 22:12:54Z as `flock-circuit-build` ended): its pool
(pid 666459, 23 workers, started 22:29:36Z) sat at about 8 GiB a worker, then from 22:55Z six workers grew to 136, 84, 80,
54, 51 and 40 GiB. Nothing bounds the pool's total: `check.py` gives circuit-check `n - n // 2` jobs whatever the memory,
and `circuit_check.checks.UNLOWERED` names only the four SHA-512 families known not to fit.

Why this tree: at `cursor/core-lean-on-t2-95d4` (3a3581e9e) circuit-check refused in seconds (`load_pins`: a sidecar
under two packages' roots read twice). The branch carries that fix (faa33d0a1, from train-prep-124), so circuit-check
now runs every target, and on a base 626 commits behind `main` most targets miss the node's circuit-check cache. A train
check that brings faa33d0a1 onto a tree whose targets are cold may do the same.

Which targets grow was not established (the report is written only at the end). The core-firewall lane ran no further
full check on the node.
