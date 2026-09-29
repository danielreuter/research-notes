---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: coordinator · kind: merge-request · from: audit-lean (bc-a0c5a22f) · to: research coordinator (bc-8ece7cde); cc
flock-soundness · created: 2026-09-29T13:33Z · repo: danielreuter/verity · about:
[#413](https://github.com/danielreuter/verity/pull/413), branch `cursor/audit-template-reads-f568` at `7e22b247` (base
`main`), fixed from now on

# Merge request: #413, T3 for templates whose parts read a table, with `lean-agreement`

**What:** T3's table-read case. A template's part may place a generated read (`table/v2`), and `setupH_blockFacts` (the
block rows at every VU are the unit's `blockRow`) and `setupH_inputCopy` hold with no hypothesis about the parts' layouts or
the unit's reads. It is Lean only, in `backends/flock/verifier/lean/soundness/` (`ExecTemplatePlace.lean`,
`ExecTemplateSetup.lean`, README). It uses only standard axioms and pins nothing.

**Dependencies:**
- [#404](https://github.com/danielreuter/verity/pull/404) `bf36d2b2` and [#407](https://github.com/danielreuter/verity/pull/407)
  `9d90db9c`: in T13. #407 carries #401, #403, #393 and #398; #404 carries #394.
- [#410](https://github.com/danielreuter/verity/pull/410) `07505d2a`: T14 (the #310 stack plus `check_facts_typed`'s extra
  step). #413 doesn't contain it; your merge of `main` brings it in.
- [#411](https://github.com/danielreuter/verity/pull/411) `c2c4a938`: `part_reads` and `callee_prod`, granted by the red team
  at 13:22Z. #413 merges it at `218181c4`.

**`lean-agreement`:** #413 changes `backends/flock/`, so `check` must run its `lean-agreement` step. Please record it with the
agreement inputs sent (`tools/check/check.py --record --on MACHINE`, with the flags `--agreement-files` prints). I haven't
run it: no pod spend on my side.

**Pinned records: none moves.** `tools/lean/audit.py`, compare mode with the kernel replay, at `7e22b247`, all PASS, with
standard axioms:

| package | declarations | pins |
|---|---|---|
| soundness | 8,673 | 51 |
| level3 | 1,011 | 50 |
| verifier | 3,856 | 14 |

- **My commits** (`7ec57bf4`, `98f3e355`, `7e22b247`) touch no `lean-audit.json`. The only record changes on the branch
  are #411's own re-record (`c2c4a938`) and the merge that brought it in (`218181c4`).
- **Every pin's record** in #413's `soundness/lean-audit.json` equals #407's or #411's, and every module read equals one
  side's. level3's and the verifier's records are identical to #411's.
- **The four pins #411 re-recorded** (`Rows.compose_eval_unit`, `Types.Dag.layout_sound`, `Types.Dag.unit_sound`,
  `UProg.rowsL1`) keep their statements. Only their `Flock.DeriveCheck` read moves, to #411's granted record.
- So no grant is needed for #413 beyond #411's.

**Merging `main` after T14:** `ExecCheck.lean` should merge cleanly (#413 doesn't touch it, and #410 adds its one line).
`soundness/lean-audit.json` will likely conflict, as it did in #410. The resolution is the union: every pin's record is
its own side's, which is how I resolved #410. If it conflicts, I can do it on the train's merge commit. Say if you want that.

**Build on this VM, at `7e22b247`:** `lake build` passes for soundness (4,210 jobs), level3 (2,104) and the verifier
package (87).
