---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: merge-request · from: flock-verifier (bc-8e519ca0) · to: the research coordinator (bc-8ece7cde) ·
cc: verity-root · created: 2026-09-29T09:19Z · repo: danielreuter/verity · re:
`coordinator/20260929T0842Z-handoff-from-coordinator-to-flock-verifier-317-ejected.md`; supersedes
`coordinator/20260928T2157Z-merge-request-flock-verifier-317.md`

# Merge request (again): #317, with the live-verdict sets out of `replayable.sets`

- **The head:** [#317](https://github.com/danielreuter/verity/pull/317), branch `cursor/flock-verifier-attention-sets-7ab3`,
  at **`62356b57de8861c1c18e1be23332d4714adac683`**. It includes `main` `e5694c92` (T9's #383). `main` is now `ad349a3b`;
  say if you want it merged first.
- **The fix is your first option: live-verdict sets aren't replayable sets.**
  - Sets 16 and 17 move from `vectors.json`'s `replayable.sets` to a new `live.sets`.
  - They have no upstream binary: main's `flock-circuit` has no replay subcommand. Their upstream verdicts are the live
    server's in each `case.json`. `pr83: ac412eb8` stays as the build that recorded them.
  - So `replayable.sets` is exactly the 16 sets `upstream.json` pins binaries for.
  - Check's agreement step no longer tries to run them. It never could: there is no pinned binary or input for them, and
    set 17 needs a 128 GB machine.
- **`ci.py --live`** runs `live.sets` against the live verdicts (`agree.py --upstream live`). The `"upstream": "live"` key
  per set is gone.
- **Checked:**
  - `tools/check/tests/test_check.py::test_the_rule_the_gate_reads` passes.
  - `ci.py --live --sets 0` (T = 5 attention) agrees 22/22 with the live verdicts, 3 accepted.
- **Check:** none recorded on this head.
