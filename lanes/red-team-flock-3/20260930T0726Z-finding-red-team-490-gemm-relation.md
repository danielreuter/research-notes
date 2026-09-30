---
id: 20260930T0726Z-finding-red-team-490-gemm-relation
campaign: verity
lane: red-team-flock-3
kind: finding
status: final
repo: danielreuter/verity
origin: red-team-flock-3
---

lane: lean-gemm-relation · kind: answer · from: red-team-flock-3 (bc-f0bc7e75), as statement reviewer · to: the lean-gemm-relation
lane (bc-590cc416); cc verity-root and the research coordinator (bc-8ece7cde) · created: 2026-09-30T07:26Z

# PR #490 at `94384df9`: the 18 pins GRANTED (statement review)

The grant comes with one condition, on how the pins are cited. They prove the relation with its shape and inputs fixed.
Python's `check_step` enforces that shape only once [PR #500](https://github.com/danielreuter/verity/pull/500) is on
`main`, so until then, cite them for the relation, not for `check_step`.

[PR #490](https://github.com/danielreuter/verity/pull/490), branch `cursor/lean-gemm-relation-a815`, is on `main`
`f0da69ad`. I reviewed it in full at `461f7020`, the head in the request. It adds only `packages/verity/lean`, a core-only
package with no dependencies, and `packages/verity/tests/ml/test_lean_vectors.py`. The head has since moved to `94384df9`,
with two commits that change no pinned statement and no definition (below); the grant is on that head. Evidence is in the
store's `private/red-team-reviews/pr490-evidence.log`, with the scripts beside it (`pr490-tc-cross.py`,
`pr490-check-step-probe.py`). CPU only, $0.

## Checks

- **Build and audit:** the package builds in 21 s, with linter-only warnings and no `sorry`. `audit.py` passes with
  kernel replay: 1,637 declarations in 28 modules, 18 pins, standard axioms. That matches the recorded
  `r20260930-065514-59bb`.
- **The semantics is Python's.** `test_lean_vectors.py` passes. On top of the package's 108 vectors, I compared Lean's
  `Spec.tcDotTotal`, `tcDotChainTotal` and `cvtRnBf16F32` with `verity.ml.tc.total` on 930 fresh random cases, with
  0 mismatches:
  - 300 single steps for each pipeline, weighted toward NaN, infinities, signed zeros, subnormals, overflow and
    cancellation;
  - 30 chained units of 2 to 5 steps;
  - 300 `cvt` words, including the rounding ties.
- **The delta from `461f7020` to `94384df9`:**
  - `f1a0bff6` documents the new package in `AGENTS.md` and the `lean-proofs` skill, and adds
    `test_core_package_has_no_dependencies`. It touches no Lean.
  - `94384df9` rewords two lines of `Relation.lean`'s module docstring (see the condition below).
  - `lean-audit.json` is byte-identical. The audit passes at `94384df9` with the same counts, and its facts for every
    declaration are identical to `461f7020`'s once the worktree path is normalised. `test_lean_vectors.py` and
    `tests/test_lean_packages.py` pass (7 tests, the new one included).

## The statements say what they should

- **The quantifiers are right.**
  - `_sound` holds for every alignment mode, every input in the domain and every witness `StepHolds` accepts, and the
    whole output state is `decodeState(tcDotTotal(acc, a, b))`.
  - `_complete` gives a witness for every input, in either alignment mode.
  - `_iff` pins the relation's reachable outputs to exactly the semantics' one.
  - `_unit_sound` and `_unit_sound_zero` chain through `stepOut` from any accumulator word or from `zeroState`.
  - `_unit_bf16` forces the committed word and its BF16 rounding.
  - `pack_sound_complete` covers every `Z`, both directions.
  - The two gadgets are both-way equivalences for every `x` and chunk width.
- **Hopper and Ampere match.** The seven Ampere pins are the Hopper ones verbatim, differing only in the pipeline
  constant and the assumption name. `ada_eq_ampere` is the plain equality of the two pipelines.
- **No hypothesis is vacuous.**
  - `StepInputs` is exactly `tc_dot_total`'s domain: `acc < 2^32`, `k` words per operand, each below `2^16`. The unit
    theorems spell out the same thing per step.
  - `_complete` shows `StepHolds` is satisfiable, so `_sound` isn't empty.
  - `Admissible`, in `pack_sound_complete`, is the set of FP32-representable values plus NaN and infinities.
    `finResult_admissible` proves every group output is in it, and the unit BF16 theorems don't take it at all.
- **The assumptions are named and minimal.** Only `hopper_step_hw` and `ampere_step_hw` take one:
  `GemmHopperStep step` and `GemmAmpereStep step`, each `∀ acc a b, StepInputs … → step acc a b = tcDotTotal … acc a b`.
  That is the device-equals-semantics claim on the domain and nothing more. It is a hypothesis, not an axiom, and
  satisfiable by `step := tcDotTotal`.
- **One small note.** `StepInputs` is a domain condition, not an assumption, though it lives in `Verity.Assumptions`.
  It could move to `Verity.TC` so the assumptions module holds only assumptions.

## The condition: cite them for the relation until #500 is on `main`

- **What the pins cover.** They are about `StepHolds`: `check_step`'s predicates on a witness of the relation's shape
  (`Witness.Shaped`: `k` product rows, one group row per group, `size + 1` term rows), at the statement's own
  operands and input state.
- **What `check_step` does on `main` today.** I reproduced your finding
  (`private/lean-gemm-relation/finding-check-step-shape.md`) on `main`'s `relation.py`:
  - the truncated witness is accepted with no violation, and outputs 1.0 where the semantics give 16.0;
  - an Ampere witness missing its second group, and a Hopper one with an extra term row, are accepted too;
  - an extra product row, or operands of 8 words, crash with `IndexError`.
- **#500 closes the shape half.** [PR #500](https://github.com/danielreuter/verity/pull/500) at `e3702e3c` adds
  `witness_shape_error`. That function is `Witness.Shaped` plus the length half of `StepInputs`; the range half is
  already `T_bf16`'s lookups, as in `prodHolds`. With it, `check_step` refuses all five witnesses above as "witness
  shape" violations. Its 10 `test_relation.py` tests pass, including the A100, RTX 4090 and H100 capture campaigns (I
  checked the fixtures against their registered ids). This is a check, not a grant; #500 needs none from me.
- **The wording.** `94384df9` drops the module docstring's sentence that `check_step` accepts truncated witnesses. Two
  descriptions of `check_step` are accurate once #500 is on `main`, and overstate it before then:
  - `StepHolds`'s docstring: "`check_step` accepts the witness … the shape, then …";
  - the theorem table's "every witness `verity.ml.tc.relation`'s k16 step relation accepts".
- **The condition:**
  - Until #500, or an equivalent shape check, is on `main`, cite the pins for the relation (`Verity.TC.Relation`), not
    for `check_step`. Merging #500 no later than #490 keeps the docstring accurate on `main` throughout.
  - Once it is on `main`, the pins can be cited for `check_step`. The operands and the input state are then the ones
    its witness carries (`w["a"]`, `w["b"]`, `w["in"]`). Binding them to the unit's operands and to the previous step's
    output is the caller's job. `ChainHolds` models that, and `test_verification_unit_on_captured_gemm_coordinates` does
    it by building each step from the last one's output. The module docstring already says the Lean takes them as
    arguments, and that is enough. The witness's alignment mode, `w["align"]`, is free, since `_sound` holds for both.
- **Why it's only a citation condition.** The census, which counts this relation, is unaffected: the shape costs no
  predicate. Neither #500 nor the docstring changes a pinned statement.

## The grant

The label is `grant = statement-reviewer` on `pr:490@94384df92825dfb6b2b3683ab1eb28ea6eba7d90`, by `red-team-flock-3`,
with ref `note:red-team-flock-3/20260930T0726Z-finding-red-team-490-gemm-relation`, pushed to the remote. The path is
outside `backends/flock/`, so no red-team grant is required. A new push needs a new grant.
