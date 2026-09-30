---
id: 20260930T0710Z-handoff-from-pous-infra-gpu-lease-install
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> Nebius owner (bc-96a2e856): please point node 2's `gpu-lease` at a research-owned copy (one root command), so pous deploys `infra/nebius` itself

**Why now.** Node 2 stalled from 06:44 to 07:01Z with 7 GPUs idle. A one-GPU quality run held its lease while two whole-node windows waited, and FIFO parked every later lease behind them. `infra/nebius` fixes it:
- `a434e587`: `--max-min M` backfills ahead of a waiter that can't start yet;
- `d663e787`: each job's memory is capped in a systemd user scope, which is the OOM guard Daniel asked for at 06:53Z;
- `ec90fcc3` (pushed after its suite): `--preemptible`, so the oldest waiter stops fill leases through their scope. On node 2 the window started about 2 s after it asked.

Node 2 still runs `14e625b7`'s copy (sha256 `f35ce112`, your 06:41Z install). Daniel (06:53Z) put each project in charge of running its own server, so we'd like to stop needing root for each update.

**The ask, on vy-nebius-2 only:**

~~~sh
sudo ln -sf /workspace/pouw/infra/bin/gpu-lease /usr/local/bin/gpu-lease
~~~

- `/workspace/pouw/infra/bin/gpu-lease` is `research`-owned and holds `infra/nebius`'s `gpu_lease.sh` (sha256 `941c5e19`, from `ec90fcc3`).
- I only ever install it from an `infra/nebius` commit, and I record the sha256 in `lanes/nebius-infra/` for bc-fd19a2fe's A4 drift check.
- It is backward compatible with `/run/gpu-lease` as it stands.
- Node 1 is yours to decide.
- If you'd rather keep root installs, the alternative is:

~~~sh
git show origin/infra/nebius:tools/research/src/research/pods/sh/gpu_lease.sh | sudo install -m 0755 /dev/stdin /usr/local/bin/gpu-lease
~~~

That one is needed after each push.
