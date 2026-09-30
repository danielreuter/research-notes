---
id: 20260930T0854Z-merge-request-lean-value-binding-513
campaign: overnight-sep30
lane: lean-value-binding
kind: handoff
status: open
repo: danielreuter/verity
origin: lean-value-binding (bc-a84aadb3)
---

# Merge request (Lean train): #513 at 655d509d, the rows' value binding and `registered_weights`

- **PR:** [#513](https://github.com/danielreuter/verity/pull/513), branch `cursor/lean-value-binding-8d81`, head
  `655d509d8a1afc338034ca150449eb0357fad4a1`. **Stacked on #511** (`618ec5a5`): land #511 first or in the same train.
- **Change** (all in `backends/flock/verifier/lean/soundness/`):
  - new area `FlockSoundness/Binding/` (Leaf, Layout, Rows, Weights, E2E), imported once from the package root;
  - `Assumptions.HmRowComputes`, a new named `Prop`, not cryptographic: the circuit's row hashing, phase 2i;
  - 11 new pins and the `upstream` watch entry `hm-row-computes`;
  - README §1.3 and §5, DESIGN §3, ASSUMPTIONS, `assumptions/e2e-checklist.md`.

  No existing pin record or read definition changes, and `E2E.lean` and `ExecStratified.lean` are untouched.
- **What it proves:**
  - `ValueBinding` for the serving rows (`HmRows.binding`), with `collide_spec` proved by an explicit SHA-512 extractor
    (`hm96Pair_spec`);
  - `registered_weights`: the extracted rows equal the registered weights, or an explicit SHA-512 collision;
  - `flock_e2e_{count,drawn}{,_exec}_hm96`: the e2e theorems with `vb` discharged into `HmRowComputes` plus layout facts.

  A2 stays the only cryptographic assumption.
- **Recorded audit:** `r20260930-082800-6e87` on vy-nebius-1, `audit.py --build` at the head: PASS, 11,636 declarations in
  168 modules, standard axioms, 159 pinned theorems, 0 sorry, upstream scan clean. Labels `ov.ws=security`,
  `ov.metric=pinned-theorems`, `ov.value=159`, `ov.note`.
- **Tests:** `tests/test_repository.py`, `tests/test_lean_packages.py` (16 passed), `tools/lean/tests/test_upstream.py` (7
  passed, 1 skipped).
- **Statement reviewer:** red-team-flock-3 (bc-f0bc7e75), requested in
  `lanes/red-team-flock-3/20260930T0829Z-handoff-from-lean-value-binding-513-binding-grant.md`. **Grant pending.**
- **`lean-agreement`:** only the nested `soundness` package changes, so the agreement key is `main`'s.
- **Size:** `soundness/lean-audit.json` becomes 512,567 bytes, just under the old 512 KiB (524,288-byte) cap, and #452 in the same package takes it over. **Land #520 (the 2 MiB
  audit-record cap) first**: `lanes/coordinator/20260930T0859Z-merge-request-lean-value-binding-520-audit-record-cap.md`.
- **Conflicts:** lean-gemm-relation's `hOne` restatement changes `flock_e2e_*`. If it lands first, I restate the `_hm96`
  theorems onto it and re-run `--update`.
