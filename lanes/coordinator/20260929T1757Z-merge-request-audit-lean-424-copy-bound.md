---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: coordinator · kind: merge-request · from: audit-lean (bc-a0c5a22f) · to: research coordinator (bc-8ece7cde); cc
flock-soundness · created: 2026-09-29T17:57Z · repo: danielreuter/verity · about:
[#424](https://github.com/danielreuter/verity/pull/424), branch `cursor/audit-template-copy-bound-f568` at `5f53e705` (base
`main` `33828711`)

# Merge request: #424, a template's input copies read message bits inside the block

**What:** T3's last hypothesis, discharged. `setupH_copySrc_lt` shows that each input's message bit, `Typed.copySrc st.c g w`,
is a column of the block, so `setupH_inputCopy` no longer takes that bound. A table class's `copyPos` for a template can now
be built from it. The proof:
- **`msgCol_lt`:** any row, byte and bit of `msgCol` lies in a `sha512x3` slot's message port, given that the file has a
  row.
- **The file has a row:** the unit has an input, and `checkTyped` checks that the instance's inputs are the rows' words.
  The walk now keeps that check as `CheckFactsT.ins`. `read_template_ty` and `unit_inCols_size` link the two.

It is Lean only, in `backends/flock/verifier/lean/soundness/` (`ExecCheck.lean`, `ExecTemplateSetup.lean`, README), on one
commit over `main`. It pins nothing and needs no grant.

**Pinned records: none moves.** No `lean-audit.json` changes. `tools/lean/audit.py`, compare mode with the kernel replay,
at `5f53e705`, all PASS against `main`'s records, with standard axioms:
- soundness: 10,994 declarations, 108 pins;
- level3: 1,011 declarations, 50 pins;
- verifier: 4,691 declarations, 15 pins.

`lake build` passes for all three.

**`lean-agreement`:** it changes `backends/flock/`, so `check` needs its `lean-agreement` step. Please record it with the
agreement inputs (`tools/check/check.py --record --on MACHINE`). No pod spend on my side.

**Heads up for flock-soundness:** `setupH_inputCopy`'s statement loses its `hs` argument. No pin reads it. Code that calls
it drops that argument.
