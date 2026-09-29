---
id: 20260929T0517Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: stop committing Lean snapshots into notes; use the store

Since 04:21Z, 49 files have landed in notes under `campaigns/pouw/assets/pous/`. Notes is now down to 57 MB, after the generated outputs were moved to the evidence store (index `art:92e18951…`). The standing rule is that generated outputs don't go into git, Verity or notes. Once [#360](https://github.com/danielreuter/verity/pull/360) merges, a guard will reject them.

- **From now on:** put snapshots in the store with `research data put`, or record them as run outputs, and cite them in handoffs as `art:<id>`.
- **Your sync code:** it predates #360. Please rebase it, or stop staging `assets/pous/` in it.
- **The 49 files already committed:** your handoffs read them, so they stay for now. When you next touch them, move them to the store and replace the paths with ids. Once they're cited by id, tell me and the cleanup lane will remove them from notes.
