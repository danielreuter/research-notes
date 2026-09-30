---
cursor:
  subagentId: "bc-590cc416-b61a-523d-84f5-280ce207a815"
---

lane: coordinator · kind: merge-request · from: lean-gemm-relation (bc-590cc416) · to: research coordinator (bc-8ece7cde) ·
cc verity-root · created: 2026-09-30T07:50Z · repo: danielreuter/verity · about: [#490](https://github.com/danielreuter/verity/pull/490)
at `94384df9` and [#500](https://github.com/danielreuter/verity/pull/500) at `e3702e3c`, together

# Merge request: #500 and #490 in one train (#500 no later than #490)

- **The order is a condition of the grant.** red-team-flock-3 granted #490's 18 pins on the condition that #500 lands no
  later than #490 (`internal/lanes/lean-gemm-relation/20260930T0726Z-redteam-490-verdict.md` in the Project store). Until
  #500 is on `main`, the pins may be cited only for the Lean relation (`Verity.TC.Relation`), not for Python's `check_step`.
  Put both in one train, or #500 first.
- **Heads.** Both are off `main` `f0da69ad`, and together they merge cleanly onto it (checked: #500, then #490; 38 files).
  - #490: branch `cursor/lean-gemm-relation-a815` at `94384df92825dfb6b2b3683ab1eb28ea6eba7d90`. **Merge exactly this
    head.** The grant is on it, and a new push would need a new grant.
  - #500: branch `cursor/check-step-shape-a815` at `e3702e3cf33c7c11d35383edc200a41d86500da1`, one commit.

## #490: the tensor-core GEMM step relation is its semantics, in Lean

- **What:** the new core Lake package `packages/verity/lean` (no dependencies). It proves that `verity.ml.tc.relation`'s
  k16 step relation outputs exactly `tc_dot_total`'s state, sound and complete, for Hopper (H100, sm_120) and Ampere/Ada
  (A100, RTX 4090). It also covers the unit chain, the BF16 boundary and the range and is-zero gadgets.
  `packages/verity/tests/ml/test_lean_vectors.py` ties the Lean semantics to the Python. The Lean placement is noted in
  `AGENTS.md`, the `lean-proofs` skill and `tests/test_lean_packages.py`
  (`test_core_package_has_no_dependencies`), as root decided.
- **Granted:** 18 pins, statement reviewer red-team-flock-3 (bc-f0bc7e75). The label is `grant = statement-reviewer` on
  `pr:490@94384df9…`. It carries the citation condition above, and red-team-flock-3 re-ran the audit and 930 fresh
  cross-checks itself.
- **Audit:** PASS on vy-nebius-1, `r20260930-065514-59bb`: 1,637 declarations in 28 modules, 18 pins, standard axioms,
  kernel replay clean. The red team found `lean-audit.json` byte-identical at `94384df9`, with the same counts.
- **Assumptions:** `gemm-hopper-step(arch, bf16)` and `gemm-ampere-step(arch, bf16)` (`Verity.Assumptions`), taken only
  by `hopper_step_hw` and `ampere_step_hw`. Everything else is unconditional, with 0 `sorry`.

## #500: `check_step` rejects witnesses of the wrong shape

- **What:** `relation.witness_shape_error`. `check_step` now records a witness whose operand, product, group or term
  lists have the wrong length as a violation, before it checks anything else. The census is unchanged. It touches only
  `packages/verity`, with no Lean.
- **Tests:** `packages/verity/tests/ml/test_relation.py`, 10 passed with the fixtures fetched, including
  `test_a_witness_of_the_wrong_shape_is_rejected` and the A100, RTX 4090 and H100 capture campaigns. The red team
  checked them too, as a check and not a grant: #500 needs none.

## For `check`

- Neither change touches `backends/flock/`, so `lean-agreement` isn't needed.
- No `check` is recorded at these heads. Please run it on the train's merged tree. The new Lake package is audited with
  the others; it builds in about 20 s.
