---
id: 20261001T1110Z-handoff-from-proofs-qword-pr-captain-qword-v2-ready
campaign: overnight
lane: coordinator
kind: handoff
status: open
repo: verity
origin: proofs-qword
---

# For the PR captain: `Q_word` v2, #667, frozen head `78a63b84f`, needs lean-agreement

From proofs-qword (bc-ec78e76a). This is 35 minutes ahead of the 11:45Z ask.

- **PR:** [#667](https://github.com/danielreuter/verity/pull/667), branch `cursor/proofs-qword-v2-95d4`.
- **Head:** `78a63b84f403961702cba8c71fe52d6bd6a2630e`, frozen and pushed. It's a merge commit of `origin/tr-T654` at `4ff29e617`
  (the Boolean IR), so it trains on T654, as proofs' 10:18Z note asked.
- **Needs:**
  - `lean-agreement`, because the PR touches `backends/flock/verifier/lean/` (`Flock/Partition.lean`, `Extract.lean`,
    `HmRow.lean`, `Main.lean`).
  - Slot d, 5:00–5:30 AM PDT, or node 1 before 5:15 AM PDT, whichever the lander scheduled.
  - If T654 is re-cut and `tr-T654` moves, tell me in `lanes/proofs-qword/` and I'll merge whatever you name.
- **Run here on the frozen head:**
  - suites: verity, repository, verity-circuit-check, and verity-flock with the Lean build and the agreement checks, all pass.
  - Five flock tests were OOM-killed by other lanes' load on this VM, and all five pass when rerun alone.
  - `circuit-check --all` wasn't run here, so `check` gives the first full run.
- **Audit:** `audit.py --build` on the flock verifier package passes with no record changed, so no statement reviewer is needed.
  level3's and soundness's records are compared in `check`.
- The PR body is in `note:proofs-qword/20261001T1110Z-handoff-from-proofs-qword-pr-body`. proofs marks #667 ready.
