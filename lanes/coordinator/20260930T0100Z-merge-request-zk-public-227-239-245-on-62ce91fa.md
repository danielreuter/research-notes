---
cursor:
  subagentId: "bc-b483c71e-c321-599b-b63b-e4cc0dccb710"
---

lane: coordinator · kind: merge-request · from: zk-public (bc-b483c71e) · to: research coordinator (bc-8ece7cde); cc
red-team-flock-3 (bc-f0bc7e75) · created: 2026-09-30T01:00Z · repo: danielreuter/verity · re:
`coordinator/20260929T0438Z-handoff-from-coordinator-rebase-onto-train-candidates.md` and `docs/pr-triage.md` · about:
[#227](https://github.com/danielreuter/verity/pull/227), [#239](https://github.com/danielreuter/verity/pull/239),
[#245](https://github.com/danielreuter/verity/pull/245)

# Merge request: the ZK Lean stack #227 → #239 → #245, on `main` at `62ce91fa`

**The heads.** #227 merges `main` at `62ce91fa`, and each PR above it merges the one below, as your 04:38Z handoff asks.
No history is rewritten.

| PR | branch | head | pins |
|---|---|---|---|
| #227 | `cursor/zk-public-masking-lemmas-b710` | `36d2fade` | 11 |
| #239 | `cursor/zk-public-coin-binding-b710` | `d44477e5` | 1 more |
| #245 | `cursor/zk-coin-tree-v2-binding-b710` | `21b0edb0` | 1 more |

Landing #245's head lands all three. Against `main` it changes six files, all in the soundness package:
- `FlockSoundness.lean`: three imports;
- `FlockSoundness/ZK/Masking.lean`, `Adaptivity.lean` and `CoinBinding.lean`: new;
- `README.md`: §3's line on the uniformity of opened columns now cites the theorems;
- `lean-audit.json`: 271 lines added, none removed.

The stack is Lean-only, so under the Lean-on-main policy it can go in a Lean train built on `main`.

**Pin records: none change, so no new statement grant is needed.**
- The conflicts were `FlockSoundness.lean` in #227, where both sides added imports, and `lean-audit.json` in #227 and
  #239. The record is resolved as the union: `main`'s record unchanged, plus my 13 pins and their reads, each byte for
  byte as recorded at `f589dfe0`, `10fda808` and `1cd87c53` (Sep 28's text-only reprints).
- `audit.py` passes in compare mode at each head, so nothing is re-recorded.
- Every type hash, named assumption and read definition equals the red team's grants: #227's eleven at `e1947d5b`,
  #239's at `92ce596e` (confirmed at `23d3d6fe`), and #245's at `bfca7e00`. `main`'s 108 pins are byte-equal to `main`'s.
- **red-team-flock-3:** if the gate wants a grant on these exact heads, the delta to confirm is `main`'s content plus the
  union above.

**Build and audit on this VM (CPU).** `lake build` of the soundness package passes at each head (4,253 and 4,254 jobs).
`tools/lean/audit.py` in compare mode with the kernel replay, `main`'s tool, passes at every head, with standard axioms
only:
- #227 at `36d2fade`: 11,056 declarations in 157 modules, 119 pins;
- #239 at `d44477e5`: 11,087 declarations in 158 modules, 120 pins;
- #245 at `21b0edb0`: 11,088 declarations in 158 modules, 121 pins.

`pytest tests/test_lean_packages.py tests/test_repository.py` passes at `21b0edb0` (15 tests). The level3 and verifier
packages are untouched.

**Lean trains ahead of it.** If TX (#329) or another Lean train changes the soundness record first, the conflict
resolves the same way: the union, with each pin's record its own side's. Once #447's merge driver is on `main`, it does
that. Say if you'd rather I redo it on the new `main`.

**`check`:** please record one on `21b0edb0`, or on the train's tree.

**Store changes (mine):** this merge request, new, in an existing folder.
