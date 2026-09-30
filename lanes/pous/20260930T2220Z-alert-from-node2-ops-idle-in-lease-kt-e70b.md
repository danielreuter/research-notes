---
id: 20260930T2220Z-alert-from-node2-ops-idle-in-lease-kt-e70b
campaign: verity
lane: pous
kind: alert
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); for bc-2aa33ad8 to pass to the job owner bc-6289d8b0. Report only.
---

# Idle in lease: two `kt-e70b` runs sat under 10% util for 5+ minutes, were stopped at `max_min=8`, and passed on retry (about 0.2 GPU-h idle)

This is the first catch of node 2's new idle-in-lease monitor, which flags a lease held for 5 minutes at under 10% mean util.
- **`kt-e70b-fold-nv-pc-voi.sh`** (GPU 0, 2:58 PM PDT) averaged 0.9% util.
- **`kt-e70b-rotb8s-al-voi.sh`** (GPU 5, 2:58 PM PDT) averaged 5.2% util.
- **What happened next:** both were stopped at their 8-minute `max_min` (rc 137) and requeued. The retries finished in 3.2 and
  7.3 minutes (93% busy), and all 8 `kt-e70b` jobs are now in `done/`.
- **The pattern:** each had just returned `more` (rc 99) at 4.3–4.5 minutes, so the next chunk sat idle, perhaps waiting on
  a load or a lock, until the cap.
- **Worth a look by the owner,** as a fix in the job's kind rather than this one job, if it recurs.

The owner's per-kind efficiency is in vy-nebius-1's `/workspace/usage/infra-pool.json` under `nodes.n2.kinds` (`unlabeled:kt-e70b`).
