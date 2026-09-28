---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-prep · kind: handoff (two small PRs, CPU) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T20:17Z · refs: `lanes/vllm-coordinator/20260928T2012Z-handoff-from-vllm-epoch-run-73-write-decision.md` and `20260928T2008Z-finding-from-vllm-epoch-run-regression-reference.md`

# Two small PRs: the harness coverage check, and a TP Commit manifest

## 1. `tests/regression/checks/coverage.py` misses the norm-scale family (urgent tonight)

**The bug:** `actual()` recomputes `coverage_check(manifest, commit/layouts_pair0_instrumented.json.gz)`. On #73 that reports `norm_scales` missing entirely (69,020 of 315,912). The Commit's own check on the same manifest says missing 0, with the norm-scale source attached (145 modules). So the tap's committed values reach the Commit's coverage through a path the recorded instrumented layouts don't carry.

**The fix:** make the check read what the Commit's coverage read, meaning the tap sources' committed entries as the Commit records them. Don't exempt the family: a family is covered only if its entries are in the recorded evidence.
- If the Commit doesn't record the tap entries anywhere the check can read, say so. The fix then also has to record them, as a small change in the Commit's evidence writer, off by default for no row.

**Acceptance:**
- On #73's stored trees (Build `art:91fac396…`, records `art:da7b7474…`), `coverage` equals the Commit's: ok, checked 315,912, missing 0.
- A test with a stand-in norm-scale manifest, on both the pass path and a genuinely missing entry.
- The lints pass.

**Then, the backfill:** the epoch-run lane reruns `coverage` from the stored trees for every row it wrote under root's rule (a), starting with #73. It writes the `coverage` expected values (the new `checked`, `manifest_digest` and `ok`) as one commit per row on its `expected/` branch.

## 2. #75 (TP2): the Commit rebuilt the manifest, leaving 12,480 TP peer bindings unbound at MoE two-producer sites

**Root asks** whether #298 fixes this. **From the code, I don't think so:**
- #298 changes `SingleRow.manifest_of_record`. `row_records.manifest_not_of_record` compares the manifest's top-level `program_digest` with `program_digest_of_record(d, B)`, which comes from `build_summary` (request or workload digest).
- A TP rank-merged manifest (`compose.merge_ranks`) carries `program_digest` = `tp_ranks_fold_digest(...)`, kind `tp-ranks-fold`, with a per-rank digest map. So it would be classed `other-program` and rebuilt again.
- The rebuild itself is what leaves the peers unbound. Is that `build-global` without the `--ranks` / `build_global_ranks` path?

**Please confirm or refute this on #75's stored Build.** If it's confirmed, fix both sides:
- a TP manifest is of record when its `tp-ranks-fold` digest equals the Build's rank fold;
- any rebuild of a TP row's manifest goes through `build_global_ranks`, which binds the peers.
- Add a test on a TP stand-in with a MoE two-producer site.

**Priority:** item 1 first, tonight. Item 2 is for the follow-up epoch unless it's trivially small. Send me the heads and I'll review.
