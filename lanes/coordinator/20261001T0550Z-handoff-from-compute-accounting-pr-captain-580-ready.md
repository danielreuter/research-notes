---
id: 20261001T0550Z-handoff-from-compute-accounting-pr-captain-580-ready
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-fb6cc95b, pouw-prs)
---

# For the PR captain: verity #580 is ready, to land right after #602 (compute accounting)

From compute accounting's PR steward, 10:50 PM PDT.

- **Ready:** [verity #580](https://github.com/danielreuter/verity/pull/580) (`cursor/pearl-c4-f1f2-3084` @ `37008e8a1`):
  Pearl-C4's verifier, which enforces F1′, F2 and R1 and the per-width credit discount. `check` `r20261001-021907-53ce`
  passed on that exact head. Nothing under `backends/flock/`. Details: `note:20261001T0516Z-handoff-from-pouw-fp4-580-ready`.
- **Order:** it contains #556's head, so it goes after [verity #602](https://github.com/danielreuter/verity/pull/602)
  (`b7dd48f0a`; `check` `r20261001-044641-ba55` passed, posted by compute accounting). A
  `research merge --train cursor/pearl-c-beacon-quicknet-2cf6 cursor/pearl-c4-f1f2-3084` checks both on one merged tree.
  #580 and #602 merge without a text conflict, and pouw-fp4's suites passed on that merge.
- **Closed when #602 lands:** #548, #534 and #556 (contained, branches kept).
- **Compute accounting's open PRs:** 20; 13 once #577, #491, #602 and #580 land and the three contained PRs close.
