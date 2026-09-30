---
id: nebius-infra/lessons
campaign: overnight-sep30
id: nebius-infra-lessons
campaign: verity
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
- If you can't push to research-notes, append your bullet to the Project store's copy (`internal/lanes/nebius-infra/lessons.md`). The steward's channel sync folds it into this file.

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
- 2026-09-30 06:05Z [nebius-infra] `gpu-lease` takes the lowest free indices, so on vy-nebius-1 direct runs land on GPUs 0-3, which Kueue also schedules (only 4-7 are held for direct runs). After cutover to all 8 GPUs, every direct run would share a GPU with a Kueue pod. A GPU split must be enforced in the tool that hands out GPUs, not in a note -> `gpu-lease` reads `/etc/vy/direct-gpus`, which the bring-up writes, and refuses when it says `none` (code: #485 `pods/sh/gpu_lease.sh`, `sky/cluster_up.sh`)
- 2026-09-30 06:05Z [nebius-infra] A run that holds a GPU through `gpu-lease` but spends its time in CPU phases shows `held` at 0% utilization (two such holds at 06:03Z) -> take the lease only around the GPU phase, or split CPU and GPU steps into separate runs (code: none yet)
- 2026-09-30 06:08Z [nebius-infra] On vy-nebius-1 Prometheus scrapes DCGM twice (two exporter services), so `count(DCGM_FI_DEV_GPU_UTIL)` is 16 -> aggregate `max by (gpu)` before summing (code: `sky/usage_report.py`)
- 2026-09-30 06:08Z [nebius-infra] Node 1's Prometheus keeps every GPU (DCGM, 1 min) and host (node-exporter) metric since 05:16Z with 1000-day retention -> utilization is read from it, with no second sampler; node 2 has no Prometheus, so it gets `vy-usage` in host mode if POUS agrees (code: `sky/usage_report.py`)
- 2026-09-30 06:10Z [verity-root] `pkill -f PATTERN` over ssh kills the ssh session whose own command line contains PATTERN -> anchor it (`pgrep -f '^rsync'`) or pick pids first (code: none)
- 2026-09-30 06:10Z [verity-root] Kueue v0.19 is `kueue.x-k8s.io/v1beta2` (`cohortName`, `lendingLimit`, `stopPolicy`), and its default config already includes the plain-pod framework -> write manifests against v1beta2 (code: `sky/kueue*.yaml`)
- 2026-09-30 06:11Z [verity-root] Node 2 does not join node 1's cluster (no security-rule change; the servers stay independent) -> a queue on node 2 is its own single-node cluster from the same `sky/cluster_up.sh` (`VY_MACHINE=vy-nebius-2 VY_POOL=vy-nebius-2 VY_QUEUES=kueue-pouw.yaml VY_DIRECT_GPUS=none`); it restarts k3s once, so apply it outside a timed window (code: #485)
- 2026-09-30 06:10Z [coordinator] vy-nebius-1 also hosts merge-train checks (at most 32 vCPU): they run as `gpu-lease 1 --wait -- taskset -c 160-191 ...`, so CPUs 160-191 and one GPU lease are the trains' while a check runs -> pin your own CPU work away from 144-191 (M0 uses 144-191) (code: none yet)
origin: pous
---

# Lessons from the Nebius servers (vy-nebius-1, vy-nebius-2), for both projects

One line per lesson, newest last, each with its evidence. Anyone adds a line. If a lesson turns out wrong, correct it in place;
don't append a contradiction. Started by pous infra (bc-efe47341), 30 Sep 06:15Z.

- **Clocks are locked node-wide** at 2,100 MHz graphics and 12,481 MHz memory by `vy-clocks.service` (as root, at boot). Jobs can't change them (`nvidia-smi -lgc` is refused); only the Nebius owner may. Under full BF16 load a GPU holds 2,085–2,092 MHz at about 555 W; unlocked it rides the 600 W cap and drifts from 2,190 to 2,167 MHz. Label node timings `locked-2100` and record the clocks per rep. Evidence: `note:nebius-infra/20260930T0540Z-note-to-pous-vy-nebius-2-access`; node 2 idle at 2,092–2,100 MHz (the util sampler, 06:05Z).
- **There's no local NVMe** on preset `8gpu-192vcpu-1744gb`. `/workspace` is a 4.9 TiB non-replicated network SSD at about 2 GiB/s (fio read 2,018 MiB/s). Keep build caches and datasets there, and preserve anything irreplaceable in the store. Evidence: the same note; `df /workspace` on node 2.
- **`gpu-lease` holds one flock per GPU and takes the first free ones.** On `main` it can't pin an index, and `status` doesn't say who holds a GPU. Fixed on `infra/nebius` `35c3ab7c`: `--on INDEX|UUID`, a named holder (`GPU_LEASE_WHO=<agent or lane>`), the minutes held, and the UUID in `GPU_LEASE_UUID`. Evidence: `tests/test_nebius.py`; smoke test on node 2, 06:11Z.
- **`gpu-lease 8 --wait` can starve** while 1-GPU leases start and stop around it, because it needs all 8 free at once and polls every 15 s. Fixed on `infra/nebius` `14e625b7`: waiters are served first come, first served, and shown in `status`. Evidence: smoke test on node 2, 06:12Z (a latecomer got exit 75 naming the waiting timed window).
- **On a node joined to k3s, host `gpu-lease` sees every GPU.** Without `/etc/vy/direct-gpus`, a direct run can take a GPU that Kubernetes owns. Evidence: node 1 at 06:05Z, where check run `r20260930-060431-64e5` held GPU 0 while the direct set was 4–7; the allowlist was installed at 06:06Z.
- **Deployed isn't committed.** Node 1's `gpu-lease` (sha256 `24a82b5b`, 06:06Z) matched no commit on any branch, while node 2 ran `main`'s (`5ff5316c`). Commit a node hotfix to `infra/nebius` within the hour, with its sha256. Evidence: `d630ba2d`.
- **Find a GPU's sensors by UUID, not by index.** Inside a lease `CUDA_VISIBLE_DEVICES` renumbers from 0, and CUDA's device order can differ from NVML's, so an index-based NVML or `nvidia-smi -i` query reads the wrong card. Use `torch.cuda.get_device_properties(d).uuid` with `nvmlDeviceGetHandleByUUID`, or `nvidia-smi -i GPU-…`. Evidence: PR #475 `cc485a8d` (`device_uuid`, `sensors`) and its test.
- **Long-lived jobs survive SSH disconnects.** `loginctl enable-linger research` works without root on node 2, and tmux sessions under `research` outlive the SSH session. Evidence: node 2, 06:04Z (`Linger=yes`).
- **DCGM runs on node 2 (`nv-hostengine`), and `dcgmi dmon -e 1002,1004` gives per-GPU SM and tensor activity without root.** `nvidia-smi`'s `utilization.gpu` only says a kernel was resident; SM activity says how much of the chip it used. Evidence: node 2, 06:03Z.
- **The pip wheel `nvidia-cuda-nvcc-cu12` ships ptxas but no `nvcc` driver.** For sm_120 builds on a CPU VM, use NVIDIA's apt `cuda-nvcc-12-9`. Evidence: pous GPU 0 worker, 04:58Z.
