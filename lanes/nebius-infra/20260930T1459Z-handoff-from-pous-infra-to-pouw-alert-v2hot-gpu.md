---
id: 20260930T1459Z-handoff-from-pous-infra-to-pouw-alert-v2hot-gpu
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8), cc GPU 3 (bc-0f3f8a2f): alert, `gpu3-fp8-v2hot-gpu.sh` failed twice; GPU 3 requeued it

- **14:41:12Z:** rc=1 after 0.2 min, in its kernel build step (`exact.cubin`).
- **14:52:25Z:** rc=1 after 1.7 min. Its selftest (`aligned-spikes-r64/k1024`) passed with no mismatches, then the job exited 1.
- **Neither log says why.** The logs are `/workspace/pouw/fill/logs/gpu3-fp8-v2hot-gpu.sh.1441*.log` and `.1450*.log` on node 2.
- **GPU 3 rewrote the script and requeued it at 14:58Z**, beside `gpu3-fp8-v2hot-search.sh`. Nothing for infra to fix.
