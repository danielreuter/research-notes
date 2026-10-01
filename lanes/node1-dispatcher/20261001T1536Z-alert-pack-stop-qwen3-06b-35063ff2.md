---
id: 20261001T1536Z-alert-pack-stop-qwen3-06b-35063ff2
campaign: one-pool
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: node 1's dispatcher (dispatch.py stop_model; MPS Commit packing, circuits' rule of 10:55 PM PDT Sep 30)
---

# MPS packing stopped for qwen3-06b: a packed Commit's replay failed

- **Item:** `vllm-epoch-run/cov-gm001-pk2`
- **Runs:** replay `r20261001-153347-cced`, Commit `r20261001-152708-7e93`
- **Pack pod:** `nd-commit-pack-cb69176114-commit-p-0-99v2t`
- **Replay Job:** `nd-vllm-epoch-run-35063ff27e-replay-0`
- **Why:** the replay task failed (rc 12)
- **Effect:** the item ended failed, and `packable` refuses qwen3-06b from now on (`/workspace/jobs/dispatch/pack/stopped-models.json`). Other models still pack.
- **Lift (circuits only):** on node 1, `cd /workspace/jobs/dispatch/infra/nebius && /workspace/jobs/venv312/bin/python dispatch.py pack-lift qwen3-06b --by circuits --why '...'`
