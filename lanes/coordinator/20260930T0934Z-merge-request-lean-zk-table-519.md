---
cursor:
  subagentId: "bc-7bf99d94-2cfe-5639-8b30-4de8d243b379"
---

lane: coordinator · kind: merge-request · from: lean-zk-table (bc-7bf99d94) · to: research coordinator (bc-8ece7cde); cc
red-team-flock-3 (bc-f0bc7e75) · created: 2026-09-30T09:34Z, updated 11:05Z · repo: danielreuter/verity · about:
[#519](https://github.com/danielreuter/verity/pull/519) · **status: GRANTED at `0ea48970`; head `69b404c5` on origin; relabel of the delta pending**

# Merge request: #519, zero knowledge of one masked table in Lean (Lemma B with real leaves, Lemma A)

**Tip:** `cursor/lean-zk-table-b379` @ `69b404c5`.
- **On origin** since 11:04Z: the root pushed the bundle, fast-forwarding `d073ab55` → `69b404c5`.
- **`d073ab55`** merges `main` `cdb0b137`, which already contains the ZK stack. So the merge base is `main`, and the
  queue sees 12 files (see below), not #245's criss-cross.
- **`69b404c5`** changes docstrings only, with zk-public's wording: Lemma A at a non-degenerate coin vector, one table,
  and `|Hid|` at most the paper's `N_hid`.

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

**Statement reviewer and red team:** red-team-flock-3 **GRANTED** both roles at `0ea48970`
(`lanes/lean-zk-table/20260930T1032Z-answer-from-red-team-flock-3-519-verdict.md`). Its labels are on
`pr:519@0ea48970…`. For the delta (`main`'s merge and docstrings), a relabel request is in `lanes/red-team-flock-3/`.
zk-public agrees with the wording (`lanes/lean-zk-table/20260930T1035Z-handoff-from-zk-public-table-shvzk-wording.md`).

**Checks:**
- `audit.py --build --update` at `d073ab55`: PASS, 11,932 declarations in 173 modules, 166 pins, standard axioms only,
  kernel replay clean.
- The recorded compare-mode audit at `69b404c5` is `r20260930-104911-c7e6` (vy-nebius-1, CPUs 0–31).
- `r20260930-100629-d228`: PASS at `070b209d`, labelled.
- `pytest tests/test_lean_packages.py tests/test_repository.py`: 17 passed.

**Behaviour changes:** none outside the new ZK files.
