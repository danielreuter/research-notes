---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: pous
kind: handoff
from: coordinator
created: 2026-09-30T03:00Z
---

# coordinator -> POUS (PoUS and PoUW work; cc verity-root, vLLM coordinator): direction change, each protocol measured on its own

**The change (Daniel via root, 02:52Z).** We're no longer combining PoUW, PoUS and sampled proofs; the combined pipeline was an
integration test. What's wanted now is clean measurements of each protocol on its own, then hillclimbing each one's efficiency
and security. The plan is `docs/protocol-measurement-plan.md`: metrics, the clean harness, the baseline, the first targets and
the hardware, per protocol.

**What this means for your work:**
- **Stops or pauses:** extending the combined pipeline.
  - **#367** (`protocol_options` admitting PoUW beside sampled proofs): don't rebase it onto #423. It's paused.
  - **#372/#380/#391** (granted, built as train TPS on TW6c): I'm holding TPS unlaunched until root says whether the stack
    still matters in the new direction. Tell root if it's needed for a PoUW-only measurement.
- **Lands as is:** #364 and #423 are in TW6c, already in flight, and land as the integration test's record.
- **What's next, for PoUS:** a PoUS-only harness. Encode, keep `C` resident, run timed audits, and measure decode overhead on a
  synthetic loop. No vLLM serving and no PoUW. Hardware: an exclusive RTX 4090 node with stable clocks and fast NVMe.
  - **Baseline:** fill in the band MVP's encode GB/s, decode overhead and audit latency.
  - **First targets:** decode overhead; the audit deadline margin; closing the random-oracle caveat.
- **What's next, for PoUW:** a PoUW-only bench on fixed matmul shapes (W1 on a 4090), with no served model.
  - **Baseline:** redo #389's and #435's numbers there, since they were taken through the served pipeline.
  - **First targets:** fused-kernel prover overhead, samples per bit, and γ_0/Ω*.

File each harness and its baseline run as ordinary PRs and merge requests; they come through the trains.
