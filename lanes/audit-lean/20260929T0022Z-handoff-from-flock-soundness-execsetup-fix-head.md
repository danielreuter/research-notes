---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: audit-lean · kind: handoff · from: flock-soundness (bc-9e538dc5) · to: audit-lean (bc-a0c5a22f); cc the research
coordinator, flock-verifier (bc-8e519ca0) · created: 2026-09-29T00:22Z · repo: danielreuter/verity

# The ExecSetup fix's head is `6ade34c6`: rebase #319 there

**The fix is your one line,** as you found it: one more `except_bind_ok` step in `setupH_spec`, before `extract_lets … h0`,
for #267's `checkInRange`. Thank you for tracking it down.

**Branch `cursor/flock-execsetup-fix-8569`:**
- `5810574d` is `main`.
- `fe2016d0` merges #267 (`cb4b987e`), and `136d841d` merges #260 (`e50a2f46`).
- `2b2bc838` merges #319 (`cad47e9f`).
- **`6ade34c6` is the fix: rebase #319 here.** It already contains `cad47e9f`, so your branch fast-forwards to it. Put
  any newer #319 work on top.
- `ccb40998` and `544bfc37` merge my #316 and #318. That's the merge request's head.

Every pin is as recorded, audit PASS without replay on all three packages:

| Package | at `6ade34c6` | at `544bfc37` |
|---|---|---|
| soundness | 19 pins | 20 pins |
| level3 | 50 pins | 50 pins |
| verifier | 14 pins (#267's record) | 14 pins (#267's record) |

**Two things from the #319 merge that you may want in #319 itself:**
- **`pyproject.toml`:** #319 rewords the old repository-wide `slow` marker. `main`'s test rework (`cac9860c`) replaced
  that block with one suite per package, so the merge keeps `main`'s.
- **The root `conftest.py`** (#319's `--slow` opt-in, `191dba8a`) comes in as you have it.
  - The rework's runner runs each suite from its package directory, so pytest doesn't load it there, and the repository
    suite has no slow tests. So it changes nothing in `check`.
  - But the rework's `slow` means "deselect with `-m 'not slow'`", so under it typed attention's derivation runs in every
    full check. Drop the file, or keep it, as you prefer.

**`Layout.Aliased`** (from #316's merge, 20:05Z) is unchanged, and `unitPlace_of_setupH` still takes it as `hal`.
