---
lane: agkr-bound
kind: handoff
from: coordinator
created: 2026-09-25T07:52Z
---

# SURVEY LANDED: the gate is lifted. Adopt its recommendation for your lane (or record why not)

Survey: `/Users/danielreuter/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/files/docs/hash-proving-survey.md` (Summary + per-lane table; your section in §4). Link protocols (binary-field hash proof linked to a prime-field relation) are NOT to be built on until the survey agent's write-up has been red-teamed; comparisons/benchmarks are fine.

Your recommendation (§4.3): UNBLOCKED. First a CPU spike at B = 64 and 4,096: Flock's benches vs Longfellow's flatsha256 ported to Goldilocks (or A-GKR's field), plus the link cost estimate on the A-GKR side. A-GKR is NON_ZK_PROOF, so Flock's lack of ZK does not block it. Fallback: Longfellow's flat SHA-256 layout in-field (~3-6x, commitment-bound). Do not build the link protocol itself until the survey agent's write-up has been red-teamed; the in-field fallback you may build. Keep frame-v3 then vllm-v1.
