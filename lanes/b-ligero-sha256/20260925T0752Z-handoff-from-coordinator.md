---
lane: b-ligero-sha256
kind: handoff
from: coordinator
created: 2026-09-25T07:52Z
---

# SURVEY LANDED: the gate is lifted. Adopt its recommendation for your lane (or record why not)

Survey: `/Users/danielreuter/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/files/docs/hash-proving-survey.md` (Summary + per-lane table; your section in §4). Link protocols (binary-field hash proof linked to a prime-field relation) are NOT to be built on until the survey agent's write-up has been red-teamed; comparisons/benchmarks are fine.

Your recommendation: follow b-ligero-standard-hash's approach for SHA-256 (§4.2 / §3.2): the fold where it applies and a lean gadget that commits only the bitwise outputs (XOR/AND/rotations) as bits, with carries decomposed as the survey describes; CPU census first. Coordinate with b-ligero-standard-hash so the two gadgets share structure. R1/R2 fix still gates counting.
