---
id: 20260930T2348Z-handoff-from-proofs-overhead-includes-verifier
campaign: verity
lane: proofs-verify-overlap
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Daniel, 4:47 PM PDT: overhead INCLUDES the interaction with the verifier; it's part of the algorithm

This supersedes "verifier excluded" in the earlier formula.
- **overhead** = peak ÷ R, where R = 2·K·VUs ÷ **t_session**.
  - t_session is the wall time of the whole interactive proof job: prover work, every live-coin round trip with the
    verifier, and the verdicts.
  - It's steady state (warm, statements back to back), per accepted VU. Setup (staging, circuit build) is reported beside
    it, not in it.
  - With pipelining it's the job's total wall time over N statements ÷ total VUs, so overlapping the verifier lowers
    overhead directly.
- **Keep as secondary fields** in each `hillclimb-point`: `t_prove_only_s_per_vu` (prover buckets only),
  `verify_s_per_statement`, `gpu_held_s_per_vu` and `gpu_util`.
- `throughput_vu_per_s` = VUs ÷ t_session.
- Any point already written with the prover-only overhead: rewrite it, and label its step `overhead=session`.
