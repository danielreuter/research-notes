---
cursor:
  subagentId: "bc-c5df929f-2e80-576c-b7b4-7951b242e6b0"
---

lane: coordinator · kind: handoff (merge request) · from: pous (bc-c5df929f, the kernel-engineering skill) · created: 2026-09-30T16:42Z

# Merge request: #577, the kernel-engineering skill (docs only, no ordering constraints)

| PR | Branch @ head | Base | What |
|---|---|---|---|
| [#577](https://github.com/danielreuter/verity/pull/577) | `cursor/kernel-engineering-skill-e6b0` @ `63ff610a` | `origin/main` `fadd2e23` (merges cleanly onto `b1134766`) | `.agents/skills/kernel-engineering/SKILL.md` (new); one routing line in `AGENTS.md`; `authoring-skills` no longer recommends extra `.md` files that `tests/test_repository.py` rejects |

- **Docs only:** no code, circuit, Lean or `backends/flock/` change, so no `lean-agreement` and no `circuit-check` report.
- **No pinned statement or definition changed,** so no statement reviewer.
- **Tests:** `uv run tools/check/suites.py repository verity-check` passed, 32 and 112 tests, uncached.
- **Fits any train.** It waits on nothing, and nothing waits on it.
- **The companion kb doc** `kb/sm120-kernels.md` (the skill's living gotchas list) is already in the notes at `af06528`.
