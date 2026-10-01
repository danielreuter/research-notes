---
id: 20261001T0728Z-handoff-from-proofs-zero-open-prs
campaign: overnight
lane: proofs-mufu
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Daniel's new goal: zero open PRs at 7:50 AM PDT

to: proofs-mufu (bc-e8b97b26-6308-54d5-bdf0-c6c684725c15).

Daniel, 12:11 AM PDT: at 7:50 AM PDT every proofs PR is either landed or closed with its branch kept and listed in proofs'
backlog. Don't open a PR that can't land by then.

- Keep building on `cursor/proofs-mufu-bool-95d4` from the frozen IR head `46c768b2c`, and push after every commit. The
  1:45 AM PDT checkpoint stands.
- The MUFU tables get a PR only if, by **6:15 AM PDT**, their exact head (stacked on the IR) passes `circuit-check` for every
  new Definition and `uv run --extra torch-cpu python tools/check/check.py --record --on vy-nebius-1`. Node 1's queues hold
  5:10–5:55 AM PDT, so record it before 5:10 or right after 5:55.
- Either way, by 6:30 AM PDT write to `lanes/proofs/`: the branch, the head, the sizes per table, and the check's run id or why
  there isn't one. Work that misses goes into proofs' backlog, branch kept.
