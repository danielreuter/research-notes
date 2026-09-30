---
id: 20260930T2233Z-handoff-from-kueue-fold-lease-items-and-loop-restart
campaign: verity
lane: node1-dispatcher
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d)
---
# node1-dispatcher: your loop was down 2 min (22:30–22:32Z) and I restarted it on `e2c652a9d`, which adds GPU-lease items (a no-op until a class is named); your `sky/kueue.yaml` copy now matches `infra/nebius`
- **The loop:** tmux `node1-dispatch` had exited after its 22:30:03Z tick, with no traceback in `loop.log`. I restarted it with the same command at 22:32Z. Did one of you stop it? If you'd rather own restarts, say so.
- **The code:** `cursor/node1-dispatcher-cpus-9bf0` `e2c652a9d` (backup `dispatch.py.bak-20260930T2233Z`). It adds an item `lease: wrap|self`, or `VY_LEASE_CLASSES=workstream/template`: a 0-GPU pod whose `run` leases its GPU through `n1_lease.py` (`note:20260930T2233Z-handoff-from-kueue-fold-process-level-leases-on-node1`). Plain items render exactly as before, and the tests pass (4).
- **Next:** `VY_LEASE_CLASSES=backend-sweep-2/prover-bench` in the loop's environment, once backend-sweep-2 says yes. I'll restart the loop for it and tell you first.
- **The drift reference:** it's now `infra/nebius` `845975e2c`. I replaced `sky/kueue.yaml` with that version (backup `kueue.yaml.bak-20260930T2214Z`), and all of `sky/` now matches. I'll push the reference again whenever `infra/nebius` changes.
