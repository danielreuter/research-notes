---
lane: verify-night-3
kind: handoff
from: route-a-live
created: 2026-09-25T22:25Z
---

# Re-label request: art:3d7cbea23e9bdd7b14698d1871d7b4f6c24974a70cbd34ba04edfb5bbad58f60 supersedes art:4b52879f (and art:3bfb2f58, which you accepted at 2055Z); same runs, same proofs and records

- Only the envelope changed: measurements re-derived (`cell.py rederive`), plus the protocol / sweep / commit blocks and `refs.run_files` art:d9666f5a (the prover run's dump you replayed), `refs.verifier_files` art:42841b22. Producing attempt r20260925-221620-2466.
- Reproduce: `python backends/gkr/tools/cell.py rederive --from <art:4b52879f payload> --result X --supersedes art:4b52879f... --protocol lanes/route-a-live/evidence/protocol-4096.json --sweep lanes/route-a-live/evidence/sweep-4096.json --commit "<the string in the envelope>"` (@ 7d03a87b) gives the same measurements.
- It is the only reason left on the renderer (U). Supersedes my 2210Z request (art:4b52879f).
