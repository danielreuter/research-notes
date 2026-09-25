---
lane: flock-bench
kind: handoff
from: coordinator
created: 2026-09-25T08:30Z
---

# NEW PRIORITY: run Flock's prover on the binary-backend unit circuit + the BLAKE3 table at 4,096 VUs (decides binary backend vs link)

The survey agent found a pure binary-field (Flock) backend could plausibly prove relation + BLAKE3 leaves in about B-Ligero's
bare time (~1x overhead, no cross-field link); the link route comes out ~2.5-4x bare. Read:
- `/Users/danielreuter/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/files/docs/binary-backend-census.md`
- `/Users/danielreuter/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/files/docs/flock-link-protocol.md` (do NOT build on the link: it is queued for red-team review)
- the reproducible circuit + tests: `/Users/danielreuter/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/files/internal/binary-census/` (the exact unit circuit, bit-exact against verity.ml.tc:
  7,100 ANDs per BF16 unit, 681,631 per VU)

Make this your lane's priority (it decides binary backend vs link):
1. Flock's prover on that unit circuit and on the BLAKE3 table at our batch shape, 4,096 VUs, on the pod CPU and on the 5090
   (third-party GPU port): prove s, verify s, proof size, memory; scaling 64 / 1024 / 4096.
2. If feasible, A100 and H100 CPU/GPU rates (clmad_peak / bench_f128) so the projection covers the 80 GB lines.
3. Report as a handoff "flock-bench: binary backend numbers" with the comparison against B-Ligero bare on the same lines
   (current Table 2 B-Ligero cells) and the census projection.
Budget raised to  (cap); FINAL moves to 15:00Z (8:00 AM PT).
