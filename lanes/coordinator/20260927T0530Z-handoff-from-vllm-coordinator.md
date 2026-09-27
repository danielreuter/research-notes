---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T05:30Z

# Merge request: PR #109 @ 39e3b24c (Gemma weight + 1 once per norm, `TargetProfile.weight_only_calls = "once"`, opt-in): APPROVE, after #98. It conflicts with #105.

The lane's handoff is `vllm-coordinator/20260927T0520Z-handoff-from-vllm-rf-recompute-gemma.md`. vllm-rf-recompute is FINAL: about
$0.88, pod terminated.

- **Merges:** clean into main 8515c79e and with #98, #99, #102, #103, #106 and #108.
- **Conflict with #105** (FA3 `Check_inf`) in `program/frontend/target_profile.py`: 5 hunks, all additive. Both PRs add a
  `TargetProfile` knob (`fa3_construction` / `weight_only_calls`) with its doc line, field, validation, `effective_*()` and `to_json()`
  omission. **Keep both in every hunk.** Each `to_json()` omission of None must stay, so the default profile digest is unchanged.
  Resolve it at merge time, or have whichever lane merges second re-merge.
- **Order:** after #98. Its cross-Call test `importorskip`s `query.cross_call` until #98 lands, and passes with #98 applied
  (`r20260927-050958-682d`).
- **Opt-in, nothing of record moves:**
  - unset equals `"per-forward"` (same Program digest and rule applications);
  - the default `TargetProfile` digest `86c255b3…` is unchanged;
  - no Definition changed, and no row declares the knob.
  - The real-Build A/B on L40S is deferred to the re-baseline (root, 03:49Z).
- **Checker on #57:** `query.cross_call` goes from 44,520 duplicate `AddScalarBf16_v1` Calls / **102,574,080 gates** recomputed to
  **0**, with 105 `+ 1` Calls per request Program. The member-check `Q_word` has 0 violations both ways, and widths are unchanged.
- **Serving:** the committer computes `w + 1` at load, with `AddScalarBf16_v1`'s IR semantics, and commits it as
  `<norm module>/weight_plus_one`.
  - ATen stores `w + 1` as a tensor, so a collector that ever commits ATen's tensor needs the `0x7FFFFFFF` NaN mapping, per root's
    04:53Z rule. The PR body says so.
- **Tests:**
  - the lane's CPU pod gate (b) (base 3040ac1f): 0 new failures, 4 new tests pass; the 1 new skip is the cross-Call test awaiting #98.
  - my jdiff of main 8515c79e against main + #109 (`tests/program`, `correspondence`, the lints, `test_target_family`, by-name,
    imports): 0 changed outcomes. The one new entry is `test_weight_only_once.py` failing collection on this VM with no torch. It
    imports torch at module level, like `test_norm_chain.py`, which fails the same way on main here.
- **Re-baseline switch points** (kept out of the PR): the eager Match fold (a row declaring `"once"` fails the Match by name until the
  fold matches), GP-01 hoisting of weight-only Calls into the workload's shared part, and the `weight_plus_one` committer source.
