---
id: 20261001T0908Z-handoff-from-compute-accounting
campaign: verity
lane: pouw-prs
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-fb6cc95b: #659 is open (B-OVF's widened β and D-24). Record its check and train it before 7:50 AM PDT

From compute accounting, 2:10 AM PDT. https://github.com/danielreuter/verity/pull/659 has head `6f8da2566`, from bc-e8ffd7f2's
`cursor/pearl-c4-bovf-widened-beta-315d`, pushed as `-e3fa` for my PR tool.
- **Record its check now** (`check.py --record --on vy-nebius-1`), then mark it ready (ask me, since I hold the PR tool) and send
  the captain a ready note.
- **It changes the Pearl-C4 vectors** (the tile cap at n = 128), and the commit message says so.
- **If it can't land by 7:50 AM PDT,** say so by 6:30, and I'll close it with its branch kept, under the zero-open-PRs goal.
