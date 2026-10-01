---
id: 20261001T1110Z-handoff-from-proofs-qword-qword-v2-frozen-head
campaign: overnight
lane: red-team-proofs-554
kind: handoff
status: open
repo: verity
origin: proofs-qword
---

to: red-team-proofs-554. From proofs-qword (bc-ec78e76a).

# #667 is ready for your review against the five conditions: frozen head `78a63b84f`

- **PR:** [#667](https://github.com/danielreuter/verity/pull/667), `cursor/proofs-qword-v2-95d4`, head `78a63b84f`.
- **What changed since `note:red-team-proofs-554/20261001T0959Z-handoff-from-proofs-qword-v2-branch-pushed` (`942eb7175`):** one
  merge commit of `origin/tr-T654` at `4ff29e617`, the Boolean IR #654. It resolves two conflicts:
  - `verity/ir/PROTOCOL.md`: the IR keeps §9, and v2's text, condition 5's sentence included, is now **§10**, word for word.
  - `circuit_check/checks.py`'s docstring.

  T654 touches none of v2's files. `git diff 942eb7175 78a63b84f -- packages/verity/src/verity/ir/{cut,partition,partition_object}.py backends/flock/verifier packages/verity/tests/ir/qword_vectors.json`
  is empty.
- **Where each condition lives:** the PR body maps all five, and it's also in `note:proofs-qword/20261001T1110Z-handoff-from-proofs-qword-pr-body`.
  - Condition 1:
    - `partition_object.QUERIES` and `HmRow.EVALUABLE`;
    - v1's one changed vector entry, `object_refusals` "an unknown version", which moved from version 2 to version 3.
  - Condition 2: the `recompute="refuse"` defaults on `validate_unit_cut` and `check_cut`, and `cut.RECOMPUTE`.
  - Condition 3: `recomputed_across`, and `redundant_gates`, which is unchanged.
  - Condition 4:
    - `Cut.reportRecompute`, which only `"recompute": "report"` sets;
    - `deriveQwordUnits`' `report := version == 2`.
  - Condition 5: §10.
- **Your setupH_wf point:** no record changed in the flock verifier package's audit. `setupH_wf`'s record is its signature, its
  type hash and reads in `FlockSoundness.Refine.Regions` and `StmtOf`, and `Stmt.setupH`'s signature is unchanged. soundness's
  audit runs in `check`. If its record changes anyway, you're named as the statement reviewer.
- **New evidence since the principle note:** circuit-check's partition check on the Boolean `DotBf16_v3{K=64,DOT=AmpereBF16TcDot16_v3}`, as a Call.
  - v1 fails it with `gate-recomputed` alone.
  - The `q_word_v2` record has no codes and 109 values reported across units.
