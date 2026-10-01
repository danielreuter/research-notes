---
id: 20261001T1018Z-handoff-from-proofs-merge-tr-t654-into-667
campaign: overnight
lane: proofs-qword
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Merge `origin/tr-T654` into #667 and resolve two files; it must be in the 4:45 AM PDT head

to: proofs-qword (bc-ec78e76a-4dc7-5fce-a5a9-147c82f16aa2). From proofs, on the PR captain's finding
(store `internal/lanes/proofs/20261001T1018Z-handoff-from-pr-captain-667-conflicts-with-ir.md`) and the top-level's instruction.

- **Why:** #667's train on slot d (about 5:20 AM PDT) stacks on T654, the Boolean IR (`cursor/proofs-ir-95d4` @ `46c768b2c`).
  #667 merges cleanly onto `main`, but conflicts with the IR in two files. I reproduced it: merging `origin/tr-T654` into
  `942eb7175` conflicts in exactly
  - `packages/verity/src/verity/ir/PROTOCOL.md`;
  - `tools/circuit_check/src/circuit_check/checks.py`.
- **Do:** `git fetch origin tr-T654` and merge `origin/tr-T654` (`4ff29e617`, which carries the IR at `46c768b2c`) into
  `cursor/proofs-qword-v2-95d4` with a **merge commit, not a rebase**. Resolve both files so each keeps both sides: the IR's
  PROTOCOL.md text and v2's paragraph (conditions 1 and 5 of red-team's grant); the IR's Boolean checks and v2's whole-cut
  record in `checks.py`.
- **Then re-run** the suites the merge touches (verity, verity-circuit-check, verity-flock with the Lean build and agreement
  checks) and `circuit-check --all`, on the merged head. Put the merged head in your PR-body note as the frozen head, by
  **11:45Z (4:45 AM PDT)**, and send it to the captain in `lanes/coordinator/` too.
- **If T654 is re-cut** (T656, T1 or T654 fails and `tr-T654` moves), say so in your lane, and merge whatever the captain
  names instead (`main` once T654 lands, or the new tip).
- Nothing else changes: draft PR [#667](https://github.com/danielreuter/verity/pull/667); red-team reviews the frozen head at
  about 12:05Z.
