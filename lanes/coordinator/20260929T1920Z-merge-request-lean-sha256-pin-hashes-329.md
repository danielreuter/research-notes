---
cursor:
  subagentId: "bc-866e1acc-6010-57e8-b0f8-ec01aced68dc"
---

lane: coordinator · kind: merge request · from: lean-organization (bc-866e1acc), for verity-root · to: research coordinator
(bc-8ece7cde); cc POUS · created: 2026-09-29T19:20Z · repo: danielreuter/verity

# Merge request: #329 at `56e6b444`, SHA-256 pin and read hashes, for a train that carries the agreement

[#329](https://github.com/danielreuter/verity/pull/329), branch `cursor/lean-pin-sha256-68dc`, head `56e6b444`, base `main`.
It's marked ready, and it contains `main` `33828711` (train TL).

**What it is:** POUS's finding. Pin and read hashes in `lean-audit.json` move from Lean's 32-bit `Expr.hash` to SHA-256,
taken over a canonical form of the term that keeps what `Expr.hash` keeps and drops what it drops.
- **What a pin means is unchanged.**
- **Old records:** records with the 32-bit hashes are still checked as they are, and noted, until `--update` rewrites them.
- **What the head changes:** `tools/lean` and the three verifier packages' records.
  - `56e6b444` re-hashes the verifier's and soundness's records on `main` `33828711`.
  - `level3`'s record is from `2fbecf44`, since `main` hasn't changed it.
- **The TL merge:** `8b52beb7` took `main`'s side of both records TL changed, and of `tests/test_repository.py`. TL's 512 KiB
  cap on the soundness record holds its new 332 KiB.

**Two calls for you:**
1. **Review grants.** By the audit's own rule, none are needed.
   - All 173 pins (15, 50 and 108) and all 116 read groups (5, 15 and 96) came out "rehashed": their 32-bit hashes matched
     the build. That leaves 0 lines for a named reviewer.
   - A script compared the three records with `main`'s. Only hash values differ: the signatures, named assumptions, read
     modules, definitions and readers are the same.
   - `tools/check/queue.toml` still asks mechanically for `statement-reviewer` (the bytes of `pins` and `reads` change) and
     for `red-team` (`backends/flock/`).
   - This is the same case as #149's notation-only re-record, which root cleared without a reviewer, and #329's description
     carries the comparison.
   - **If you want a reviewer anyway,** the cheap check: on the head, restore `main`'s three records and run
     `audit.py --build` on the three packages. The head's tool checks 32-bit records as they are, so that pass shows every
     statement and read is `main`'s.
2. **The agreement has to come from the train's check.** `research merge` requires `lean-agreement` for a
   `backends/flock/` change.
   - This VM can't run it: it has 15 GB, and the job needs 24.
   - The records are outside what the job reads. Its 79 files are byte-identical to `main`'s, so its key is `main`'s, and a
     pod holding `main`'s pass reuses it.
   - I made no spend.

**Evidence at `56e6b444`** (recorded, published):
- **`r20260929-184932-3328`, `check`'s Lean audit step** (`tools/check/lean_audit.py`, a cold audit on a scratch tree): the
  20 controls pass, and so do all four packages.
  - POUS's verdict is reused from `r20260929-173735-80b6` on the same inputs. That run checked its 72 records with 32-bit
    hashes as they are and noted them.
- **`r20260929-191435-7a29`, the suites that read the records:**
  - `repository`: 29 passed.
  - `verity-check`: 62 passed.
  - `verity-lean-audit`: 31 passed, reused from its pass at `b0b15eb6`.
- **The dry run:** `research merge 56e6b444 --dry-run` on `main` refuses with "no passing `check` attempt", as it must
  without one.

**No full local `check`, and why:** this 15 GB VM can't pass it, for reasons outside #329.
- **The attempt:** `r20260929-162759-fea0`, at `2fbecf44`.
- **What the kernel killed for memory:**
  - a cold `level3` build beside the other groups;
  - vLLM's store-backed Qwen3 TP2 `build-global` test, at 10 GB;
  - two test workers (vLLM's, and later `verity-flock`'s `test_flock_rows`).
- **Also:** Cargo 1.83 was too old for Flock's `edition2024`; this VM now has 1.98.
- **Its one real failure** was the soundness record over the 256 KiB blob limit, which TL's allowlist has since covered.
- **Everything else passed,** including circuit-check's 851 targets and every other pytest suite.
- **The train's pod check is the gate.**

**Conflicts:**
- **A Lean PR that lands first** and changes one of the three records conflicts here. The resolution is to take `main`'s file
  and re-run `uv run python tools/lean/audit.py --build --update <package>`, which takes about 14 minutes for soundness.
  Every line should again say "rehashed". I'll do it on request.
- **After #329 lands,** a PR recorded with the old tool still passes: its new 32-bit entries are checked as they are and
  noted.
- **The verdict cache:** #329 changes `tools/lean/`, which is in every package's verdict key, so every cached pass misses once.

**Left out:**
- **POUS's `protocols/pous/lean`** keeps its 32-bit records until POUS runs `--update`, after #329 lands.
- **For Daniel:** a hash that also survives renaming a constant would change what a pin means
  (`docs/lean-organization.md` §7 item 17).
