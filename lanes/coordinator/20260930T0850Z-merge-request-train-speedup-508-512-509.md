---
id: 20260930T0850Z-merge-request-train-speedup-508-512-509
campaign: verity
lane: train-speedup
kind: handoff
status: open
repo: danielreuter/verity
origin: train-speedup (bc-8e199f0d)
---

# Merge request, one infra train (root's OK for #509): #508, #512, #509. #495 already landed in TVF

This supersedes my 08:15Z and 08:45Z merge requests. #495 (`43ec23e5`) is on main inside TVF (`cc0f4688`), so the train is:

| Order | PR | Head | What |
|---|---|---|---|
| 1 | [#508](https://github.com/danielreuter/verity/pull/508) | `5e288c15` | The Lean audit runs its packages side by side. Cold: 2,145 s → 1,564 s. |
| 2 | [#512](https://github.com/danielreuter/verity/pull/512) | `7f1123d0` | Per-test keys narrowed to the traced reads, with #498's longest-first scheduling. After an infra-only edit, the vLLM suite reused 4,031 tests and ran 251, in 55 s. |
| 3 | [#509](https://github.com/danielreuter/verity/pull/509) | `577f9e5a` | Tree-identical landing in `research merge`. Root OK'd `a508730a`, and `577f9e5a` adds root's test case. |

**The #509 addition (`577f9e5a`).**
- **Root's test:** A adds `merge_requires={'agree': ['flock/']}`, and C, checked on A, changes `flock/`. After A lands, C merges
  tree-identically. Its attempt that skipped `agree` is refused, and the one where `agree` passed lands with C's tree.
- **The bug that test caught:** `tools_registry._from_file` cached a declaration by file path alone. A process that read `main`'s
  declaration before the train ahead landed kept applying the old rules, and would have admitted the skipped attempt. The cached
  module's name now includes the file's sha256.
- **Tests:** the full `tools/research` suite passes (711 passed, 2 skipped).

**Trial of the train on main `cc0f4688`** (`git merge-tree` in order, then the tests on the merged tree):
- no conflicts;
- `tools/check` 112 pass;
- `tools/lean` 22 pass;
- the `tools/research` merge-gate and sweep tests 14 pass;
- the wall-clock and repository lints 16 pass.

**Cost:** one cold rerun of every suite (suite runner changed) and one cold Lean audit (`tools/lean` changed). With #508 in the tree,
that's about 25–30 min on a nebius slot (`UV_PYTHON=3.14.7`). Trains after it reuse per test. No `backends/flock/` change, so no
lean-agreement.
