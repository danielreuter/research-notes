---
id: 20260928T0733Z-handoff-from-pous-runpod-burn
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# FYI: RunPod balance runway is about 5.6 h at the current burn

A POUS sweep at 07:32Z read the balance at $134.28 and the burn rate at $23.80/h, up from $4.63/h at 06:00Z.

- POUS/PoUW pods account for $8.27/h:
  - `vy-pouw-b200`, a Pearl calibration run, $6.79/h, capped at $8 total;
  - `vy-pous-pouw-fp8` and `vy-pouw-mvp`, $0.74/h each.
- About $15.5/h is from pods outside our prefixes.

At this rate the balance runs out around 13:00Z, and then every pod stops. Our B200 comes down within its cap. Please check whether the non-POUS pods are intended. Daniel is asleep; I've let him know.
