---
lane: coordinator
kind: handoff
from: pous-lean
created: 2026-09-27T20:57Z
---

# pous-lean → coordinator: #183 (the dense secure-first scheme's deployment proofs) is stacked on #162; merge it after #162

- **PR:** [#183](https://github.com/danielreuter/verity/pull/183), draft, branch `cursor/pous-lean-dense-2464`, head
  `f8181a51`, base `cursor/pous-lean-2464` (#162). It is Lean proofs and docs under `protocols/pous/` only; the trusted
  layer is unchanged.
- **What it lands:** `dense_meets_64` and `seg_meets_14` (`Meets` at 64 KB × 512 blocks and at 14 GB, `D = 5`,
  `k = 106`, random-oracle H), and the per-segment tag alignment (`domainSep_equiv`, `tag_injective_14`). It pins all four;
  the records from #162 are unchanged.
- **Checks at `f8181a51`:** `tools/lean/audit.py` from `main` passes, the package's `check.sh` passes all checks
  (including `--fresh`), and 28 tests pass on `main` merged with the branch. A recorded `check` has not been run.
- **Statement review (contract §5):** the reviewer is Red-team POUS Lean statements (`bc-22298e90`). Its §30 in the POUS
  store's `docs/lean-trusted-layer-review.md` covers the two `Meets` theorems: nothing false, GRANTED WITH CONDITIONS.
  **The tag additions (two pins and three definitions) are not yet covered by §30.** Details are in the PR description.
