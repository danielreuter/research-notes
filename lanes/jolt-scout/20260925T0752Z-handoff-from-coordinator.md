---
lane: jolt-scout
kind: handoff
from: coordinator
created: 2026-09-25T07:52Z
---

# SURVEY LANDED: the gate is lifted. Adopt its recommendation for your lane (or record why not)

Survey: `/Users/danielreuter/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/files/docs/hash-proving-survey.md` (Summary + per-lane table; your section in §4). Link protocols (binary-field hash proof linked to a prime-field relation) are NOT to be built on until the survey agent's write-up has been red-teamed; comparisons/benchmarks are fine.

Your recommendation (§4.5): use Jolt's BLAKE3 inline instruction (648 cycles; keyed 64-byte variant 646) rather than SHA-256 (1,900 cycles) for the committed guest; measure one committed VU's cycles on CPU; find what ICICLE actually accelerates (MSM, sumcheck) and BN254's ~100-110-bit level. The survey notes absolute speed (0.5-1.5 MHz on CPU, no CUDA in the repo) is the issue: report go/no-go accordingly.
