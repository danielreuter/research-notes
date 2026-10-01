---
id: 20261001T1051Z-handoff-from-circuits-circuit-check-table
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (3:51 AM PDT): circuit-check table for PR 1 is done; three small things for the body or the head

The table is the store's `internal/circuits/bool-integration-circuit-check.md` (circuits-bool-rope, bc-8fa9e530). All 178 Boolean targets on
`b06cf4ae4` pass standalone, with 0 word-view mismatches. As-call `gate-recomputed` shows on 13 targets, with counts. Cite it in the PR body.

- **Your head `23f2018c6` adds element-wise's merge**, whose 45 targets its lane checked green on `9366d8afc` (`art:9257ee13…`). The PR
  still needs a `circuit-check --all` on the final head; `check --record` gives that.
- **Five gather ids error when run by id** (`GatherBf16x1024u10_v1`, `GatherBf16x1100_v2`, `GatherBf16x2u22_v1`, `GatherBf16x64_v2`,
  `GatherBf16x76u10_v1`: "not in the registry"). `targets.definition` can't build them; only `boolean_gather.gather_bf16(n)` does. They
  pass through `suite()` and `--all`. Use `--all` in the PR's commands. If the fallback to `suite()` is a few lines, add it; otherwise say so in the body.
- **18 targets warn `lowering/unpinned`** (listed in the table). If `--all` treats a warning as a failure, pin their AND counts in
  `pins.json`; if not, pin them anyway if it's cheap.
