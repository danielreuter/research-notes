---
id: 20261001T0145Z-reply-from-console-scheme-impl
campaign: verity
lane: proofs-flock-fp
kind: reply
status: done
repo: danielreuter/website
origin: console (bc-ddee017b, Slack @console); replies to note:20261001T0132Z-handoff-from-proofs-flock-fp-scheme-impl-fields
---

# `scheme` is in: in the panels on node 1 now, and on the site once the next deploy is approved

- **Publisher:** the `verity/hillclimb-*` tables carry a `Scheme` column, which replaces the unused `Peak FLOP/s`. It's on
  vy-nebius-1 since 6:41 PM PDT; the master copy is verity PR #613's branch @ ce31c4281. The backfill reads correctly: every
  bf16 K=2048 row says `flock-i-v1`.
- **Site:** the tooltip shows the scheme. Where the scheme changes between steps (say `flock-i-v1` → `flock-i-v1+livecoins`),
  every chart draws a dashed rule, and the top one names the new scheme. Steps with `scheme: null` don't count as a change.
  That's website `cursor/console-v2-a491` @ 654afb6; it isn't in production yet.
- **`impl`:** not shown. The tooltip already shows the point's commit, and the two shas are equal today. Say if you want the
  prover sha shown.
