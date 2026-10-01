---
id: 20261001T0608Z-handoff-from-proofs-review-554-statements
campaign: verity
lane: red-team-flock-3
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs), on Daniel's overnight goal (10:58 PM PDT)
---

# Review request: #554's statements, so the hillclimb points can drop `draft-554-unreviewed`

to: red-team-flock-3 (bc-f0bc7e75), statement reviewer of record for C-Flock. Thanks for #638's grant.

Daniel's overnight goal (due 7:50 AM PDT) is overhead against K for BF16, E4M3, NVF4 and MXF4 at all four K, with the
`draft-554-unreviewed` flag cleared. Every hillclimb point carries it, because the trees build on #554
([draft](https://github.com/danielreuter/verity/pull/554), head `8a0b17250`; the flock-fp tree is at that head, the
bf16-hill tree at `9967b96b6`, 13 commits behind). `gemm_hill.py` adds the flag unconditionally: "#554 is a draft, its
statements unreviewed: these are costs, not claims".

Two questions, in this order:

1. **Non-tile points (no `FLOCK_GEMM_TILE`):** does #554 change any statement byte against main for `GemmCoordinate_v2`
   and the E4M3/NVF4/MXF4 coordinates? #554's title says its changes are tooling, pipelined witnesses and two
   byte-identical kernel fixes, which would leave statements alone. If you find them byte-identical (a staged statement
   digest on main against one on `8a0b17250`, or a code read you trust), grant that, naming the digests or the scope.
2. **The 4x4 tile statement** (BF16 K=2048 step 2, `FLOCK_GEMM_TILE=4x4`): the statement and pins review M0 asked for
   (`note:20260930T1235Z-report-prover-morning-inputs`, decision 1).

When either grant lands, the lanes change the flag to fire only outside what you granted. Write the verdict to
`lanes/proofs/`. A CPU staging job on node 1, if you need one, goes through me (the research owner clears jobs).
