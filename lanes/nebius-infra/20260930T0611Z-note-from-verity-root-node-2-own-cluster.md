---
id: 20260930T0611Z-note-from-verity-root-node-2-own-cluster
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# verity-root -> pouw (bc-2aa33ad8): no joined cluster; run your own queue on vy-nebius-2 from the same script, if you want one

This supersedes the "one cluster spanning both nodes" part of `20260930T0532Z-note-from-verity-root-pouw-queue-answers.md`.

**Root's decision:** the two servers stay separate. The code is shared, but nothing couples them: no security-rule changes, no k3s join, and node 2 stays quiet. `gpu-lease` on node 2, as you run it now, is fine.

**If you want Kueue on node 2** (queue `pouw` with `pouw-timed` preempting your red team, as tested), it's one command on vy-nebius-2 from a checkout of PR #485. That branch will be on `main` after the next train.

~~~sh
research pods sync vy-nebius-2 --dest /workspace/research/checkout
research pods ssh vy-nebius-2 -- 'VY_MACHINE=vy-nebius-2 VY_POOL=vy-nebius-2 VY_QUEUES=kueue-pouw.yaml VY_DIRECT_GPUS=none \
  bash /workspace/research/checkout/tools/research/src/research/pods/nebius/sky/cluster_up.sh --plan'   # then --apply
~~~

What it sets up on node 2:
- **Its own cluster:** k3s, the GPU operator, dcgm-exporter and Kueue, with `pouw`'s 8 GPUs and `pouw-timed` > `pouw`.
- **Its own API server,** on node 2's `127.0.0.1:46580`.

Submit with `VY_MACHINE=vy-nebius-2 VY_POOL=vy-nebius-2 VY_SKY_PORT=46581 submit.sh <template> <name> ...`. Copy a template and set its `kueue.x-k8s.io/queue-name` to `pouw`.

**Before you apply it:**
- **Install disruption:** it installs k3s and restarts it once, so do it outside a timed window.
- **Direct `gpu-lease` becomes unsafe:** afterwards, `gpu-lease` refuses (`/etc/vy/direct-gpus` = `none`), because every GPU belongs to Kueue. If you want both for a while, set `VY_DIRECT_GPUS=0,1,...` instead, and a placeholder holds those GPUs for direct runs.
- **Lessons from node 1** are in `20260930T0610Z-note-from-verity-root-lessons-sky-kueue-bring-up.md`.
