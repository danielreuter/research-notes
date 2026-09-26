---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-26T00:37Z
---

# verify-flock-pure: all five current Flock cells are verified=accepted as file re-verifications (1589ffe1, c3e83404, 7afeecbe, 167e64a8, 56f792bd); pod terminated 00:36Z; lane spend about $2.8

| cell | result | verifier run | sessions replayed | replay run | verifier built from |
|---|---|---|---|---|---|
| H100 BF16 | art:1589ffe1 | r20260925-233818-a37e | 60/60 | r20260925-235824-1a5c | 0864d146 (+replay) |
| H100 E4M3 | art:c3e83404 | r20260925-234513-abf3 | 66/66 | r20260926-000935-dd35 | e52eca82 (+replay) |
| RTX 4090 E4M3 | art:7afeecbe | r20260925-234753-f84e | 54/54 | r20260926-000935-dd35 | e52eca82 (+replay) |
| A100 BF16 (frozen set) | art:167e64a8 | r20260925-235045-9b93 | 18/18 | r20260926-000935-dd35 | e52eca82 (+replay) |
| H100 E4M3, vllm-v1 | art:56f792bd | r20260925-232101-016f | 48/48 | r20260926-002803-d4e8 | ff1c1e3f (+replay) |

- **Each cell's checks:**
  - My instance files match the verifier pod's by sha256. For the A100, the frozen bench-instances/v1 arrays were rebuilt
    and checked against the committed manifest; for vllm-v1, the step roots were checked under the port domains.
  - The netlist is the pinned one, and Σ, the honest publics and `link_sha256` are recomputed here.
  - The proof files are the recorded ones, and so are the prover's plateau proofs.
  - Both reps verify over the recorded coins on the committed root, and 12 tampered-record negatives behaved as expected.
  - Recorded coins are replayed, so this is not transferable evidence.
- **Also labelled accepted, now pulled:** bb289d47, ed0047be, fb526e50, 37215309.
- **Code:**
  - lane/verify-flock-pure @ 0f933bbf: replay subcommand for flock-pure-gpu plus 31-replay.sh, on flock-backend e52eca82.
  - lane/verify-flock-pure-vllm @ f9ada8e7: replay subcommand for flock-vllm-v1, on ff1c1e3f.
  - Both are merge candidates alongside their bases. The verifier paths are unchanged.
