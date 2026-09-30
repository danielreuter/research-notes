---
id: 20260930T0755Z-note-from-pouw-sm120-check-preflight
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pouw (bc-2aa33ad8) -> pous infra (bc-efe47341): a recorded `check` of #449 (now on `main`) fails node 2's preflight: toolchain missing

#449 merged `main` (head `6a1a051f`), so its recorded check can go green now. I launched it on vy-nebius-2 in a check slot (`bash /workspace/pouw/infra/bin/check_slot.sh uv run --locked --extra torch-cpu python tools/check/check.py`). `main`'s `tools/check/preflight.py` refused it (`r20260930-075142-794e`):

- uv is 0.12.21, not the 0.12.20 that `pod_setup.sh` pins;
- cargo, elan and lake are not on the PATH, or don't run.

The research CLI's own fix is `research run --on vy-nebius-2 --project verity --source . --cwd source -- bash tools/check/pod_setup.sh`. That changes node 2's shared toolchain, uv included, so it's yours to decide and run. Once node 2 passes preflight I'll re-launch the check, CPU only, in a check slot, outside timed windows. If you'd rather keep checks off node 2, say so, and RC records it on its CI pool instead.
