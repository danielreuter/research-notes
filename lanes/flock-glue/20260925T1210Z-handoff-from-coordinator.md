---
lane: flock-glue
kind: handoff
from: coordinator
created: 2026-09-25T12:10Z
---

# STOP: laptop disk at 1.82 GiB and falling. Write FINAL now

The root's rule: below 1.8 GiB, the lowest-value laptop lane stops. You're first, because Flock numbers are drill-down-only
until flock-live and a re-audit land. Now:
1. Don't fetch anything to the laptop. Your final runs' results stay on R2 (`--custody-r2`). Check them with
   `research data preserved <run>`, and repush from the pod if needed (`lanes/b-ligero-sha256/evidence/pod-scripts/62-repush.sh`).
2. Terminate vy-flock-glue-h100 and vy-flock-glue-a100 (the A100 has been idle 17 min).
3. Write your report's results so far, with each timing labelled by Flock profile and "not cleared", and a short handoff to
   the coordinator plus flock-live with the best end-to-end ratios and what's still open (the device witness, the single
   2.15 GB upload).
4. Write FINAL with `--require-pushed`.
