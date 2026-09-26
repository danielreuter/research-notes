---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-26T00:10Z
---

# verify-flock-pure: H100 BF16 art:1589ffe1 is verified=accepted (60/60 sessions, a file re-verification) for the 01:00Z render; the other three re-runs and vllm-v1 are in progress

- **art:1589ffe1** (prover r20260925-233831-a064, verifier r20260925-233818-a37e), by replay run r20260925-235824-1a5c.
  - The verifier was built from flock-backend 0864d146, which has the Ping answer, plus my replay subcommand
    (lane/verify-flock-pure @ 5f2b5cb2).
  - All 60 recorded sessions were accepted, from 1,024 to 32,768, including the 16,384 plateau (2 proofs).
  - My instance files match the verifier's (10/10), the prover's 24 plateau proofs are the recorded ones, and all 12
    tampered-record negatives behaved as expected.
- **Also labelled accepted, all now pulled:** art:bb289d47 and art:ed0047be (same runs as ids I'd already replayed),
  art:fb526e50 (18/18) and art:37215309 (66/66).
- **Running now:** r20260926-000935-dd35, covering art:167e64a8, art:7afeecbe and art:c3e83404. All three verifier runs
  ran e52eca82, whose verifier path is identical to 0864d146, and each plateau's proofs are the recorded ones (12/12).
  vllm-v1 art:56f792bd follows, with its own replay tool on lane/verify-flock-pure-vllm @ f9ada8e7 (ff1c1e3f plus a replay
  subcommand); a spot replay on my VM was accepted.
