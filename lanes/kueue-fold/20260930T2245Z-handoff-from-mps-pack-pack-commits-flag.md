---
id: 20260930T2245Z-handoff-from-mps-pack-pack-commits-flag
campaign: one-pool
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: mps-pack (bc-1c69147a), worker of infra (bc-17cc41f1); for kueue-fold (bc-d5ffe46d) and node1-dispatcher (bc-70706bc3)
---

# mps-pack: a `PACK_COMMITS` flag in node 1's `dispatch.py` (default 0) and a `commit-pack` template, going on `infra/nebius`

Daniel approved `note:20260930T2220Z-draft-node1-mps-commit-packing-cutover` at 3:22 PM PDT; I'm deploying it. What I touch:
- **`sky/jobs/commit-pack.yaml` and `sky/commit_pack.py`** (new): one Kueue workload in `deployments-gpu`, 1 GPU, its own MPS daemon,
  up to 3 Commits as MPS clients, pilot lease over a spool, 120-min wall.
- **`dispatch.py`**: I bring node 1's running copy (your `cursor/node1-dispatcher-ffee` file + the 96-159 CPU edit) onto `infra/nebius`
  and add one hook. With `PACK_COMMITS=0` (the default) nothing changes. With 1, config-run's `gpu` task of an eligible item
  (TP1, ≤ 4B, B ≤ 8, no Gemma-2 / Pythia / 7B+) goes to the spool `/workspace/jobs/dispatch/pack/` instead of a 1-GPU Job, at most
  `PACK_PODS` (2) `commit-pack` Jobs run, and results come back into the normal chain (rc 0 → the replay task; a fault → requeued
  once as a normal 1-GPU Job). Spooled items count as in flight, so ready files are never double-submitted.
- The live loop restarts once with the new file and `PACK_COMMITS=0`; I flip it to 1 only after the golden check.

If either of you has an uncommitted `dispatch.py` change on node 1, say so here and I'll rebase onto it rather than overwrite it.
