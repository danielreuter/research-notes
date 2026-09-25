---
lane: flock-backend
kind: handoff
from: coordinator
created: 2026-09-25T18:36Z
---

# Pure-Flock cell = the batch-size plateau, not 4,096; record rounds/bytes/RTT/compute-vs-wait for interactive runs

**Daniel's direction: every Table 2 cell is the maximal-batching throughput plateau on its hardware.** No lane reports a
fixed 4,096-instance batch as the cell. Sweep batch size upward (e.g. 4,096 -> 8,192 -> 16,384 -> 32,768 -> ...) until
instances/s stops rising or memory runs out, report the plateau point as the cell, and keep the smaller points as the
sweep. Rule I applies to every re-packed or regenerated set (an instance-equiv/v1 document per size).

**Every interactive result records** (from now on; a reporting standard is coming to kb/TABLES.md once Daniel confirms):
rounds; bytes up and bytes down; measured RTT between prover and verifier; and the split of wall time into prover compute,
verifier compute and network wait. Put them in the result record (bench-result/v1 fields or its measurements block) and in
your report. Name how RTT was measured.
