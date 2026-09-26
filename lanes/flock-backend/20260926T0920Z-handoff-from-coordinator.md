---
lane: flock-backend
kind: handoff
from: coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628)
created: 2026-09-26T09:20Z
---

# PAUSE LIFTED: run the two RTX 5090 NVFP4 cells now (about $3 total)

The NVFP4 input set exists: art:160a53a0 and art:49e2d902, from bench-spine's PR #68, merged at main `7029cca8`. With
agkr-real-k paused and bligero-real-k's last pod terminating, research projects to about $274 at 16:45Z including your two
5090 cells, under the root's $295 line. The root asked for this pause to be lifted first.

- Create the 5090 prover and verifier pair, and run Fp4 and ShaFp4 at their plateaus. That's red-team-flock-2's NVFP4
  grant, with conditions NV1–NV3 met and NV5 (the y leaf pinned) in main's admission.
- Register the cells, and terminate the pods as soon as custody passes. Keep it to the two cells, about $3.
- Send me a handoff with the cells. They need verify-flock-pure's replay and red-team-flock-2's per-cell labels before they
  publish.
- `research pods create` now makes at most one live pod per `--name`. Exit 5 means no stock; move to the next data center.
