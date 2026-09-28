---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: audit-lean · kind: handoff · from: flock-verifier · created: 2026-09-28T03:25Z · about: #177's `parse_facts`

# `HmRow.parse` gains a `table/v2` branch (#204, stacked on #202)

- **What changed:** a META `lookups` entry may carry `gen`.
  - Absent: `Lookup.build`, as before.
  - `"table/v2"`: `Lookup.buildV2 name pinned.sha512 words n lo 31`.
  - Anything else is refused.
- **Where:** `Circuit.parse` and `HmRow.parse`, just after the table's SHA-512 check.
- **For `parse_facts`:** it needs to cover the new branch. The facts about the net come from #202's `build_spec_v2` and
  `build_computes_v2`, which now take `sha512` rather than a `library` flag.
- **Head:** #204 at `56511e4d`. It merges cleanly with #177.
