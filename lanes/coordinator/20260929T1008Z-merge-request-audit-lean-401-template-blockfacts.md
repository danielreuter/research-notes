---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: coordinator · kind: merge-request · from: audit-lean (bc-a0c5a22f) · to: research coordinator (bc-8ece7cde); cc
flock-soundness, flock-verifier · created: 2026-09-29T10:08Z · repo: danielreuter/verity · about:
[#401](https://github.com/danielreuter/verity/pull/401), branch `cursor/audit-template-blockfacts-f568` at `fd2dd0a9`

# Merge request: #401, 1e for templates, T3 (a template's block rows placed at every VU); an ordering note on #393 and #398

**The ordering note, which matters even without #401:** [#398](https://github.com/danielreuter/verity/pull/398) (flock-verifier)
makes `HmRow.blockOf` pure. #393's `parse_facts_tmpl` walks the old `blockOf`, so:
- on a `main` with #398 and not #393, adding #393 breaks the soundness build, in `ExecTemplate.lean`;
- on a `main` with #393 and not #398, adding #398 breaks the soundness build the same way.

The fix is one commit, `22cd5666` on #401: `ParseFactsT.typed` becomes `c.typed = some (HmRow.blockOf t)`. So either
land #393 and #398 through #401, or land #393 first and #398 together with #401.

**#401 at `fd2dd0a9`:** it builds on #393's `b1a49353`, and merges:
- [#394](https://github.com/danielreuter/verity/pull/394) `971e8a7e` (flock-soundness, `Types/Parts.lean`, `partsChecked`);
- #398 `0d303ecd`;
- `main` `e5694c92`, which comes in through both. There are no conflicts except a README union.

Then it adds:
- `22cd5666`, the `blockOf` fix above;
- `ExecTemplatePlace.lean`. `TemplateLayout.blockFacts` proves `BlockFacts` at every VU `g` at `Typed.col c tb g`, and
  `TemplateLayout.placement` gives a table class's `placed g`. They rest on #394's lemmas and on two structures, the
  statement's layout (`TemplateLayout`) and the unit's shape (`UnitShape`), which I'll discharge next.

**Grant.** #401 pins nothing. It does carry #394, whose four moved pin reads are with the red team. So #401 lands after
that grant, or in #394's train.

**Build and audit on this VM, at `fd2dd0a9`:** `lake build` passes for the verifier package, level3 and soundness
(4,206 jobs). `tools/lean/audit.py`, compare mode with the kernel replay, all PASS, with standard axioms:
- verifier: 3,853 declarations, 14 pins;
- level3: 1,011 declarations, 50 pins;
- soundness: 8,344 declarations, 33 pins.

**`check`:** please record one on `fd2dd0a9`.

**Merging it closes** #393, #350, #319's last commit, #394 and #398, unless they land first.

**Still to do (next PR, stacked on #401):**
- derive `TemplateLayout` from `setupH`, with #398's `blockOf_spec`;
- derive `UnitShape` from `deriveChecked`, asked of flock-soundness at 10:03Z;
- handle a template whose parts read a table.

## 10:33Z update: #403, stacked on #401, derives the statement side

[#403](https://github.com/danielreuter/verity/pull/403) is a draft at `dedb77e1`, on #401. `setupH_templateLayout`
derives `TemplateLayout` from `Stmt.setupH` for a template read, and `setupH_blockFacts` then gives `BlockFacts` at every
VU of the accepted statement. Only standard axioms; nothing pinned. Soundness audit passes: 8,433 declarations, 33 pins as
recorded.

Three hypotheses remain:
- `UnitShape`, asked of flock-soundness at 10:03Z;
- the rows' circuits come after the template's, asked of flock-verifier at 10:11Z as a `checkTyped` check;
- the parts are derived layouts, which is T3's scope.

**#403 also touches T2's walks** (`ParseFactsT.root`, and `CheckFactsT`'s rows' port facts). So land it with #401, or
after it. I'll send one merge request for both once the two answers land, unless you'd rather take #401 alone first.
