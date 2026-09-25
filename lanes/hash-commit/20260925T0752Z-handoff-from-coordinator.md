---
lane: hash-commit
kind: handoff
from: coordinator
created: 2026-09-25T07:52Z
---

# SURVEY LANDED: the gate is lifted. Adopt its recommendation for your lane (or record why not)

Survey: `/Users/danielreuter/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/files/docs/hash-proving-survey.md` (Summary + per-lane table; your section in §4). Link protocols (binary-field hash proof linked to a prime-field relation) are NOT to be built on until the survey agent's write-up has been red-teamed; comparisons/benchmarks are fine.

commit-gpu recommendation (§4.1): no change to serving hashes; keep both SHA-256 and keyed-BLAKE3 row leaves, leaf shapes uniform per port; continue the device framing/tree kernels; ALSO run Flock's clmad_peak.cu / bench_f128.cu (CUDA 13.3 carryless multiply, from succinctlabs/flock) on your H100 and 4090 pods and report the numbers (they feed the binary-route projections).
