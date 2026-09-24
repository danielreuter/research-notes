---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-24T23:56Z
---

# verified: RTX 5090 NVFP4 A-GKR art:5adf62eb (supersedes art:ad8f92b9 and art:fe57e68b; verdict art:4791cc89)

This is lane agkr-nvf4's best attempt (2b25df7f, 0.245 s median), now `verified=accepted --by verify-po` with
`same_device=false`. Verdict art:4791cc89 is PRESERVED. The laptop Table 2 (23:52Z, after `reindex --remote`) shows the
cell as art:5adf62eb at 3.3e7×.
- The verifier is the same f271e422 build: `backends/gkr/verifier` at 2b25df7f is byte-identical to 3c769c6d's. The merge
  decision from 22:07Z still applies.
- All 3 proofs are accepted with the expected counts: 700 slots, 1689 msgs, 9467080 bytes, 11666 rows. Each takes 0.63-0.79 s.
- The circuit (one table, `LK 89119`), epilogue, chain and manifest are byte-identical to 2b25df7f's export run on my pod.
  public.bin equals main's frozen (s, t, f), with 0 rows mismatched.
- Negatives, all rejected: `mutate --sample 24` (148/148), my s/t/f edits, and the public line reordered or removed.
