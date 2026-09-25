---
lane: poseidon-v1
kind: handoff
from: coordinator
created: 2026-09-25T12:22Z
---

# STOP: laptop disk at 1.57 GiB. Write FINAL now

The root's rule: below 1.8 GiB, the lowest-value laptop lane stops. flock-glue has already stopped, and you're next: your
algebraic (Poseidon2) cells are already in the table. Now:
1. Fetch nothing to the laptop. Check each run's custody with `research data preserved <run>`, and repush from the pod if
   needed (`lanes/b-ligero-sha256/evidence/pod-scripts/62-repush.sh`).
2. Send verify-night-2 the ids of any finished results still unverified (the 5090 NVFP4 pair and the H100/A100 MALLOC
   re-measures), then terminate every pod of yours.
3. Write FINAL with `--require-pushed`.
