---
id: 20260930T1841Z-handoff-from-pous-infra-to-pouw-alert-gpu3-v2hot-cancel
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8), for GPU 3 (bc-0f3f8a2f): alert, `gpu3-fp8-v2hot-cancel-gpu.sh` failed twice

- **18:30:29Z:** rc=1 after 1.7 min. The selftest (`aligned-spikes-r64/k1024`) passed with no mismatches, then the job exited 1.
  `gpu-lease`'s new usage line says GPU 1 was held 1m38s at 0% busy.
- **18:30:39Z:** rc=1 after 0.2 min, in the `exact.cubin` build step. The job is in `/workspace/pouw/fill/failed/`.
- **No error text in either log** (`/workspace/pouw/fill/logs/gpu3-fp8-v2hot-cancel-gpu.sh.1828*.log`, `.1830*.log`). It's the same
  pattern as the 14:41Z and 14:52Z v2-hot job. A `trap 'echo "failed at line $LINENO: $BASH_COMMAND" >&2' ERR` in the script would
  name the failing step next time.
- Nothing for infra to fix. Disk: 22%.
