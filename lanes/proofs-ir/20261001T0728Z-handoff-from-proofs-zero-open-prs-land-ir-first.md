---
id: 20261001T0728Z-handoff-from-proofs-zero-open-prs-land-ir-first
campaign: overnight
lane: proofs-ir
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Daniel's new goal: zero open PRs at 7:50 AM PDT. Land the IR first; nothing else gets a PR unless it can land

to: proofs-ir (bc-6cd83494-c180-583c-83f9-ef70e4b3f19b).

Daniel, 12:11 AM PDT: at 7:50 AM PDT every proofs PR is either landed or closed with its branch kept and listed in proofs'
backlog. Don't open a PR that can't land by then. Node 1's queues hold from 5:10 to 5:55 AM PDT, and trains' checks run there.

1. **The Boolean IR on main is the one that must land.** At 12:15 AM PDT node 1 had no check of the frozen head `46c768b2c`.
   Run it now from a clean checkout of that head: `uv run --extra torch-cpu python tools/check/check.py --record --on vy-nebius-1`
   (it sends the upstream build for `lean-agreement`). If `main` (21 commits ahead) conflicts with it, merge `main` once, then
   freeze and check that head.
   - Send me the run id, the head and a circuit-check report in `lanes/proofs/` the moment it passes. I open the PR and ask
     for the train.
   - **Hard limit: a passing check by 4:00 AM PDT**, so the train runs before the 5:10 hold. If that slips, the last chance
     is a check passing by 6:15 AM PDT, trained after 5:55.
   - Known trap: check's Lean audit fails on vy-nebius-1 for any package it must re-audit from scratch (a symlinked cache).
     #642 fixes it and trains next. If your check fails only there, merge `cursor/check-lean-audit-resolved-scratch-95d4`
     into your head and re-run; say so.
2. **Attention and FP8/FP4** stay on `cursor/proofs-ir-attn-95d4`, stacked on the frozen head. They get a PR only if a passing
   check of their exact head exists by 6:15 AM PDT. Otherwise write the branch and head to `lanes/proofs/` by 6:30 AM, and
   they go into proofs' backlog.
3. Push after every commit.
