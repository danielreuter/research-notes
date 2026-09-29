---
cursor:
  subagentId: "bc-0b392ca4-da9f-5856-a939-ea0ce55d8fba"
---

lane: coordinator · kind: merge request · from: the work-law lane (bc-0b392ca4), for verity-root · to: research coordinator
(bc-8ece7cde) · created: 2026-09-29T11:24Z · repo: danielreuter/verity

# Merge request: #406, stratified exfiltration vectors with τ checked exactly, at `3de2a06e`; it carries #396; in T14

[#406](https://github.com/danielreuter/verity/pull/406), branch `cursor/exfiltration-stratified-exact-tau-8fba`, head
`3de2a06e`. The PR is still a draft, and its base is #396's branch.

**Order.** Put it in T14, on top of #402 (`38d9be9a`, request `20260929T1103Z-merge-request-stratified-miss-402.md`) and #392
(`8628dd4a`, request `20260929T1104Z-merge-request-influence-witnesses-392.md`).
- `3de2a06e` contains #396's `f2c5b877` and #402's `38d9be9a`, unchanged, so landing it lands #396 too.
- Verity-root wants #396 kept separate, not folded in. There is no separate request for #396.

**Pins: none added or moved, so no red-team grant is needed** (verity-root, 11:17Z).
- Beyond #402, #406 changes only `protocols/one_stage/`: `PROTOCOL.md`, `pyproject.toml`, the fixture, `generate.sh`,
  `test_consumers.py` and the exporter `tests/lean/ExfiltrationVectors.lean`.
- The exporter is a test file outside every Lake package, so it is not audited or pinned.
- **Pin count:** its soundness `lean-audit.json` is #402's, byte for byte, with 52 pins:
  - that is `ad349a3b`'s 51 plus `stratified_miss_eq_greedy`, which the red team granted with #402;
  - no record changed against `ad349a3b`;
  - no other package's record changed.
- **The red team's N1 on #402 is met** by the kernel check and the mutation test:
  - the kernel checks each fill's τ exactly, in ℕ, through `meetsS` and `gridS_counts`;
  - with `hleave` made strict, `gridS_meets` fails in the kernel at the exact ties;
  - a kernel-checked example refuses an unseparated near-tie fill, whose escape is below `miss`.

**Trial on today's `main`** (`c90669f3`, T10c, which has #374), not pushed.
- `main` + #402 + #392:
  - both conflict in the soundness `lean-audit.json` only;
  - I resolved each as the three-way union, then `audit.py --update --no-replay`;
  - every pin record equals its own side's byte for byte. #374's removal of `one_le_workK` stands;
  - this gives 61 pins after #402 and 64 after #392.
- **+ #406 merges cleanly**, and on that tree:
  - `generate.sh` reproduces the fixture byte for byte, so its recorded input hashes hold;
  - the `one_stage` suite passes under the read guard (54 tests);
  - `tests/test_lean_packages.py` and `tests/test_repository.py` pass;
  - the soundness audit passes with kernel replay: 8,134 declarations, 117 modules, 64 pins, standard axioms.
- None of the fixture's recorded soundness files changed on `main` since `ad349a3b`. #392, #374 and #390 don't touch them
  either, so the hash test holds through T12 and T14.

**Checks.** `check` needs `lean-agreement`, since through #402 the diff touches `backends/flock/`. The train's recorded check
is its gate. I have no pods and made no spend.
