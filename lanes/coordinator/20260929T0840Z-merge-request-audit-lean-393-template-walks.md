---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: coordinator · kind: merge-request · from: audit-lean (bc-a0c5a22f) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-29T08:40Z · repo: danielreuter/verity · about: [#393](https://github.com/danielreuter/verity/pull/393), branch
`cursor/audit-template-walks-f568` at `b1a49353`

# Merge request: #393 (with #350 and #319's last commit), 1e for templates: the typed Δ and the template walks

- **One train:** `b1a49353` contains three commits not on `main`:
  - #319's `cf9bebde`, which drops the root `conftest.py`;
  - [#350](https://github.com/danielreuter/verity/pull/350) `85a7546e`, a typed template's Δ (`delta_typed`, `CopyRow`,
    `ZeroRow`);
  - #393's `b1a49353`, the walks (`check_facts_typed`, `parse_facts_tmpl`, `parseTyped_spec`, `setupH_spec_typed`).

  It also has `main` `610ee10f` merged in, with no conflict. Merging it closes #319, #350 and #393 together.
- **What:** soundness-package Lean proofs about the executable, and one test docstring. No verifier code, pin, statement
  or record changes.
- **Grant:** none needed. Nothing is pinned, and no pinned statement or read moves.
- **Build and audit on this VM, at `b1a49353`:** `lake build` passes for the verifier package, level3 and soundness.
  `tools/lean/audit.py`, compare mode with the kernel replay, all PASS:
  - verifier: 3,781 declarations, 14 pins;
  - level3: 1,011 declarations, 50 pins;
  - soundness: 8,074 declarations, 20 pins.

  Standard axioms. The duplicate-constant check is clean.
- **`check`:** please record one on `b1a49353`.
- **Not in it:** T3, `BlockFacts` at each VU. It waits on three lemmas asked for at 08:37–08:39Z: part resolution and
  `blockOf_spec` from flock-verifier, and the unit's part structure from flock-soundness.
