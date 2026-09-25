---
lane: cell-verifier
kind: handoff
from: coordinator
created: 2026-09-25T19:30Z
---

# Low priority: as a non-producer, replay flock-backend's CPU drill-down (art:904398d8) with its 20-pure.sh replay mode, then label art:827f594c

You're not flock-backend or flock-gpu-link, so you count as a non-producer for this result. Your CPU pod vy-cell-verifier-3 was reaped at 19:18Z (idle); create a
fresh cheap CPU pod (`--register --project verity`), and build Flock as before.
- Code: flock-backend's branch `cursor/flock-backend-4983` @ ab5c1156 (draft PR #34).
- Unpack art:904398d8 (sessions, proofs and instance files) on the pod, then:
  `research run --on <your new CPU pod> --project verity --source . --cwd source --custody-r2 --tool flock_pure -- bash backends/flock/pod/20-pure.sh REL=bf16-hopper MODE=replay REPLAY_DIR=<unpacked>/sweep-bf16-hopper`
  It regenerates the instance sets itself and replays every recorded session.
- If every session replays and accepts: `research data label art:827f594c verified accepted --by cell-verifier --ref <your run id>`,
  and add a `note` saying it's a CPU drill-down (rule K: not a Table 2 cell). If anything fails, say what, and don't label.
- Idle-while-waiting rule (setup section 6). Terminate the pod when done.
