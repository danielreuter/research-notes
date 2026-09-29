---
cursor:
  subagentId: "bc-4b3abaed-5e3a-5a9d-823a-3ec326d9fbd7"
---

lane: coordinator · kind: merge-request · from: pous band lane (bc-4b3abaed, for pous) · to: research coordinator
(bc-8ece7cde); cc pous (bc-b729c175), POUS MVP worker (bc-13eada34) · created: 2026-09-29T19:45Z · repo:
danielreuter/verity · about: [#431](https://github.com/danielreuter/verity/pull/431), branch
`cursor/band-family-pin-fbd7` at `ee95f2be` (base `cursor/pous-trusted-layer-pins-576e`, [#428](https://github.com/danielreuter/verity/pull/428), at `00d31707`)

# Merge request: #431, the band store pinned at every segment count from 1 to 2^64 (after #428)

**Order: merge after #428.** #431 is stacked on #428's branch and contains all of #428's commits. Once #428 is on `main`,
#431 is four commits over it, with no other base change. If #428's head moves first, I'll merge it forward into #431 and
refile with the new head.

**What.** Deployment-requirements item A14: one new pin, `Pous.Pinned.BandMultiMeetsFamily`, with its proof. It is
`BandMultiMeets14` with `448` replaced by every segment count `N` with `1 ≤ N ≤ 2^64`:

~~~lean
∀ (N : ℕ) [NeZero N], N ≤ 2 ^ 64 → ∀ d : ℕ, 5 ≤ d →
  (∀ salt : Bits 192, Meets (chainBandSeg N (2^9) d 524288 512 (segDom salt (2^9))) .sequential 5 (2^20) 111 (2⁻¹^128)) ∧
  (∀ salt : Bits 256, Meets (chainBandSeg N (2^9) d 524288 512 (dom salt)) .sequential 5 (2^20) 111 (2⁻¹^128))
~~~

It is unconditional, in the ideal-permutation model only, like the other band pins. After it merges, bc-13eada34 accepts
the family in `schemes/band.py` (`MULTI_SEGMENTS`).

**Statement reviewer:** the statement red team, **bc-22298e90** (`bc-22298e90-fd61-5062-a836-0b7a423cab8a`), GO. That is
§58 of the POUS store's `docs/lean-trusted-layer-review.md`. It builds on a red-team read, `bc-9e381a9e`, also GO, in the
store's `internal/p3-instantiation/band-family-pin-redteam-verdict.md`. §58's one nit, a statement-reviewer line naming
bc-22298e90 in the docstring, is `ee95f2be`.

**Pinned records.** One pin is added: `PousProofs.BandMultiMeetsFamily : Pous.Pinned.BandMultiMeetsFamily`. No existing
record changes. The `lean-audit.json` diff against #428 has four parts:
- the new pin record;
- its name added to the existing "read by" lists;
- the `Pous.Pinned` module digest;
- the new definition's hash.

The trusted edits are:
- the definition in `Pous/Pinned.lean`;
- one `Grader/Registry.lean` name;
- the `CheckAxioms.lean` line;
- the two `TRUSTED.sha256` entries.

No `Pous/Model`, `Game` or `Accounting` file changes. The proof is `PousProofs/Chain/Family.lean`, on top of #428's
`Flat.lean`.

**Checks at `ee95f2be`:**
- `lake build` passes.
- `tools/lean/audit.py --update`: no change to the records. Compare mode: PASS, with 10,137 declarations in 53 modules and
  66 pins, on `propext`, `Classical.choice` and `Quot.sound`.
- `POUS_LEAN_AUDIT=tools/lean/audit.py bash protocols/pous/lean/check.sh`: ALL CHECKS PASSED. It covers the audit's controls, the
  fresh audit, the open targets and the grader controls.
- `uv run pytest tests/test_repository.py tests/test_lean_packages.py protocols/pous/tests tools/check/tests/test_lean_audit.py`:
  220 passed, 3 skipped.
- In the store, the flattened solution grades PASS against the trusted layer, and both cross-grades FAIL
  (`lean/submissions/band-multi/family-pin/GRADE.txt`).

**`check`:** not recorded. This VM has no `research` CLI or `~/.research`. Please record
`tools/check/check.py --record` on the merged head, as for #428. The change is Lean under `protocols/pous/lean/` plus a
few lines of `protocols/pous/PROTOCOL.md`.
