---
lane: coordinator
kind: handoff
from: pous-lean
created: 2026-09-28T04:27Z
---

# pous-lean → coordinator: POUS landing queue #162 → #183 → #166 → #196; checks for #166 and #196 re-recorded to the shared store

This extends `20260927T2222Z-handoff-from-pous-lean.md` (#162, #183) with the reference-implementation PRs.

- **Queue, in order:**
  1. [#162](https://github.com/danielreuter/verity/pull/162) at `662a6aea`: the POUS Lean package.
  2. [#183](https://github.com/danielreuter/verity/pull/183) at `8c0076e3`, stacked on #162: the dense proofs.
  3. [#166](https://github.com/danielreuter/verity/pull/166) at `ee781de8`, branch `cursor/pous-reference-9796`: the POUS
     reference `verity_pous`.
  4. [#196](https://github.com/danielreuter/verity/pull/196) at `df2c04e5`, stacked on #166: the public encoder.
- **Recorded `check`, at those exact SHAs, in the shared store:**
  - #166 at `ee781de8`: **passed**, `r20260928-031711-6715`.
  - #196 at `df2c04e5`: **passed**, `r20260928-034942-10aa`.

  Both are done with rc 0 on a clean tree and PRESERVED on R2. Each ran pytest, `circuit-check`, `lean-build` and
  `lean-unit-cut`, and skipped `lean-agreement` by name. Their base predates #130, so their `check` has no `lean-audit`
  step.
  - **A failed attempt at `ee781de8` is also in the store,** `r20260928-024917-d62d`. It failed on
    `tools/research/tests/test_remote_local.py::test_exclusive_refuses_a_live_holder_and_reclaims_a_dead_one`, the
    exclusive-lock race under load that lean-organization reported at 15:01Z. The test passed alone right after, and
    the retry passed. The gate reads passing attempts only.

  These re-record the reference worker's passing runs `r20260928-014852-9bae` and `r20260928-021529-181a`, which exist
  only in that worker's VM store. Mine ran on my VM through `tools/check/check.py --record`, with write-through to R2.
- **The gate will still refuse these SHAs.** All four PRs branch from `main@5a7061c0`, and `main` has moved past it
  (now `6746f408`). `research merge` requires `main`'s tip to be an ancestor, so each needs `main` merged in and a check on
  the new tip, or a train. The re-records are the evidence for the PR heads as reviewed.
- **Conflict: `protocols/pous/PROTOCOL.md`.** #162/#183 and #166/#196 both add it (add/add); nothing else conflicts in a
  trial merge of #183 with #196. The two files also disagree on which scheme is secure-first: #183 says dense, from
  Daniel's choice in the POUS store's `docs/scheme-choice-e2e.md`, and #166 says band `d = 12`, from the later memo
  `docs/band-vs-dense.md`. Resolving it needs that call from Daniel or the POUS coordinator; the Lean statements aren't
  affected.
- **#166 touches `tools/research`.** `tools/research/tests/test_pythonpath.py` adds `protocols/pous` to `REAL_ROOTS` and
  `verity_pous` to the probed names, because `protocols/pous` joins the uv workspace (`pyproject.toml`, `uv.lock`). It's
  a test of shared infrastructure, so please have its owner look.
- **Statement review:** #166 and #196 change no pinned statement and no `lean-audit.json`. Their `.lean` files under
  `protocols/pous/tests/lean/` are check scripts outside any Lake package. For #162 and #183, the reviewer and verdicts are
  in the 22:22Z handoff (red team §17; §30, §31, §34).
