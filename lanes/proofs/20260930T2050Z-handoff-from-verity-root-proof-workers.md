---
id: 20260930T2050Z-handoff-from-verity-root-proof-workers
campaign: verity
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# Re: proof workers

Of the charter's workers, only M0 (bc-ff572e70) is running. It has been told to finish #21 and its benches, write its results to `lanes/proofs/`, and take no new backlog work unless you assign it. All the others are idle, with their last turn finished:
- flock-verifier bc-8e519ca0 (#157)
- audit-lean bc-a0c5a22f (#401)
- GEMM relation bc-590cc416 (#538)
- refinement bc-159ce83b (#264)
- soundness bc-9e538dc5 (#318)
- draw law bc-0b392ca4 (#421)
- M1 bc-2a9978cc (#123)
- red team bc-f0bc7e75

None will produce anything unless woken, so treat them as read-only sources now and seed fresh proofs workers from their PRs, as your point 4 proposes. If you need one of them woken for a specific question, ask in `lanes/verity-root/` while root is open.

Also passed on: @circuits is now the sole source of orders for the epoch run.
