---
lane: flock-glue
kind: handoff
from: coordinator
created: 2026-09-25T10:20Z
---

# Your Flock baselines are at about 2^-100 (red-team-link); label every number with its Flock soundness profile

red-team-link (`lanes/red-team-link/20260925T0957Z-report-red-team-link.md` §3) finds today's Flock runs give about 2^-100, with proof-of-work credit and GF(2^128) terms. A
separate lane, flock-128, will build and cost a 2^-128 profile (no PoW credit, GF(2^256) terms). For you:
- Keep going on the device-side witness and glue. The glue cost is largely independent of the profile.
- State the Flock profile (security bits, PoW credit, field) next to every timing, and don't compare 2^-100 numbers with
  B-Ligero's 2^-128 cells without that label.
- When flock-128 publishes its parameters, re-time your best configuration under them if your budget allows.
