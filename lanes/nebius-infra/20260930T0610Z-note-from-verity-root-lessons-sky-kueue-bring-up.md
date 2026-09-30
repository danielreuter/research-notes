---
id: 20260930T0610Z-note-from-verity-root-lessons-sky-kueue-bring-up
campaign: verity
lane: nebius-infra
kind: finding
status: open
repo: danielreuter/verity
origin: verity-root
---

# Lessons from the SkyPilot and Kueue bring-up on vy-nebius-1 (for the nebius-infra lessons log, bc-fd19a2fe)

Each lesson is one line to copy into the shared log; the fix is in PR #485 unless noted.

1. **A relative `workdir` resolves on the API server's host.** `workdir: .` from a client checked out at `/workspace` made the server copy *its own* `/workspace`, the 5 TB data disk with weights, into the jobs controller pod. It reached 51 GB before it was stopped and cleaned. Fix: the templates have no `workdir`. Jobs run from a tree `research pods sync` puts on the host (`SRC`), and `submit.sh` does it.
2. **SkyPilot's SSH tunnel for the Kubernetes API takes 127.0.0.1:6444, k3s's own internal apiserver port.** With the API server on the k3s head, k3s crash-looped once the GPU operator restarted it. Fix: on the head, the kubeconfig points straight at `127.0.0.1:6443`, with no tunnel.
3. **SkyPilot's job runner sets `OMP_NUM_THREADS=1`.** `nproc` printed 1 in an 8-vCPU job, and numpy, torch and OpenMP Builds would run on one thread. Fix: every template sets `OMP_NUM_THREADS` to its `cpus`. A `--cpus` override also needs `--env OMP_NUM_THREADS`.
4. **The SkyPilot client forwards its `KUBECONFIG` to the API server,** so a stale local value (here, a throwaway k3s's) disabled the SSH pool for that user. Fix: `submit.sh` unsets it.
5. **In CDI mode the GPU operator's device plugin can't be narrowed with `NVIDIA_VISIBLE_DEVICES`:** the plugin failed with "unresolvable CDI devices". Fix: a placeholder pod holds the direct-run GPUs.
6. **Device minors run opposite to `nvidia-smi` indices on this VM,** so `/dev/nvidia7` is index 0. Always map a GPU through `nvidia-smi -q` or its UUID.
7. **SkyPilot's pod image runs as uid 1000 with Python 3.10.** Host directories owned by `research` (uid 1001) are read-only to jobs, and `research` needs Python 3.11+. Fix: jobs write only under `/workspace/jobs` (mode 1777), and run `research` through uv's Python 3.12.
8. **`research` had never run as non-root.** `Path("/root/dm").is_dir()` at import raised `PermissionError` on Python 3.12. Fixed in `telemetry/cancel.py`.
9. **`pkill -f PATTERN` over ssh kills the ssh session whose command line contains PATTERN.** Anchor it (`pgrep -f '^rsync'`), or pick pids first.
10. **A GPU split must be enforced in the tool that hands out GPUs, not in a note.** The first `gpu-lease` on vy-nebius-1 counted from index 0. A direct run at 06:05Z got GPU 0, which is Kubernetes'. It was a CPU-torch check with no GPU memory in use. Fix: `gpu-lease` reads `/etc/vy/direct-gpus`, which the bring-up writes.
11. **Kueue v0.19 is `kueue.x-k8s.io/v1beta2`** (`cohortName`, `lendingLimit`, `stopPolicy`), and its default config already includes the plain-pod framework.
