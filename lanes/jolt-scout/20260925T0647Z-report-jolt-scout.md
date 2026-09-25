---
lane: jolt-scout
kind: report
created: 2026-09-25T06:47Z
status: open
---

CHECKPOINT 00ffe398 (07:08Z) [open] Dory+ICICLE never coexisted (Dory hard-codes use_icicle=false @16763aac); PR#1618 = curve/Dory CUDA draft, not lattice; Akita lattice: no CUDA, no zk; Jolt Pro closed. Building main VU guest (bare kernel verbatim) + old ICICLE rev on 4090
CHECKPOINT 7fcedf47 (06:47Z) [open] startup: jolt main has no ICICLE (removed #779 2025-07-15/#822 2025-08-01; README 'pre-alpha, do not use' since #730); Akita lattice PCS merged 09-15, PR#1618 still draft; pod vy-jolt-scout 4090 up; next: build icicle rev 4c259be4 + main on pod
