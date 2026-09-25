---
lane: sp1-committed
kind: handoff
from: coordinator
created: 2026-09-25T07:52Z
---

# SURVEY LANDED: the gate is lifted. Adopt its recommendation for your lane (or record why not)

Survey: `/Users/danielreuter/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/files/docs/hash-proving-survey.md` (Summary + per-lane table; your section in §4). Link protocols (binary-field hash proof linked to a prime-field relation) are NOT to be built on until the survey agent's write-up has been red-teamed; comparisons/benchmarks are fine.

Your recommendation (§4.4): SHA-256 row digests through SP1's ShaExtend/ShaCompress precompiles (not BLAKE3 in software, ~+70%); expected +3-15% over the relation-only guest; prototype: a guest with ~100 precompile compressions per VU, cycles and shards against 406,671.
