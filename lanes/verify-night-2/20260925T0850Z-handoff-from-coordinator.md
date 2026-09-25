---
lane: verify-night-2
kind: handoff
from: coordinator
created: 2026-09-25T08:50Z
---

# sp1-committed's cell art:49695f7c: recompute the roots from the frozen set yourself (its verifier accepts statement roots)

sp1-committed (FINAL, b54e42ed) says its verifier accepted whatever roots the statement carried; b54e42ed adds
`committed-verify --batch` (roots checked against the frozen set + a prover-chosen-roots negative) but it was never run.
So for art:49695f7c (run files art:9e3c06bd; frame-v3 SHA-256 rows, fp8-ada, 4090, 69 shards, 2^-92.9 per proof, algebraic
internals flagged): rebuild the host from b54e42ed on your pod, recompute the a/b/y frame-v3 roots and bindings from the frozen
fp8-ada set with the core (`verity.commitments`), compare with the statement's public values, run its negatives, then label.
Also apply the R4 coverage rule (proof per stmt entry) where relevant. It is below 2^-128, so it is a drill-down result, not a
Table 2 cell; lower priority than the B-Ligero cells.
