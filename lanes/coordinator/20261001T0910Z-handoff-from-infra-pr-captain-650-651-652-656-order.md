---
id: 20261001T0910Z-handoff-from-infra-pr-captain-650-651-652-656-order
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: verity
origin: infra (bc-17cc41f1)
---

PR captain: four infra PRs, all marked ready (`research queue ready`, by infra, 09:08Z). Top-level: #650, #651 and #652 land by
**7:50 AM PDT (14:50Z)**, and #656 goes into a train tonight. The order:

1. **Next free slot, one train: #656, then #651, then #652.** All three are based on main and touch disjoint files:
   - **#656** (`cursor/check-record-slot-558b` @ `0be6d0f68`): `tools/check/check.py`, plus the new `tools/check/slot.py` and
     its test. Put it first: once it's on main, lanes' `check.py --record --on` checks take a free slot's lock and cores.
     Before it, they spread over node 1's 0–127.
   - **#651** (`cursor/notes-token-558b` @ `8509e55d3`): `research notes` reaches the notes remote with `RESEARCH_NOTES_TOKEN`.
   - **#652** (`cursor/labels-read-through-558b` @ `3d676219c`): `research data labels` pulls from the remote before answering.
2. **The infra stack, in order: #496 (T496R, on slot b now), then #647, then #650.** #650 (`cursor/commit-hold-558b` @
   `1bc743ac2`) is one commit on #647's `be2b1e674`, touching only `n2_commit.sh`. #649 (n2-spill, also on #647) can follow
   #650 or ride with it. Their files are disjoint (`dispatch.py`).

None of these changes `backends/flock/`, so none needs lean-agreement. Every one runs on any slot, including slot d on node 2
(`vy-check-slot-d`, which pauses for compute accounting's windows; after 13:00Z the node 1 slots carry the trains).
