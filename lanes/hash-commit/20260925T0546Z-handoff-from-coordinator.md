---
lane: hash-commit
kind: handoff
from: coordinator
created: 2026-09-25T05:46Z
---

# PAUSE (user): Poseidon2 is dropped from the committed relation; stop optimizing it at the next clean point

User decision (10:45 PM PT): Table 2 commitments must use NON-algebraic hashes (SHA-256 and BLAKE3 to be benchmarked); Poseidon /
algebraic hashes are out. Your Poseidon2 committer work is therefore paused:
1. Stop at the next clean point: commit and push what you have, register and preserve every result you measured (their numbers
   stay useful as a baseline), note the state in your report.
2. Terminate your pod now (the retarget, SHA-256/BLAKE3 committing, possibly B-Ligero binding through its own BLAKE3 Merkle
   commitments with no in-proof hash, is still being designed and will not be ready within the hour).
3. Checkpoint `blocked` ("waiting for the SHA-256/BLAKE3 retarget"), keep polling your inbox every ~10 min, and resume only on the
   coordinator's retarget handoff. Do not spend more budget on Poseidon2.
