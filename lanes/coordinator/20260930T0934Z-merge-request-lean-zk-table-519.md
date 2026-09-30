---
cursor:
  subagentId: "bc-7bf99d94-2cfe-5639-8b30-4de8d243b379"
---

lane: coordinator · kind: merge-request · from: lean-zk-table (bc-7bf99d94) · to: research coordinator (bc-8ece7cde); cc
red-team-flock-3 (bc-f0bc7e75) · created: 2026-09-30T09:34Z, updated 12:55Z · repo: danielreuter/verity · about:
[#519](https://github.com/danielreuter/verity/pull/519) · **status: stacked on TLP at `48b8452d`; re-grant asked 12:39Z (granted at `69b404c5`)**

# Merge request: #519, zero knowledge of one masked table in Lean (Lemma B with real leaves, Lemma A)

**Tip:** `cursor/lean-zk-table-b379` @ `48b8452d`, stacked on TLP.
- **`8fa92dd1`** merges #526 `04b94af7`, which contains #513 `59671040`, #514 and #521. It resolves your 12:14Z conflict
  in `Assumptions.lean` by keeping both sides' definitions (`HmRowComputes`, and `Hm96Hiding`, `PadNonvanishing`), with
  one joined intro. `lean-audit.json` merged through `merge.py`.
- **`48b8452d`** merges `main` `1c10b00c`, with no conflict.
- **On origin** since 12:54Z: the root pushed the bundle, fast-forwarding `69b404c5` → `48b8452d`.
- **Once TLP lands,** the diff against `main` is #519's own 12 files again.

**What it changes against `main`** (12 files, Lean-only plus one skill line):
- `soundness/FlockSoundness/ZK/Dist.lean`, `Blocks.lean`, `Table.lean`, `SHVZK.lean`, `Complete.lean`, `Hiding.lean`,
  `RealView.lean` and `RealLeaves.lean`: new;
- `soundness/FlockSoundness.lean`: three imports;
- `soundness/FlockSoundness/Assumptions.lean`: `Hm96Hiding`, `PadNonvanishing` and an import of `Model.Basic`;
- `soundness/lean-audit.json`: 11 new pins with their reads, and 2 `upstream` watch entries (0 hits);
- `.agents/skills/lean-proofs/SKILL.md`: one gotcha (the replay's `congr_simp` refusal).

**The record.**
- `lean-audit.json` was merged with `tools/lean/merge.py`: `main`'s 155 pins plus the 11, each from its own side.
- `audit.py --build --update` on the merged tree rewrote nothing, so no pin of `main`'s moved.
- The review text for the 11 is `art:1a5cd1dd8881`.

**Statement reviewer and red team:** re-grant at `48b8452d` asked
(`lanes/red-team-flock-3/20260930T1239Z-handoff-from-lean-zk-table-519-regrant-on-tlp.md`). Earlier, red-team-flock-3
**RE-GRANTED** both roles at `69b404c5`
(`lanes/lean-zk-table/20260930T1146Z-answer-from-red-team-flock-3-519-regrant.md`).
- **Labels:** `grant = statement-reviewer` and `grant = red-team` on `pr:519@69b404c5a6e6edd8a9210443d04fe840e73f3eb9`,
  by `red-team-flock-3`, with ref `note:lean-zk-table/20260930T1146Z-answer-from-red-team-flock-3-519-regrant`, on the
  remote.
- **The earlier grant** was at `0ea48970` (`…T1032Z-answer-…-519-verdict.md`).
- **Roles:** the queue now asks for exactly these two roles; `vllm-coordinator` is gone.
- **Wording:** zk-public agrees (`lanes/lean-zk-table/20260930T1035Z-handoff-from-zk-public-table-shvzk-wording.md`).

**Checks:**
- `audit.py --build --update` at `48b8452d` rewrote nothing: PASS, 12,118 declarations in 180 modules, 187 pins,
  standard axioms only, kernel replay clean.
- **Recorded:** `r20260930-123826-8340`, PASS at `48b8452d` (vy-nebius-1, CPUs 0–31), preserved and labelled.
- `r20260930-104911-c7e6`: PASS at `69b404c5`, labelled.
- `pytest tests/test_lean_packages.py tests/test_repository.py`: 18 passed.

**Behaviour changes:** none outside the new ZK files.
