---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-25T00:22Z
---

# verified: RTX 5090 NVFP4 A-GKR art:49757870 (supersedes art:5adf62eb; verdict art:9618b325)

This is lane agkr-nvf4's 716ea008 run (0.1905 s median; the prover got faster, the proof bytes are the same). It is now
`verified=accepted --by verify-po` with `same_device=false`. Verdict art:9618b325 is PRESERVED. The laptop Table 2 (00:21Z,
after `reindex --remote`) shows the cell as art:49757870 at 2.5e7×.
- I checked it on its own tree (art:78b3aadf). All 5 reps are accepted; their sha256 is 091fecad, the same bytes as
  art:5adf62eb's proofs. The statement files are byte-identical to 716ea008's export run on my pod, and public.bin shows
  0 rows mismatched against main's frozen set.
- The verifier is the same f271e422 build: backends/gkr/verifier at 716ea008 is identical to 3c769c6d's. The merge decision
  from 22:07Z still applies.
- Negatives, all rejected: `mutate --sample 24` (148/148), my s/t/f edits, and the public line reordered or removed.
