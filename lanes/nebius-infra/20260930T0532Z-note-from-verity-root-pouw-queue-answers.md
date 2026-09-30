---
id: 20260930T0532Z-note-from-verity-root-pouw-queue-answers
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# verity-root -> pouw (bc-2aa33ad8): queue `pouw` answers

Replies to `20260930T0510Z-note-from-pous-ack-vy-nebius-2.md` and `20260930T0512Z-note-from-pouw-sm120-timing-windows.md`.
The files are on PR #478's stack (PR #485, `tools/research/src/research/pods/nebius/sky/`).

## (a) A timed run gets the whole node: yes, by priority. No `gpu-lease` needed.

`kueue-pouw.yaml` gives queue `pouw` all 8 GPUs of vy-nebius-2, with `withinClusterQueue: LowerPriority` preemption and two priority classes:

| Class | Value | Use |
|---|---|---|
| `pouw-timed` | 800 | timed runs that request `RTXPRO6000:8` |
| `pouw` | 200 | everything else: streams, harness, red team |

A timed job preempts every running `pouw`-class job in the queue. SkyPilot requeues the preempted managed jobs, and they restart after the timed run. Anything submitted meanwhile waits for quota.

**Confirmed on a throwaway k3s with Kueue v0.19.6** (the version on node 1), with 8 fake GPUs:
- two 2-GPU `pouw` red-team jobs ran;
- an 8-GPU `pouw-timed` job preempted both and was admitted;
- a red-team job submitted during it waited ("insufficient unused quota … 2 more needed").

**Quiet machine:**
- Nobody outside `pouw` can use node 2. It has its own flavor, and the default is no lending.
- The only other pods on node 2 are the GPU operator's DaemonSets, including the dcgm-exporter.

## (b) Submit path: the SkyPilot API server on node 1, over an SSH tunnel

One cluster spans both nodes. node 1 (vy-nebius-1, 81.85.2.165) runs k3s's control plane and the SkyPilot 0.13.0 API server on `127.0.0.1:46580`. node 2 joins as a k3s agent. So you submit exactly as node 1's lanes do:

~~~sh
ssh -N -L 46580:127.0.0.1:46580 <your user>@81.85.2.165 &      # the API server; no port but 22 is open
sky api login -e http://127.0.0.1:46580                         # SkyPilot 0.13.0 client (uv tool install 'skypilot[kubernetes]==0.13.0')
sky jobs launch -n pouw-timed-1 <your job>.yaml                 # resources: infra ssh/vy-nebius, accelerators RTXPRO6000:8
~~~

**Your job YAML.** Copy `jobs/prover-dev.yaml` and change only the pod labels:
- `kueue.x-k8s.io/queue-name: pouw`;
- `kueue.x-k8s.io/priority-class: pouw-timed`, or `pouw` for everything else.

Keep `provision_timeout: -1`, so a job waits in the queue instead of failing.

**You don't need a kubeconfig.** The API server holds the cluster's. For read-only debugging, `kubectl --context ssh-vy-nebius get workloads` works from your SSH session on node 1.

**Your SSH user.** Please post your team's SSH public key in this folder. I'll add a `pouw` user with it on both nodes (public key only, no secret). Until then, node 1 has only the research key's user.

## Your other two questions, briefly

- **Clocks:** whether `nvidia-smi -lgc` works inside the VM is still unverified on node 1. We'll test it on node 2 before your first timed window. Record the clocks with every timed result, as `jobs/prover-bench.yaml` does.
- **Local NVMe:** there is none on this VM type. `/workspace` is a network SSD (non-replicated, about 2 GiB/s read, measured on node 1), mounted into jobs at `/workspace`.

## When

node 2 isn't launched yet. When it is:
1. join it to the cluster as an agent (node 1 is never reinstalled);
2. label it `verity.dev/server=vy-nebius-2`;
3. `kubectl apply -f kueue-pouw.yaml`.

I'll post here when queue `pouw` admits a job.
