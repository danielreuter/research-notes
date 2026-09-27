---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-rf-moetap · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T02:00Z

# PR #96: the evidence meets every condition. It can't merge yet: it conflicts with main after #95 (guarded max) merged.

The records, the #86 comparison, the live check, TP2, the partition report and the wording all meet my 0015Z conditions.
Root: keep the `0x7FFFFFFF` mapping.

**Conflicts with main `fa662029`** (#86, #90, #92 and #95 are all on main): `integrations/vllm/README.md`,
`verity_vllm/config.py`, `pipeline/manifest.py` (11 hunks), `pipeline/row_stages.py` and `query/manifest/verify.py`.
- #95 added `guarded_max: bool` through `manifest.build` / `build_global`, `verify`, `row_stages.required_manifest`
  (`--guarded-max`) and `CommitConfig.guarded_max_tap`.
- #96 generalizes the tap policies into `taps: tuple[str, ...]` / `TAPS` / `R.tap_policy_flags`.

**What to do** (CPU, $0):

1. Merge `origin/main` into your branch (a real two-parent merge) and resolve so that both work.
   - `--guarded-max` stays a query-header statement: the identities and manifest digest are the record's, and its
     behaviour and tests are unchanged.
   - Keep it as its own parameter, or fold it into `R.tap_policy_flags` if that is cleaner. Either way, #95's tests
     (`tests/query/test_guarded_max.py`, the fa_tap_exactness record tests, the manifest-verify policy comparison) must
     pass unchanged.
2. **Default path:** with every flag off, #101's manifest must still be `90f81868…` (a CPU manifest build from the
   fixtures, strict `--word-check`).
3. **Tests on the merged tree:** the lints, plus `tests/query`, `tests/pipeline`, `tests/properties`, `tests/acquire`,
   `tests/commit` and `tests/program/test_moe_router_ordered.py`. Paste the counts. I'll run a jdiff against main on the
   touched directories myself, so you don't need a pod.
4. Hand off the new head. The GPU records stay valid, because the conflicts are in plumbing, not the router, the vocab
   range or the tap sources. If resolving touches any of those, say so.
