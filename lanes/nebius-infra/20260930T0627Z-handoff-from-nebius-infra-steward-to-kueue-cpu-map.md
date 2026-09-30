---
id: 20260930T0627Z-handoff-from-nebius-infra-steward-to-kueue-cpu-map
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward (bc-fd19a2fe) -> Kueue worker (bc-c445c55b): your cutover is blocked by train checks' `gpu-lease`; CPUs 128–191 are for checks, so please cut Kueue's CPU nominal by 64

**Cutover.** `cutover.sh` (pid 320771 on node 1) is waiting on train checks, which take `gpu-lease 1 --wait` although they're
CPU-only. Check `r20260930-060431-64e5` holds GPU 0 under the pre-allow-list `gpu-lease`, and `status` doesn't show it, because
it's outside `/etc/vy/direct-gpus`. I've asked the research coordinator to drop `gpu-lease` from checks and use slot locks
(`lanes/coordinator/20260930T0627Z-...-checks-drop-gpu-lease.md`). After cutover, a check with `gpu-lease` would exit 2.

**Two small asks, for your files:**
- **Checks' CPUs.** CPUs 128–191 (64 vCPU) go to merge-train checks, in two pinned 32-vCPU slots (merge velocity is Daniel's
  priority). Please take 64 off `kueue.yaml`'s CPU nominal quotas, 192 → 128 in total (for example circuits 144 → 104, provers
  48 → 24), so admitted jobs don't count on those cores. Pods aren't pinned, so this is accounting, like the rest.
- **`gpu-lease status` lists held GPUs outside the allowed set,** so a leftover like GPU 0 stays visible. It's a one-line change
  on `infra/nebius`. I can do it if you'd rather.

**Two utilization facts for your retune:**
- **Node 1, 05:16–06:25Z:** GPUs 0.4% busy, CPU 8.8%, RAM peak 112 GiB of 1,716.
- **`config-run` asks for 512 GB.** `circuits`' 1,280 GiB therefore admits only 2 config runs at once, although it has 4 GPUs.
  Small models (135M–1.5B) need far less. I'm asking the vLLM side to use the template's per-class overrides.
