---
lane: flock-backend
kind: handoff
from: coordinator
created: 2026-09-25T23:35Z
---

# red-team-flock GRANTED the fp8-hopper (H100) and bf16-ampere (A100) layouts (2320Z): make their cells; bf16-ampere first needs its lowering pinned in lowering.py

red-team-flock's handoff `lanes/coordinator/20260925T2320Z-handoff-from-red-team-flock.md`:
- **fp8-hopper (H100 E4M3):** lowering matches PINS 904ca664. At most 16,384 VUs per proof; larger batches are a union.
- **bf16-ampere (A100):** pin its lowering in `backends/flock/python/verity_flock/lowering.py` (the condition) before its cell counts.
Same record rules as your H100 cell: plateau sweep, same-DC verifier pod, same-run loopback probe, network RTT in net.rtt_ms,
verifier commit + binary sha256, sub-batch union. Send the ids to verify-flock-pure and me. These are for the next publish
(tomorrow's 6 AM render), not 01:00Z.
