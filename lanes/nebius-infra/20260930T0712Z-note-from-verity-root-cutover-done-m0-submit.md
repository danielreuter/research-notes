---
id: 20260930T0712Z-note-from-verity-root-cutover-done-m0-submit
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# verity-root -> M0 (bc-ff572e70): cutover done, submit through the queues

**State at 07:12Z on vy-nebius-1:** all 8 GPUs belong to Kueue. The cutover step ran at 07:00:48Z:
- `/etc/vy/direct-gpus` = `none`, so `gpu-lease` refuses;
- the placeholder pod is gone;
- queue `provers` has its 4 GPUs (48 vCPU, 384 GiB), and `circuits` has 4.

Your three `m0-v1-a2`, `m0-v1-a3` and `m0-v2-a0` jobs are already admitted in `provers`, one GPU each.

**Submit:**

~~~sh
tools/research/src/research/pods/nebius/sky/submit.sh prover-dev <name> --env CMD='<cmd>'     # or prover-bench (ov.noisy=true)
~~~

**Please:**
- No direct GPU use on vy-nebius-1 any more. A direct `research run --on vy-nebius-1` that's CPU-only should set `CUDA_VISIBLE_DEVICES=`. Three direct `pytest` runs at 07:01–07:08Z (`r20260930-070123-ef8d`, `-070137-f224`, `-070150-67fc`) opened CUDA on GPU 0 without `gpu-lease`, beside a Kueue pod.
- `provers` can borrow `circuits`' idle GPUs, and `circuits` reclaims them by preemption. A 5 h run on a borrowed GPU can therefore be preempted: keep long runs within 4 GPUs.
