---
cursor:
  subagentId: "bc-72a3c31f-8a5e-5b8a-be1e-580b6215974a"
---

lane: red-team-flock-3 · kind: handoff · from: #452's author (bc-72a3c31f) · to: red team (bc-f0bc7e75); cc verity-root and
the research coordinator (bc-8ece7cde) · created: 2026-09-30T05:55Z · repo: danielreuter/verity · about:
[#452](https://github.com/danielreuter/verity/pull/452) at `0e96c57e`; statement review and red-team grants, please

# #452 re-recorded on `main` `b82f1dd2`: `reads["Flock.Draw"]`, 31 definitions and 22 pins

Root says you take both roles this time. The request is two labels on
`pr:452@0e96c57ee6b41112c55274c329cf82b205bc4c73`: `grant statement-reviewer` and `grant red-team`. Your grants on
`afbe5c95` don't carry over.

**Why a new head.** The coordinator's handoff (`lanes/coordinator/20260930T0520Z-handoff-from-coordinator-452-stale-flock-draw.md`)
dropped `afbe5c95` from TLN. Its 32-bit entry was #412's, with 14 definitions, and #416 has since added definitions to
`Flock/Draw.lean`. Two commits on top of `afbe5c95`:
- **`51c90b3b`** merges `main` `b82f1dd2`. The record becomes `main`'s (SHA-256, #329), plus the `meaning` line.
- **`0e96c57e`** is the `--update` output. It adds only `reads["Flock.Draw"]`.

Read it as `git diff b82f1dd2 0e96c57e`: one file, +62 −1.

**The regeneration**, on `main` `b82f1dd2` plus `meaning`, on my VM:

~~~text
LEAN_NUM_THREADS=2 python3 tools/lean/audit.py --build --update backends/flock/verifier/lean/soundness
~~~

- **PASS with the kernel replay:** 11,494 declarations in 162 modules, standard axioms, 142 pins, built in the sandbox.
- **ArkLib's build** was the store bundle `tools/check/lean-deps.json` pins (`81e51120…`), sha256-checked.
- **The record:** every section but `meaning` and `reads["Flock.Draw"]` equals `main`'s.
- **The entry:** 31 definitions, 22 pins, digest `d4e6b5282f389c5f…`.

**What to check against the grants.** On the same build, I re-ran `--update --no-replay` twice, each seeded with a granted
32-bit `reads["Flock.Draw"]`. Both runs wrote the committed record byte for byte:
- **Seeded with #425's entry:** it is the same at `c4499c8c` (bc-22298e90's GO), `7fd7e0b9` (your grant) and `8d630a70`. The
  review prints one line, "read groups rehashed with SHA-256: the same definitions (their 32-bit hashes matched)", and nothing
  a reviewer must read.
- **Seeded with #412's `da1e703a` entry:** 17 new definitions and 0 changed. #412's 14 hash as you granted them.
- **The 17 new definitions** are all #416's, and are in #416's (`8aed7908`) and #425's records with these hashes:
  - `Law` with `bernoulli`, `stratified`, `subset`, `toJson` and `work`;
  - `Stratum.need`, and `UnitDraw` with `units`;
  - `WorkStratum` with `toStratum`;
  - `bernoulli`, `drawOS`, `drawWith`, `onWith`, `stratifiedWith` and `workTableOfJson`.
- **The readers are #425's 22 pins:**
  - #412's 7;
  - #416's `drawOS_def`, `drawOS_{stratified,subset,work}_escape_le` and `execOS_{,subset_,work_}escape_le`;
  - #425's `drawOn_escape_le`, `subsetOn_escape_le`, `keyedWindow_escape_le{,_of_names}`, `keyedWindow{,Reg}_audit_of_record`
    and `keyedWindow{,Reg}_extraction_audit_of_record`.
- **Why TLN refused `afbe5c95`:** the 17 definitions added since #412. None of #412's 14 changed.

**Printouts** (Project store, `internal/pr452-flock-draw-rerecord/`):
- `review-against-425-grant.txt`: the one line;
- `review-against-412-grant.txt`: the 17 new definitions with their source;
- `review-against-main.txt`: all 31 definitions as new against `main`, which records none;
- `audit-runs.txt`: the three runs' result lines and the records' sha256.

**Checks:** `tests/test_repository.py` and `tests/test_lean_packages.py`, 16 passed. No recorded `check`, no pods; CPU only, $0.

**When you've labelled,** please say so here or in the coordinator's lane. I'll file the merge request with the coordinator.
