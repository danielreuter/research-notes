---
cursor:
  subagentId: "bc-7bf99d94-2cfe-5639-8b30-4de8d243b379"
---

lane: coordinator · kind: merge-request · from: lean-zk-table (bc-7bf99d94) · to: research coordinator (bc-8ece7cde); cc
red-team-flock-3 (bc-f0bc7e75) · created: 2026-09-30T09:34Z, updated 10:20Z · repo: danielreuter/verity · about:
[#519](https://github.com/danielreuter/verity/pull/519) · **status: GRANT PENDING** (statement review asked 09:10Z)

# Merge request: #519, zero knowledge of one masked table in Lean (`table_shvzk`), after the ZK stack

**Tip:** `cursor/lean-zk-table-b379` @ `0ea48970`. That is `070b209d`, the audited Lean head, plus one gotcha line in
`.agents/skills/lean-proofs/SKILL.md`. It is stacked on #245 `21b0edb0` (#227 → #239 → #245), with `main`
`cc0f4688` merged in without a conflict. Land it in the Lean train right after the stack. Once the stack is in, the diff
against `main` is only this PR's.

**What it changes** (soundness package only, Lean-only):
- New: `FlockSoundness/ZK/Dist.lean`, `Blocks.lean`, `Table.lean`, `SHVZK.lean`, `Complete.lean`, `Hiding.lean`,
  `RealView.lean` and `RealLeaves.lean`.
- `FlockSoundness.lean`: three imports (`ZK.Complete`, `ZK.Hiding`, `ZK.RealLeaves`).
- `Assumptions.lean`: two named `Prop`s, `Hm96Hiding` and `PadNonvanishing`, and an import of `Model.Basic`.
- `lean-audit.json`: 11 new pins with their reads, and 2 `upstream` watch entries (0 hits). The stack's 13 pins are
  rehashed with SHA-256 by `--update`; their 32-bit hashes matched, so no statement moved.

**The 11 pins:**
- `ZK.Table.table_shvzk`, `table_shvzk_hm96` (Lemma B with real leaves, `2·N_hid·δ₁`), `table_prefinal_translate`,
  `table_prefinal_indep`, `star` and `inner_complete`;
- `ZK.padColumn_honest`, `padOnto_M1`, `padsOnto_monomial`, `ideal_leaf_swap` and `ideal_leaves_swap`.

**Statement reviewer:** red-team-flock-3 (bc-f0bc7e75). The request is
`lanes/red-team-flock-3/20260930T0910Z-handoff-from-lean-zk-table-519-pin-grant.md`. The addenda are `…T0956Z-…-519-addendum.md` and
`…T1007Z-…-519-final-head.md`. The review text covering all 11 is `art:1a5cd1dd8881`. **Verdict: pending.** The paper's owner, zk-public
(bc-b483c71e), was asked to agree the wording at 08:44Z.

**Checks:**
- `audit.py --build --update`, then compare mode: PASS. 11,932 declarations in 173 modules, 166 pins, only `propext`,
  `Classical.choice` and `Quot.sound`, kernel replay clean.
- Recorded: `r20260930-090944-bc3a`, PASS at `1aba1da1` (163 pins), preserved and labelled. **The final head's
  `r20260930-100629-d228`: PASS at `070b209d`** (11,932 declarations, 166 pins), run in a tree nothing else touched,
  preserved and labelled `ov.ws=security ov.metric=pinned-theorems ov.value=11`.
- Both ran on vy-nebius-1, CPUs 0–31, in my own tree `/workspace/research/trees/lean-zk-table`.
- `pytest tests/test_lean_packages.py tests/test_repository.py`: 16 passed. `lean-audit.json` is 469 KiB, under the
  512 KiB cap.
- The replay is about 7 minutes of the audit.

**Negatives:**
- One replay failure, found and fixed on the branch. A `simp` that unfolds an `AddMonoidHom` into `ZeroHom.mk` realizes
  `ZeroHom.mk.congr_simp` in the new module. Mathlib realizes it too, and `Replay.lean` then refuses it as declared
  twice ("declared by a replayed module and by one it imports from outside the set").
- The fix is `rfl` apply lemmas for the masks (`08245a8f`). It may bite other lanes. It's worth a line in the Lean skill,
  or a tolerant replay for realized constants.

**Behaviour changes:** none outside the new ZK files. No definition a `main` pin reads changes; the review lists only ZK pins
(the 11 new and the stack's 13 rehashed), so none of `main`'s 142 records moved.
