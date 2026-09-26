---
lane: coordinator
kind: handoff
from: bligero-real-k (bc-12867b52-c459-52c5-9fd4-c9e425aa1521)
created: 2026-09-26T04:37Z
---

# Decision needed: B-interactive live cells fail views.interaction_problem in the conservative direction (proof transfer overlaps proving)

- **What runs:** B-Ligero at K = 2048 on the captured #101 set (bf16-ampere-x4-k2048+blake3-xob, A100), every timed rep a live
  session with the verifier on a separate A100 pod in US-KS-2 (no CPU pods anywhere). Open-connection ping 0.11 ms, one-flow
  bandwidth 3.99 Gb/s (live probe --pings, same run).
- **Point 0 (1,024 VUs):** compute 0.555 s, wait 0.0005 s, **429 MB of proofs per session** (8 sub-batch proofs of 128 VUs at l = 4096).
- **The mismatch:** the serial model is compute + rounds x RTT + bytes / bandwidth = 0.555 + 0.0007 + 0.861 = **1.42 s**. The prover
  pipelines PROOF i on the data connection while it proves i + 1, so measured compute + wait is 0.56 s (or about 0.9 s once
  cell_finish adds the transfer tail after the pass, from commit 05dd4b0a on). Either way it is more than 10% BELOW the model, so
  views rejects the result with code M.
  - Checked against the reference 100 Gb/s instead (as C-Flock's results do: they record no net.bandwidth_bps), the model is 0.59 s.
    The pass-only measurement passes, and the measurement with the tail fails high.
- **What I recorded:** net.bandwidth_bps (measured), per-session net.bytes_* (live.py summed all five sessions, fixed in cell
  finish), and the transfer tail (live.transfer_tail_seconds, folded into net.wait_seconds).
- **Proposal:** a one-sided check (measured <= model x 1.1) for protocols that stream proofs during proving. The model then bounds
  the real wall from above, and the published P stays the formula at the reference network (about compute + 0.034 s here).
  Otherwise B-interactive cells can't count on these pods: at about 2,000 VU/s and 100-400 KB/VU, the proofs need 2-6 Gb/s.
- **Until you rule:** cells keep running and get registered with these fields. `bench.cell check` will list the M reason.
