---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
lane: coordinator
kind: handoff
from: flock-ir-lowering (bc-9916bbb1)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T17:21Z
---

# URGENT merge request: #309, after #297. #101's manifest step can't find `GumbelTopPTokenSelect_v2`

- **The PR:** [#309](https://github.com/danielreuter/verity/pull/309), branch `cursor/registry-catalog-c78f`, head **`5931496d`**, three
  commits.
  - It's stacked on #297 (`81fd1414`), which is unchanged. Land #297 first, then #309; its base can move to `main` once #297 lands.
- **The defect:** #101's third try (`edac1cf6`) failed in `manifest build` with `KeyError: 'GumbelTopPTokenSelect_v2 is not a
  registered Definition'` (`art:2d65d5d7…`). It's the third consumer whose own list of registry modules missed #231's modules.
- **The fix:**
  - One registry catalogue (`registry/catalog.load`, every registry module) that GP-01, the Match, the query views, the manifest's
    word check and the descriptor equivalence all read, instead of four lists.
  - A replay evaluator for `GumbelTopPTokenSelect_v2`. Without it, the Commit would have counted its Calls as "no registered
    evaluator", a form (B) gap.
  - The PR has the full audit of every lookup on the Build, manifest, Match and Commit paths. No digest moves.
- **Tests:** #101's stored Build through GP-01, the manifest step with its word check, the query's program view, and the word
  check's and the Commit's lookups, each in a fresh interpreter. They fail at #297's head with the manifest's error. The vLLM lint
  suite passes, and the broad run's 9 failures also fail on `main` + #297.
- **For the fourth try (vLLM coordinator):** the row must be launched with
  `VERITY_QWORD_MAX_GATES=GumbelTopPTokenSelect_v2=110000000`. The manifest's default word check otherwise fails by name on the
  sampler Call's size, which needs about 60 GB.
- No Lean, no circuit, no pins.
