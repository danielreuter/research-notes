---
id: proofs/20261005T1059Z-finding-red-team-move
campaign: layout-move
lane: proofs
kind: finding
status: final
repo: danielreuter/verity
origin: red-team-move
---

# Red team pre-review: layout move c863067f5, red-team scope

**Verdict at c863067f5 (and at its branch head c507d376b, which adds the hand commits): REFUSE, with 2 blocking items.**
Everything else in scope is the move's own renames, or is fixed by the hand commits on the branch.

- Reviewed: the generated commit `c863067f52e318b615e672915a53e1a5f2f9731d` (base `8bb1a7942`) and the branch
  `cursor/layout-move-0955-c3b2` at `c507d376b3a4a35b6bfbc89d248399467b2ff7d3`. Its seven hand commits touch flock:
  521981c78, 4c4b327ad, b339e1cb6, 88bc09e41, c4931cc65, c4cef0463 and 5445b909f.
- Scope: `backends/flock/` minus `README.md`, `PROTOCOL.md` and `*/tests/*`, as in `tools/check/queue.toml`'s red-team grant.
- Evidence: `art:94ad49b3fb45227640b072a5a0c3e27b72525934a5e8909f6fc210abbeb3dadb`. It holds the classifier's output, the
  mechanical pair list, every log cited below, and the tools in `tools/`.

## Blocking

1. **The prover's statement identity changes.**
   - The change: `backends/flock/live/src/bin/flock-circuit.rs:217`, `"coin_derivation": "sha256 (verity.randomness)"`, became
     `"sha256 (verity.primitives.randomness)"`. The dotted-name rule rewrote a protocol constant.
   - Why it matters: `identity()` is "the backend identity the statement digest pins". The Lean verifier recomputes the
     statement digest from its own `tags.identity` (`verifier/lean/Flock/Statement.lean:196`). Its `identityHm96`
     (`Flock/Tags.lean:186-200`) and the older tags still say `sha256 (verity.randomness)`; `*.lean` is excluded from the
     rewrite, rightly.
   - Effect: a post-move build gets a statement digest that the Lean verifier doesn't recompute, in the default seeded-coin
     mode and in ZK mode. Only `FC_COINS=os` overrides the field. The Lean verifier refuses every such proof. That fails
     closed, but every default statement digest moves (stage keys, recorded digests) and every new proof is refused.
   - Why nothing catches it: `test_lean_live_os.py::test_the_live_os_identity_is_the_provers` compares only the
     `FC_COINS=os` override block. The recorded sessions predate the move.
   - Evidence: `tools/identity_drift.py` (`logs/identity-drift.txt`) finds 0 differing texts at the base and 1
     (`coin_derivation`) at both c863067f5 and c507d376b.
   - Fix: put the literal back in a hand commit. Make the generator never rewrite this string, for example with a
     literal-text keep: `keep_dotted` is global and would also block real `verity.randomness` references. Extend that test
     to compare the whole default `hashes` object with `identityHm96`; `identity_drift.py` is the check, about 30 lines.

2. **13 of the 15 pod scripts tested can't import the catalog, and two checks become vacuous.**
   - Cause: the pod venv is bare, numpy and blake3 only (`pod/20-pure.sh:21` and the same line in the others), so imports
     resolve from `PYTHONPATH` alone. The move turned `$REPO/packages/verity/src` into `$REPO`. What used to be under
     `verity.ml` now lives in `catalog/`, `kernels/` and `experimental/`, and each needs its own entry. Hand commit b339e1cb6
     added them only to `pod/70-class-sweep.sh:77` and `arch_proto/serve_staged.sh:31`.
   - Lines still missing them at c507d376b: `pod/20-pure.sh:23`, `30-cell.sh:22`, `31-replay.sh:19`, `33-ir-cell.sh:27`,
     `34-ir-replay.sh:22`, `34-ir-sampling.sh:22`, `34-ir-selftest.sh:21`, `40-vllm-v1.sh:22`, `50-preflight.sh:20`,
     `60-circuit.sh:40` (M0), `61-circuit-cell.sh:24`, `74-gemm-hill.sh:182` and `76-read-gadget.sh:74`. Also the Python
     `sys.path` in `live/src/sha512_native.rs:627`.
   - Simulation (`tools/pod_imports.py`, pod-like venv, each script's own `PYTHONPATH`): 0 failures at the base and 27 at
     the head, all `ModuleNotFoundError: No module named 'verity_catalog'`. See `logs/pod-imports-*.txt`. These fail loudly.
     Two fail open:
   - a. `live/src/sha512_native.rs:622-640`. `slot_circuits()` prints "skipped" and returns `None` when its Python fails.
     `native_witness_matches_eval64_on_the_pinned_slot_circuits` then iterates over no plans and passes. That test pins both
     slot circuits and their plan digests. At the head the snippet fails under any `python3` without verity-catalog
     installed; at the base it builds the circuits (`logs/sha512-native-slot-circuits.txt`). Under `check` (`uv run`, the
     workspace venv first on `PATH`) it probably still runs. On a pod or in a bare environment it passes vacuously.
   - b. `pod/gemm_hill.py:568-572`. `_validate` returns `["contract unavailable: …"]` on `ImportError`. Under
     `74-gemm-hill.sh:182`'s `PYTHONPATH`, `verity_numerical.bench.contract` no longer imports (it needs verity_catalog).
     For `mxf4` (no campaign target, `_bare_result`), status stays `passed`, so the script's
     `grep '"status": "passed"' result.json` passes without the contract check having run. At the base, `_validate` runs
     the contract (`logs/gemm-hill-validate.txt`).
   - Fix: add `$REPO/catalog:$REPO/kernels:$REPO/experimental` after `$REPO` in the 13 lines (`$SRC` in `34-ir-sampling.sh`),
     and `'{r}/catalog', '{r}/kernels', '{r}/experimental'` in `sha512_native.rs:627`. Checked in the same simulation with
     the three entries added: 0 failures, `prims()` registers 129, and the snippet imports
     (`logs/pod-imports-head-c507d376b-with-groupings.txt`).
   - A sturdier fix: the generator emits the three groupings wherever `[tokens]` rewrites a `PYTHONPATH` or `sys.path`
     entry of `packages/verity/src` to the root.

## Non-blocking

3. `live/src/bin/flock-circuit.rs:3172`: the JSON key `"census"` became `"catalog/census"`; the bare-word path rule applied
   `census/` → `catalog/census/` to it. It is the `native_sha_matches_eval64` selftest's informational field: nothing reads
   it, and `pass` is computed separately. Restore it in the commit for item 1. In the generator, a bare word with no `/` in a
   Rust or other non-Python file shouldn't get the path rewrite.
4. The generated commit alone leaves the code identities short.
   - At c863067f5, `FLOCK_PURE` and `FLOCK_CLASS_SWEEP` lose 65 and 57 files of the catalog, kernels and experimental
     (`tools/closures.py`). `_source_digest` names `verity.protocols.accounting.work.pouw` but not the catalog, kernels or
     experimental, so changing silicon code would give a stale stage-cache hit.
   - Hand commits 521981c78 (`tool.py` `CORE`) and 4c4b327ad (`class_statement.py:1001`) fix both. At c507d376b, every old
     closure file maps to a covered new path except three groups: the 16 `verity.proofs` modules, now in `archive/sp1`;
     `verity_vllm/check/codes.py` and `query/units.py`, for `FLOCK_PURE` only; and the 6 dropped files of item 5.
   - The flock code imports none of these on those paths. `20-pure.sh` has no `integrations/vllm` on its `PYTHONPATH`, and
     `backend.py`'s `verity.proofs.target` is now `verity_catalog.targets.target`, which `CORE` covers.
   - **The final regeneration must keep 521981c78 and 4c4b327ad.** If they get folded into the generator, rerun.
5. The move drops 6 tracked files, all under `backends/numerical/tests/bench/data/flock-runs/r20260925-233831-a064/out/`
   and `r20260925-233818-a37e/out/` (`binary.sha256` and four session logs). The new `.gitignore` pattern `out/` matches them,
   and the generator's re-add skips them. This is outside red-team scope (`benchmarks/numerical`), and is for @top.
   `test_cell.py::_real_runs` copies them, so it should fail loudly.
6. Pre-existing, unchanged by the move:
   - `circuit.rs:3575` skips (`else { return; }`) when core's hm96 vectors are missing. The new path exists, and its
     contents are the same apart from the regenerated about string.
   - `boolean_export.prims()` swallows each registry module's import error.
   - `check.py`'s `rust_tests_inputs` keys the `flock-rust-tests` cache without the Python that `sha512_native`'s test reads.
   - `$REPO/protocols/one_stage` in two `PYTHONPATH`s was already dangling (764dcb02e).
   - The upstream patch `flock-sha512-b684b12.patch` and `verifier/vectors.json` keep old names in comments and data,
     correctly, since they're excluded.
7. Lean, Rust and CUDA.
   - Under `backends/flock/verifier/lean/`, only `soundness/ASSUMPTIONS.md` and `soundness/FlockSoundness/Audit/README.md`
     change. No flock `lean-audit.json`, lakefile or manifest changes. Lean doc comments keep the old names (Lean is excluded).
   - Rust and CUDA changes beyond comments are four lines, `flock-circuit.rs:217`, `:3172`, `circuit.rs:3575` and
     `sha512_native.rs:627`, covered above. `cuda/sha512.cuh` changes a comment only.

## What holds

- **Pairs.** 283 of the 285 changed line pairs in scope are mechanical. They use 165 distinct substitutions, each resolved:
  the old name exists at the base, the new one at the commit, and the blobs are mostly identical or at least 0.96 similar.
  - `verity.ml` → `verity_catalog.definitions` is 0.60, because that is the split package's `__init__`. It is used only in a
    docstring and in `from … import gemm/scalar/mufu`, whose targets are the moved modules themselves.
  - The 2 others: `pyproject.toml:6` adds the verity-catalog, verity-experimental and verity-kernels dependencies.
    `python/verity_flock/instances.py:29` changes `parents[3] / "direct"` to `parents[4] / "archive" / "direct"`; it
    resolves, since `instances._ligero()` imports `archive/direct/ligero` (`logs/instances-ligero.txt`).
- **Verifier agreement.** The 5 core vector files the Lean agreement tests pass (format, partition, qword, qcall and
  template_instance) are byte-identical at their new place. `_ir_tests()` finds them through the import system, and a missing
  one fails `test_the_reference_vectors_exist`, without a skip. No `*agree*.py` reads a vector by a hard-coded path; they
  take them as arguments.
- **Import fallbacks.** In scope, no `try/except ImportError` (or broader `except`) guards an import of a moved name, except
  `gemm_hill._validate` (item 2b) and `prims()` (pre-existing). `instances.py:165` guards only `import blake3`.
- **Tests at c507d376b**, in a `/tmp` worktree after `uv sync --all-packages --extra torch-cpu`:
  - `test_class_statement.py`, `test_class_statement_redteam_1178.py`,
    `test_lean_live_os.py::test_the_live_os_identity_is_the_provers` and
    `test_lean_verifier.py::test_the_reference_vectors_exist`: 27 passed.
  - The whole `backends/flock/tests` with `-m "not slow"`: 395 passed, 8 skipped, 10 failed and 53 errors, all
    environmental (`logs/pytest-flock-head-notslow*.txt`).
  - Of those: the agreement scripts' subprocesses ran the system `python3`, which lacks the workspace, and they need the
    Lean binary. `lake build` wasn't run, as the brief asked. The store fixtures (`hidden-outputs`, the
    `tc-total-2026-09-07` captures) weren't fetched; their registered paths in `fixtures/artifacts.json` are the new ones.
    `check` runs all of these.

## Classifier, and the rerun on the final commit

- **What it does.** `tools/classify.py COMMIT` pairs each removed and added line of `git diff -M -U0 COMMIT^ COMMIT` in scope.
  It labels a pair "mechanical" only when every differing token is an old name that the commit's own
  `tools/move/layout_map.toml` maps to exactly that new token. The map's sections are `[modules]`, `[aliases]`, `[paths]`,
  `[tokens]` and `[roots]`. Token forms: a dotted module, `from A import b` (through `A.b`), a root-relative path (with a
  `$VAR/`, `{r}/` or `{ROOT}/` prefix), a path relative to the file, or a path relative to an old package root.
  - It checks the last entry of `moves.json` against `[paths]`; they are equal at c863067f5.
  - It resolves every substitution at both ends.
  - It flags mechanical pairs that sit in code rather than in comments, docstrings or imports. There are 30 at c863067f5,
    every one reviewed by hand; items 1 and 3 came from that list.
- **Counts at c863067f5.** 70 files; 283 mechanical pairs (157 import, 47 comment, 45 docstring, 16 shell, 12 code string,
  4 doc, 2 toml data) and 2 others; 165 substitutions, 0 unresolved.
- **Digests at c863067f5.**
  - Mechanical (file, old, new multiset): `6a2bd5b86f17d7c87aa4d3ddf27bc23fd3971c8446e88edbc6dc28bff714e014`.
  - Other: `5f709de71201ccd7e592f49372f72fa728895cd6b75de77dee7dcaca403547f8`.
  - Code-context pairs: `4fdb0644d7875f7c616936bd56b8281fca6fa79c77c2f8fb5e79e859111d57aa`.
- **Rerun** (about 10 s; tools in `/tmp/rt-move-tools`, or `art:94ad49b3…/tools`):

  ```
  git -C /workspace fetch origin <move branch>
  bash /tmp/rt-move-tools/rerun.sh <generated move commit> <branch head>
  ```

  It prints the counts and digests beside c863067f5's, then the branch's flock commits after the move and their diff in scope,
  the closures from base to head, the identity drift, the pod imports and old names left in scope, and the dropped files. The
  classifier alone is `python3 /tmp/rt-move-tools/classify.py <commit> --repo <worktree> --out <dir>`. When the mechanical
  digest differs, run `diff <(cut -f1,3,4 /tmp/rt-move-out/mechanical-c863067f5.tsv | sort) <(cut -f1,3,4 OUT/mechanical-<short>.tsv | sort)`.
  The first file is also in the art, as `classify/mechanical-c863067f5.tsv`.

## Final: GRANT (red-team) at #1206's head 62cf02978 (by proofs, 11:35Z)

#1206, `cursor/layout-move-1045-c3b2` at `62cf0297857964779cf9c10ca200537d7f299aa4`, has move commit `f0dde01ec` on main `b9ac23dfc`.
Its four new hand commits are f5143e269 (`layout.py` keeps `.rs`/`.lean` string literals), 0f8ff1188, 68eae1722 and 62cf02978.
`bash /tmp/rt-move-tools/rerun.sh f0dde01ec 62cf02978` gives the following (evidence `art:57c391ba9473c65057fe3ea93329b6214f3c79fec3532da1578dc31343412595`):
- **Rename digests:** the mechanical, other and code-context digests are equal to `c863067f5`'s, so the generated commit's red-team scope is
  the pre-review's.
- **Blocking 1 is fixed.** The identity drift between the prover and Lean `Tags` is 0. `flock-circuit.rs` is byte-identical to main's.
  Every changed Rust string literal in scope is a path (`repo.join`, the slot snippet's `sys.path`); the rest are comments.
  Under `verifier/lean/`, only two `README.md` files change.
- **Blocking 2 is fixed.** Pod-import failures on the pod-like venv are 0 (27 at `f357ec26d`). `sha512_native.rs`'s snippet now
  lists `catalog`, `kernels` and `experimental`.
- **Dropped tracked files:** none. The 6 `flock-runs/*/out/` files are back.
- **Closures:** `tool.py`'s `CORE` covers verity, the catalog, the kernels and experimental. The only old files left
  uncovered are the groups noted in item 4: 16 `verity.proofs` modules now in `archive/sp1`, and, for `FLOCK_PURE`,
  `verity_vllm/check/codes.py` and `query/units.py`. C-Flock imports none of them.
- `class_statement.py`'s code digest reads verity, `verity_catalog`, `verity_kernels` and `verity_experimental`. PoUW is a
  module of `verity` now, so it's still covered.
- **Moved vectors:** core's `hm96/vectors_sha512.json` exists at its new path, and only its `generator` field changed.
  `circuit.rs`'s `hm96_leaves_match_core_vectors` reads it there.

Label: `pr:1206@62cf0297857964779cf9c10ca200537d7f299aa4 grant red-team --by proofs`.
