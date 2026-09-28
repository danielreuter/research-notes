---
id: 20260928T0724Z-handoff-from-pous-to-coordinator
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous (worker bc-51d80f1e-a453-50ad-81ea-731440def4fc)
---

# Merge-ready: verity#240 (the approach registry) @ 1c559b63, `check` PASSED as r20260928-053910-3af7 (PRESERVED)

**The tip:** `cursor/approach-registry-f4fc @ 1c559b63`, base main@6746f408. It changes `tools/research` only. It merges cleanly with the current main `3ba4d8b3` (#224, #241); I haven't merged main in, so a train can take it as it is.

**`check`:** `r20260928-053910-3af7`, rc 0, on a clean tree at 1c559b63, with every leg PRESERVED on R2:
- pytest: 3,177 passed, 42 skipped;
- circuit-check: passed;
- lean-build and lean-unit-cut: passed;
- lean-audit: PASS on all three packages (the verifier, `level3` and `soundness`);
- lean-agreement: skipped, since no bundle was sent.

**No pinned statement or Lean file changes**, so there's no statement reviewer.

**Known conflicts,** with the consolidation coordinator's ready PRs:
- #216: `notes.py` and `tools/research/README.md`;
- #235: `store/vocab.py`.

Whichever lands second resolves. If #240 lands first, the consolidation coordinator rebases both. If one of them lands first, I merge main into #240 (no rebase, no force-push), resolve, and re-record `check`.

**Still open from my 05:40Z handoff:**
1. **The `[approaches]` table in `steward.toml`,** after the merge: `store = "/workspace/steward/store"`, `every_min = 10`.
2. **The lane-contract §3b section** (text in that handoff), and the "New agent? Start at `kb/onboarding.md`" line in the notes README.
3. **Done, on Daniel's go-ahead:** the backfill of 64 POUS and PoUW approaches is in the store. All 64 read back from the remote with the intended status, and `approaches check` gives 0 errors and 0 warnings. `campaigns/pous|pouw/APPROACHES.md` are rendered in the notes (`6df14b72`).

The consolidation coordinator adds the `AGENTS.md` sentence once #240 is on main (its 05:58Z answer). Replies to `lanes/pous/`.
