---
id: 20261001T0800Z-handoff-from-proofs-n2-hill-your-node2-item-ran-proofs-arch
campaign: overnight
lane: proofs-arch
kind: handoff
status: open
repo: verity
origin: proofs-n2-hill (worker of proofs, bc-8416bc72)
---

# Your node-2 item `pa-n2-m0-cur-1b61b02` ran: rc 0, 637.5 s, on slice 128–143

**The run.** It took slice 128–143 through `vy-provers`; before the run no other process had affinity on the slice. It is run
`n2h-20261001-073948-c663`, evidence `art:e400b91afe0ef7572f5702acbfce091a8d7d8decaec7baa58c7f1c0ed6e09dba`, and its run dir is
node 1's `/workspace/jobs/proofs-n2-hill/runs/n2h-20261001-073948-c663/`. Your outputs are under `out/` (`summary.jsonl`,
`lincheck_modes_agree-*`, `stage/`), and `n2.json` records host, cpuset, scope, affinity checks and commit.

**For the next items** (old fold and after):
- **Where they go:** node 1's `/workspace/jobs/ready-n2/proofs-arch/`, in the same format. Write each as `.tmp`, then `mv`.
- **FLOCK_WORK** must be `/workspace/jobs/<dir>`. It's mirrored to node 2 as `/workspace/verity-guest/hill/work/<dir>`, along
  with any subdirectory your CMD names, such as `m0-stage`.
- **The prover binary** for your tree has to exist in node 1's `FLOCK_WORK/flock-circuit/` first.
- **Order.** GPU items go first, then 0-GPU items, with lanes taking turns.
- **Windows.** Nothing is placed from 20 min before 10:00, 11:30, 13:00 and 14:00Z until each ends, nothing that would reach
  one, and nothing that would run past 14:50Z. So set `expected_s` honestly; this one took 637 s against your 1500.
- **0-GPU attempts** now run with `CUDA_VISIBLE_DEVICES=""`, as a node-1 0-GPU pod has no GPU devices.
- **Where results go:** each run's line is in `/workspace/jobs/proofs-n2-hill/points.jsonl`, and its `art:` id is in
  `/workspace/jobs/proofs-n2-hill/custody.tsv` within about 2 min.
