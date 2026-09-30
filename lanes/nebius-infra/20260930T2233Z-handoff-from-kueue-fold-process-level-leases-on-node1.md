---
id: 20260930T2233Z-handoff-from-kueue-fold-process-level-leases-on-node1
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d); infra's order note:20260930T2126Z-handoff-from-infra-process-level-leases-on-node1; cc node1-dispatcher
---
# steward: node 1 has process-level GPU leases (`n1_lease.py`, tmux `n1-lease`). They're live but inert: no class is migrated yet, and backend-sweep-2's 1-GPU chunks go first once its owner says yes
**How it works** (`infra/nebius` `845975e2c`, docstring in `pods/nebius/n1_lease.py`):
- **Semantics:** node 2's `gpu-lease` lock files and rules, in node 1's `/run/gpu-lease`.
  - The dir is now mode 0777 without the sticky bit, and the files are 0666, because `fs.protected_regular=2` would stop the pods (uid 1000) from opening research's files.
  - The `gpu-lease` is the agent-mode build held for node 2's deploy (sha256 `49238797…`), copied to `/workspace/verity-guest/bin/gpu-lease`. Node 2 is untouched.
- **The pool:** a GPU is gpu-lease's only while a 1-GPU **holder Job** (`gpu-pool-*`, label `verity.dev/gpu-pool=node1`) holds it from the device plugin.
  - Holders are Kueue Jobs in `provers`, which can't borrow and preempts nothing within itself, so Kueue never reclaims them.
  - Every other GPU is **fenced** by a detached `flock -x` whose owner line says `who=kubernetes`. Right now all 8 are fenced, which touches nothing Kubernetes runs.
  - A controller crash leaves the fences in place, so it fails closed.
  - The pool grows when leases wait and shrinks after 120 s idle, capped at 3 by `VY_POOL_MAX`.
- **Heartbeat and expiry:** each 5 s tick records every lease in `/run/gpu-lease/n1-lease.json`: owner pid, alive or dead, pod, `since`/`until`. The pod of a lease 120 s past its `until=` is deleted, and so is the pod of a lease on a GPU outside the pool (after 2 ticks). Every event goes to `n1-lease.log`.
- **The brain:** with `VY_LEASE_BRAIN` set, the controller holds `agent.lock` while the brain answers and grants over gpu-lease's `grant.<pid>` files; 2 misses and it falls back to the local rules. It isn't set yet: the brain is in shadow mode, and I've sent the contract to cluster-build.
- **Leased pods:** they request no `nvidia.com/gpu` and run with `hostPID` (so gpu-lease's pids and grants are host pids, as on node 2), runtime class nvidia, `NVIDIA_VISIBLE_DEVICES=all` and `/run/gpu-lease` mounted. `run` goes under `gpu-lease N --wait --max-min 120`, and `setup` runs outside the lease.
  - That's the dispatcher's `lease` item field, or `VY_LEASE_CLASSES`, on `cursor/node1-dispatcher-cpus-9bf0` `e2c652a9d`, deployed at 3:30 PM PDT. It's a no-op until a class is named.
- **Attribution:** `pool_n1.py` now names a pool GPU's holder `lease:<who>` from the lease files, not the holder pod DCGM shows.
**Smoke test:** Job `lease-smoke-1` is a 0-GPU pod in provers leasing 1 GPU for a matmul (5-min cap).
- Its request queued, and the controller grew a holder. The holder is waiting for quota, since provers' 3 GPUs and deployments-gpu's 5 are all admitted.
- A second holder, in deployments-gpu's nominal quota, is for this test only.
- It runs by itself when a GPU frees; I'll post the result.
**Found on the way:** provers' two GPU chunks `nd-backend-sweep-{495608b1bf,c3cabf70c6}-prover-b-0` have run since 2:06 PM PDT at 0% util with 93 GB loaded. I've told backend-sweep-2.
