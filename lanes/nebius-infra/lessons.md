---
id: nebius-infra/lessons
campaign: overnight-sep30
lane: nebius-infra
kind: report
status: open
repo: danielreuter/verity
origin: nebius-infra
---

# Nebius servers: shared lessons log (vy-nebius-1 = Verity, vy-nebius-2 = POUS)

**How to use it:**
- Read it before you start a job on either server.
- It's append-only: add at the bottom, one bullet per lesson, in the form `- YYYY-MM-DD HH:MMZ [who] what bit you -> fix (code: path | PR | none yet)`.
- Never edit someone else's bullet. To correct one, append a new bullet that says what it corrects.
- It's union-merged in git (`.gitattributes`), so concurrent appends from both sides don't conflict.
- When a lesson recurs, the steward (nebius-infra) turns it into code or config on `cursor/nebius-infra-e910` and appends the fix.
- It's public: no secrets, keys or exploit details.

## Log

- 2026-09-30 04:23Z [verity/nebius-owner] Editor on the project can't attach a service account to a VM, so the self-stop lease can't work -> launch passes `NEBIUS_VM_SA_ID` (the separate vy-vm-self-stop SA) (code: `pods/nebius/launch.sh`)
- 2026-09-30 04:59Z [verity/nebius-owner] Never `shutdown` inside the VM: Nebius treats it as a failure, restarts the VM and keeps billing -> stop only with `teardown.sh stop` or the lease (code: runbook)
- 2026-09-30 05:24Z [verity/nebius-owner] `research` crashed for the non-root `research` user (the `/root/dm` probe raised PermissionError, and on Python 3.12 at import) -> `os.path.isdir` probe (#484/#488; #485 fixed it differently, and the two conflicted until the infra branch resolved it); interim host fix `chmod 711 /root` on both VMs
- 2026-09-30 05:4xZ [verity/kueue] A SkyPilot job with a relative `workdir` started uploading the API server host's `/workspace` (stopped at 51 GB) -> templates run from a synced tree (`SRC=/workspace/research/trees/<lane>`), with no workdir upload (code: `sky/jobs/*.yaml`, `sky/submit.sh`)
- 2026-09-30 05:4xZ [verity/kueue] SkyPilot's SSH tunnel for the Kubernetes API takes 127.0.0.1:6444, which is k3s's own internal port, so k3s crash-looped -> on the head node the kubeconfig points straight at 6443 (code: `sky/cluster_up.sh`)
- 2026-09-30 05:4xZ [verity/kueue] SkyPilot's runner sets `OMP_NUM_THREADS=1`, so a job silently runs single-threaded -> every template sets it to its vCPUs; set it in any job YAML you write (code: `sky/jobs/*.yaml`)
- 2026-09-30 05:4xZ [verity/kueue] The job image's user is uid 1000 with Python 3.10 -> jobs write only under `/workspace/jobs` (mode 1777) and run `research` through uv's Python 3.12; weights stay read-only at `/workspace/hf` (code: `sky/jobs/*.yaml`)
- 2026-09-30 05:4xZ [verity/kueue] The SkyPilot client forwards `KUBECONFIG` to the API server -> `submit.sh` unsets it (code: `sky/submit.sh`)
- 2026-09-30 05:4xZ [verity/kueue] In CDI mode the GPU device plugin ignores `NVIDIA_VISIBLE_DEVICES`, and device minors run opposite to `nvidia-smi` indices (index 0 is `/dev/nvidia7`) -> a placeholder pod holds the direct-run GPUs, checked through `nvidia-smi -q` (code: `sky/cluster_up.sh` step 2b)
- 2026-09-30 05:4xZ [verity/kueue] Kueue quotas are accounting only: pods request CPU but can burst to the whole host, and direct `research run --on` work is invisible to Kueue -> pin benchmark CPUs yourself (`taskset -c`, as M0 does with 144-191) and record `ov.noisy` (code: none yet)
- 2026-09-30 05:46Z [verity/nebius-owner] GPU clocks are locked node-wide at boot (2,100 MHz graphics / 12,481 MHz memory, `vy-clocks.service`); `nvidia-smi -lgc` is refused for `research` -> label timings `locked-2100`; clock experiments go through the Nebius owner (code: #488 `vm_setup.sh`)
- 2026-09-30 05:46Z [verity/nebius-owner] Hard stop 2026-10-02T04:57:26Z (the lease is clamped; root's `vy-deadline.timer` stops each VM). No renewal or restart passes it -> finish timed and long runs before then (code: #488)
- 2026-09-30 05:46Z [verity/nebius-owner] There's no local NVMe: `/workspace` is a network SSD, non-replicated, about 2 GiB/s read -> keep anything irreplaceable in the store; `HF_HOME=/workspace/hf`, read with `HF_HUB_OFFLINE=1` (code: runbook)
- 2026-09-30 06:05Z [nebius-infra] `gpu-lease` takes the lowest free indices, so on vy-nebius-1 direct runs land on GPUs 0-3, which Kueue also schedules (only 4-7 are held for direct runs). After cutover to all 8 GPUs, every direct run would share a GPU with a Kueue pod -> allow-list fix on the infra branch (code: `pods/sh/gpu_lease.sh`, `/etc/research/gpu-lease.allow`)
- 2026-09-30 06:05Z [nebius-infra] A run that holds a GPU through `gpu-lease` but spends its time in CPU phases shows `held` at 0% utilization (two such holds at 06:03Z) -> take the lease only around the GPU phase, or split CPU and GPU steps into separate runs (code: none yet)
- 2026-09-30 06:08Z [nebius-infra] On vy-nebius-1 Prometheus scrapes DCGM twice (two exporter services), so `count(DCGM_FI_DEV_GPU_UTIL)` is 16 -> aggregate `max by (gpu)` before summing (code: `sky/usage_report.py`)
- 2026-09-30 06:08Z [nebius-infra] Node 1's Prometheus keeps every GPU (DCGM, 1 min) and host (node-exporter) metric since 05:16Z with 1000-day retention -> utilization is read from it, with no second sampler; node 2 has no Prometheus, so it gets `vy-usage` in host mode if POUS agrees (code: `sky/usage_report.py`)
