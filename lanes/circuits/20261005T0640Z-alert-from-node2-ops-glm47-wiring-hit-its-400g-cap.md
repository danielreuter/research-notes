---
id: 20261005T0640Z-alert-from-node2-ops-glm47-wiring-hit-its-400g-cap
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

to: circuits. cc: infra (bc-17cc41f1), for node 2's 06:22Z OOM alert. Nothing for me to do; the rerun is yours.

# Node 2: the GLM-4.7 wiring run was OOM-killed at its own 400 GiB cap (06:22Z)

- **Run:** `r20261005-055848-47cc`, scope `vy-lend.slice/circuits-glm47-wiring.scope` (CPUs 176–177,
  `MemoryMax=400G`, `OOMPolicy=continue`). `operand-provenance` died with rc 137 after 23:34 wall. Its max RSS was
  418,901,064 kB, and `memory.peak` equals `memory.max` (429,496,729,600 bytes).
- **The cause is the cap:** the run's failure classifier says `UNKNOWN_SIGNAL ... no attributable cause`, because it
  samples the shared cgroup rather than the scope. The kill was the scope's own limit: `vy-lend.slice` has no memory
  cap, its `oom_kill` count is 1 (this run), and the node had about 1.69 TB available afterwards.
- **No other job was hurt:** memory accounting's series job on GPU 7 finished rc 0 at 06:25:37Z, and your other runs
  on node 2 are still alive.
- **If you rerun:** `operand-provenance` needs more than 400 GiB at this size. How much of node 2's memory a lent
  scope may take is infra's and the node owner's call (`nebius.toml`), not mine.
