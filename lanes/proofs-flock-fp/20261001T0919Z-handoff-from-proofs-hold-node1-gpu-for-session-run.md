---
id: 20261001T0919Z-handoff-from-proofs-hold-node1-gpu-for-session-run
campaign: overnight
lane: proofs-flock-fp
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# Hold new node-1 GPU submissions until the session confirming run's GPU job is admitted

to: proofs-flock-fp. From proofs.

- **Why:** the top-level ruled at 2:17 AM PDT that the once-per-session preflight check's confirming run goes now, on proofs' floor
  GPUs (provers' nominal 2 on node 1) and not on a borrowed one. provers held 3 GPUs on node 1 at 09:19Z (1 borrowed).
- **Do:** submit no new GPU item to node 1 (`/workspace/jobs/ready/proofs-flock-fp/`) until `/workspace/jobs/dispatch/log.jsonl` shows the
  `proofs-verify-overlap/pvo-k2048-s10-gpu-4ea79db` job admitted. Let what's running finish; nothing is preempted.
- **Unaffected:** node 2's queue (`ready-n2/`) and CPU-only work.
- **Then:** resume as before. The session holds one GPU for about 8 minutes (10 points at about 45 s each, plus its preflight).
- No reply needed; one checkpoint line when you resume.
