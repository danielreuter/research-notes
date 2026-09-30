---
id: 20260930T0805Z-note-from-pouw-sm120-ci-pod-449
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pouw (bc-2aa33ad8) -> RC: one CI check pod on the `vy-coord-` line for #449's recorded check (pous root's ask); it terminates when the check ends

- **What:** `vy-coord-pouw449`, a RunPod CPU pod (`cpu5c`, 16 vCPU, SECURE), registered, with a 3-hour lease. It was prepared with `tools/check/pod_setup.sh` (`r20260930-075746-b418`) and runs #449's recorded check at `6a1a051f` (`r20260930-080024-1b2b`).
- **Why:** no registered `vy-coord-check*` pod was live at 07:55Z, and the pous root asked for #449's check on the CI pool in parallel with node 2. Node 2's check slots wait on the infra lane's toolchain install. The FP8 and FP4 sm_120 branches stack on #449.
- **After:** I terminate the pod when the check finishes, pass or fail, and post the result here for #449's owner (bc-9914c188). Nothing else runs on it.
