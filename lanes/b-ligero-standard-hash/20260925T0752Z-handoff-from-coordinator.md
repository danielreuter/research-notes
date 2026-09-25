---
lane: b-ligero-standard-hash
kind: handoff
from: coordinator
created: 2026-09-25T07:52Z
---

# SURVEY LANDED: the gate is lifted. Adopt its recommendation for your lane (or record why not)

Survey: `/Users/danielreuter/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/files/docs/hash-proving-survey.md` (Summary + per-lane table; your section in §4). Link protocols (binary-field hash proof linked to a prime-field relation) are NOT to be built on until the survey agent's write-up has been red-teamed; comparisons/benchmarks are fine.

Your recommendation (§4.2): NOW the x2 fold plus a lean BLAKE3 gadget that commits only the XOR outputs as bits (the survey's XOR-output-bits design); target in-field ~3.5-5x bare. Prototype first: a CPU census of the new gadget. The binary route (shared Flock-style hash proof + public-coin bit link) waits for Flock ZK and the red-teamed link write-up. Keep the first cell (existing gadget) as the overnight target if the lean gadget is not ready in time; R1/R2 fix still gates counting.
