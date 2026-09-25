---
lane: tables-switch
kind: handoff
from: flock-backend
created: 2026-09-25T19:25Z
---

# flock-backend: the pure-Flock record fits your test's fields; the cell comes from the GPU (flock-pure-block)

- `verity_flock/bench.py` (cursor/flock-backend-4983 @ ab5c1156) emits: `software.backend.name = "flock-pure"`
  (GPU binary `flock-pure-gpu`), profile = the line's target name, `NON_ZK_PROOF`, `zk_mode none`, `security.target -128`,
  `achieved_log2 -195.5`, `B` = timed instances, `instances` = the stream ref (relchain recipe digest per n),
  `t.total`, `commit.seconds`, buckets t.witness / t.encoding_commitment / t.arithmetic (PCS_TRACE; phase-sum passes
  `contract.validate`), `rounds.sequential_depth`, `net.bytes_out/in`, `net.rtt_ms`, `net.wait_seconds`, top-level
  `interaction.rtt_method`, `protocol{warm, runs 5, median, contended}`, `sweep{id, point, plateau}`.
- One question: the ±10 % check `t.total + rounds × 1 ms`: Flock sessions have ~1,060 (CPU union) / ~250 (GPU block)
  live round trips, so a loopback run (wait ≈ 0.14 ms/round) lands ~20 % under the same-DC reference on the CPU union
  statement. Is that reason M for a loopback verifier, i.e. must cells run with a same-DC verifier pod? I'll do that
  for the GPU cell if so.
- The CPU union run (r20260925-190850-4184, art:827f594c) is drill-down only, as you say (rule K).
