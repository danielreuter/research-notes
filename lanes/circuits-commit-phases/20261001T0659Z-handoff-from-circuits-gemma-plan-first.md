---
id: 20261001T0659Z-handoff-from-circuits-gemma-plan-first
campaign: verity
lane: circuits-commit-phases
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: priority. Measure fix 1 on a Gemma-2-2B i1024 row: its pre-run planning holds a GPU about 25 min

- **The evidence:** cov-cg10 (Gemma-2-2B B16 i1024/o128 top-p, tree cursor-coverage-v1-2622), from `timeline.jsonl`:
  - `engine.build` 06:32:39–06:36:16Z (209 s), `prep.warmup_control0` 5.5 s;
  - then a **16-min gap to `prep.committer_setup`** (06:36:22 → 06:52:31Z): the required-value manifest load and the acquisition plan;
  - then committer setup (hidden, fa2 and norm-scale taps attached, JIT) for 8+ more minutes.
  - All on one core with the GPU at 0%. Five such Commits held five node-1 GPUs at 11:57 PM PDT.
- **What to do:** make this row (or Gemma-2 B8 i1024 greedy, cov-cg05) one of your golden rows. Report how much of the 16-min plan
  and the committer setup moves into the 0-GPU plan task.
- The grid runs on `cursor/coverage-v1-2622`, so once fix 1 is proven, port it there (cherry-picks, no force). circuits-replay-keep-leaves
  owns node 1's tree sync; leave it a handoff with the head. The advisor's no-draw-before-root constraint still applies.
