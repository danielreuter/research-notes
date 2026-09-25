---
lane: coordinator
kind: handoff
from: verify-night-3
created: 2026-09-25T19:40Z
cc: flock-backend
---

# flock-backend CPU drill-down art:827f594c: verified=accepted (18/18 sessions replay), run r20260925-193306-85c5

- Replay: `20-pure.sh REL=bf16-hopper MODE=replay` from cursor/flock-backend-4983 @ ab5c1156 (`--source . --cwd source --tool flock_pure
  --custody-r2`), on a fresh pod vy-verify-night-3 mzclpkcwdyp4xm (cpu3c, 16 vCPU). Flock b684b12 plus the patch was built there.
  The inputs were art:904398d8, staged unchanged (91/91 files) by r20260925-193226-9540.
- The instance sets were regenerated on the pod. The bf16-hopper lowering da1bbe2c is PINNED (fp8-hopper 904ca664 PINNED too).
- **18/18 REPLAY accepted:** 6 sessions each at p0-1024, p1-2048 (this result) and p2-4096, both reps each. There were no failures.
- Labels on art:827f594c by verify-night-3, ref the run: `verified=accepted`, and a `note` saying it's a CPU drill-down (rule K: not a
  Table 2 cell) and a file re-verification with the recorded coins, not transferable.
- Both runs PRESERVED. The pod was terminated at 19:39Z, about $0.10.
