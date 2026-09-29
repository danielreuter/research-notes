---
cursor:
  subagentId: "bc-51aad0a4-29e4-5b89-a799-383acbe93d5f"
---

lane: coordinator · kind: handoff · from: generated-outputs (bc-51aad0a4) · created: 2026-09-29T04:25Z ·
to: research coordinator (bc-8ece7cde)

# The notes cleanup is on `main`: `39d42a6c` + `7fb8c595`, a fast-forward from `4a313440`

- **`39d42a6c`** sets the render `out` outside the notes and adds the kb rules. It was `0171208f` / `6290938a` before the rebase.
- **`7fb8c595`** removes the 4,401 files. Before the push I re-hashed every removed path on `4a313440`: all 4,401 still equal
  the indexed store bytes.
- **Nothing was force-pushed.**
- **`research notes sync` needed one fix to push it.** Its key scan crashed on a non-UTF-8 diff (`UnicodeDecodeError`). The fix
  is in PR #360 as its own commit. The control pod's copy has the same bug: a commit that removes a Latin-1 or binary file
  makes its sync fail until #360 lands.

**Next, on root's go:** the remaining files under `renders/`, `campaigns/*/assets/` and `lanes/*/evidence/` go into the store
(631 at the last count, plus any added since). I verify each by hash, extend the index, and remove them in one follow-up commit.
I'll say here when that's on `main` too.
