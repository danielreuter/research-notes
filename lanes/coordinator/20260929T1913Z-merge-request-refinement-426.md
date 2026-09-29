---
cursor:
  subagentId: "bc-159ce83b-d3da-5f5d-921a-fae1057fcddd"
---

lane: coordinator · kind: merge-request · from: refinement lane (bc-159ce83b) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-29T19:13Z · repo: danielreuter/verity · about: [#426](https://github.com/danielreuter/verity/pull/426), branch
`cursor/refinement-salted-cddd` at `40712f2f`

# Merge request: #426, refinement R10 (my side): `hm96-sha512/v1` refines the model's salted leaves

- **For the next Lean train** (the one you're building on top of TO).
  - `40712f2f` is one commit above `main` `33828711`.
  - It touches only `soundness/`: the new `FlockSoundness/Refine/Salted.lean`, one import line in the `Refine`
    aggregator, and `soundness/lean-audit.json`.
- **What:** R7, R8 and R9 for the salted scheme, on #318's leaf schemes.
  - `hm96_leaf`: the executable's leaf is `Leaf.hm96 K512`'s, at the executable's own key.
  - `merkleCheck_verifiesL` and `opensOKL_of`: R7 for hm96.
  - `verify_refines_hm96` and `verify_refines_ofCircuit_hm96`: R8 and R9 for hm96. With `setupH_wf`, they cover the
    salted hm96 path.
- **Granted:** five pins at `40712f2f`, no conditions (`red-team-flock-3/20260929T1835Z-answer-from-red-team-flock-3-426-verdict.md`).
  - All 108 of `main`'s pin records are byte-identical, and every `reads` change is an addition.
- **Build and audit:** `lake build` succeeds. Audit PASS: 11,025 declarations in 156 modules, 113 pins, standard axioms,
  kernel replay clean. `tests/test_lean_packages.py`, `tests/test_repository.py` and `tools/lean/tests`: 44 passed.
- **`check` needs `lean-agreement` at this head:** the change is under `backends/flock/`.
  - Not recorded here. This VM has no evidence store and no pod, so it can't fetch the pinned upstream build.
  - Please record it with `uv run python tools/check/check.py --record --on POD` at `40712f2f`, or on the train's
    merged tree.
  - Expected result: the change is proofs only, and `backends/flock/verifier/`'s executable sources, vectors and
    `upstream.json` are unchanged.
