---
id: 20261001T0707Z-handoff-from-compute-accounting
campaign: verity
lane: pouw-lean
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-dd9ede96 (pouw-lean): stop writing the store copy now. M5 lands on the repo copy

From compute accounting, 12:10 AM PDT. Daniel wants PoUW's Lean out of the Project store now, and lean (bc-19c498a8) owns the
move into `protocols/pouw/lean/`. The cutover terms are in `lanes/lean/20261001T0707Z-handoff-from-compute-accounting.md`. Your part:
1. **From now on, write nothing to `internal/pouw-lean/`.** The store copy freezes at M3b: 665 pins, `lean-audit.json`
   `43ba801d…`, `art:0d156c69…`.
2. **M5 goes on the repo copy.** Keep the restage, the red-team review and the assessor's re-grant going as they are. Then
   rebase M5 onto lean's import branch, or onto `main` once the import lands, in your own checkout and `.lake`, and run
   `verify_merge.py` against the repo layout. It lands as a PR. If it's ready before the import, it waits.
3. **When lean's import lands,** add one line to the store README: "moved to `protocols/pouw/lean/`, read-only since <time>".
4. M2b stays held, and you open no other PR: we're at the PR cap.
