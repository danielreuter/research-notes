---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-b1c
created: 2026-09-25T20:12Z
---
# b1c pods past the 20:30Z vyv- deadline: please extend

b1c (reopened) runs on two new pods, both registered guard 90:
- `vyv-rf-b1c-cpu` (ct8r3kp8kt3b1r, cpu3g 16 vCPU, $0.64/h): `r20260925-200850-e37c`, lints + gate (b) head `dca6a867` vs main
  `7da00370`, expected end ~21:25Z.
- `vyv-rf-b1c-g2` (sw02ba4affppfn, 1x L40S, driver 580, $1.09/h): #101 head + base `r20260925-201117-8d31`, expected end ~21:00Z.
Both are terminated as soon as their runs are preserved. (`vyv-rf-b1c-g1` was terminated at once: driver 550, torch cu129 saw no GPU.)
