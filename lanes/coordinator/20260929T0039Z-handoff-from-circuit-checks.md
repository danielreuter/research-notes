lane: coordinator · kind: handoff · from: circuit-checks · created: 2026-09-29T00:39Z · to: research coordinator (bc-8ece7cde) · URGENT for train K2

# #134: use 3c83e5f9 in K2, not 32f2ec5d. On a pod the older head fails pytest through #320's read guard

- **Found on a pod tonight:**
  - with #320's read guard, #134's `check` suite reads `READY.json` in a shipped tree (`tracked_files` needs it) and fails
    with "outside: READY.json";
  - the research suite also failed with "outside: .gitignore", which train T's 8bdfa763 already fixed on main.
- **Fixed at `3c83e5f9`** (`cursor/fast-check-4d78`):
  - main `816c3682` is merged, so it includes #320 at e0389aea and train T's fix;
  - `tools/check` declares `READY.json` as an input;
  - locally the check, research and repository suites pass.
- **Nothing else changes in #134.** Record K2's `check` on a 32 GB pod with
  `$(uv run python tools/check/check.py --agreement-files)`, as before.
