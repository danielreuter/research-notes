---
id: proofs/20261005T1614Z-finding-flock-security-defs
campaign: flock
lane: proofs
kind: finding
status: in-progress
repo: danielreuter/verity
origin: bc-e3b551b5-6835-5a58-ba91-31ab8894f651 (flock-security-defs, for the proofs coordinator bc-8416bc72)
---

# C-Flock's soundness package, split so that trusted text builds on Mathlib alone

**Question.** Can every trusted-text module of C-Flock's soundness package (`flock_verify_sound`'s statement and every
definition it reads, the named assumptions, ZK/GK's extractor and simulator) build on Mathlib alone, with ArkLib and VCVio
only in proof modules and C-Flock's `Game` replaced by core's `Verity.Game`, without weakening any guarantee's statement?
This is step 1 of Daniel's layout ruling (8:53 AM PDT): the split is made in place, under today's module paths.

**Branch** `cursor/flock-security-defs-95d4`, from `cursor/flock-lock-reduction-95d4` (#1170) at 1d8b99cdf, with
`origin/cursor/verifier-fail-closed-95d4` fe0b6f9d9 merged at d1f81c431 (on the `lean-audit.json` conflict, #1170's side
was kept; the result has 41 guarantees, all with owner `@proofs`).

## Before (read from `.lean` imports at d1f81c431)

| | modules | reach ArkLib, VCVio or CompPoly |
|---|---|---|
| soundness package | 584 | 434 |
| trusted: a module in `reads`, `Assumptions`, or under `ZK/GK` | 238 | 129 |

- Five modules import ArkLib or VCVio directly: `Defs`, `Discharge.ZkSession.Inner`, `JohnsonMCA`, `LigeritoMCA` and
  `ListSize`. Every other module reaches them through those five.
- The inventory (`flock-spec`) reports that the read definitions name only 2 ArkLib constants (`ReedSolomon.code` and
  `Code.relativeUniqueDecodingRadius`) and 1 VCVio constant. The import graph is far wider than that, because modules
  that hold read definitions also hold proofs, and they import proof modules.

## Plan and progress

- [ ] A declaration-level dependency dump on node 1 (`Deps.lean`, scratch). For each declaration it gives its constants,
      which shows which import each trusted module needs for its definitions and which only for its theorems. It is
      running as r20261005-162232-7f67.
- The scale is larger than the five direct importers suggest. The 129 tainted trusted modules hold 1468 theorems and
  1360 definitions, and only 13 of them hold no theorem. So the work is a split of each such module: its definitions,
  plus the theorems that need nothing tainted, stay at today's path, and the other theorems move into a proof module
  beside it. The records' `reads` then keep their modules.
- [ ] Step 1: the ArkLib cuts (`Defs`, `ZkSession.Inner`), plus plain Mathlib references for the RS code and the
      unique-decoding radius, with their equivalence to ArkLib's proved in a proof module.
- [ ] Step 2: the ZK/GK closure.
- [x] Step 3: `Game` onto `Verity.Game` (ed4e2a8f8, not built yet). Core's definitions are C-Flock's, word for word.
      `export` keeps every old name (`FlockSoundness.Game.bind` and the rest). Dot notation on core's type doesn't see
      C-Flock's own lemmas, but a source scan finds no such use. The audit takes the move as
      `--moved {"FlockSoundness.Game": "Verity.Game"}`. The package now requires `verity/lean` by path. That changes
      `lake-manifest.json`, so two fixtures, `exfiltration_lean.json` and `randomness_lean.json`, record a stale sha256
      until they are regenerated on node 1.
- [ ] Step 4: the repository test.
- [ ] Step 5: the full audit on node 1.
- [ ] Step 6: the before and after table.
