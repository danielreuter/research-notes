---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T05:10Z

# Merge request: PR #108 @ 17e9df25 (the vLLM-shaped serving view, `pipeline/serving_view.py` + `serving-view` CLI): APPROVE

The lane's handoff is `vllm-coordinator/20260927T0459Z-handoff-from-vllm-serving-view.md`. vllm-serving-view is FINAL: about $2.05 of
its $4, pod terminated.

- **Additive:** `pipeline/serving_view.py`, `tests/pipeline/test_serving_view.py`, and one line in `pipeline/cli.py`. It merges cleanly
  into current main 8515c79e and with every queued PR (#98, #99, #102, #103, #105, #106).
- **Nothing of record moves:** no Program, manifest, Definition, query or partition changes, and no allowlist grows. It reads
  `query.word.unit_rule` and changes nothing. The partition checker doesn't apply.
- **What it produces** (dataset `art:10eeb72d…`, mirrored in `internal/datasets/serving-view/`): #101's view on the record Build.
  - 46,654 Calls, each in exactly one leaf; gates equal the address-map span.
  - All 32 chronology step ranges, the 260 group ids, the Q_word units and the committed words agree with the program graph from the
    same Build.
  - The KV-cache edges are exactly `rotary_emb → attn` (K) and `qkv_proj → attn` (V).
  - The TP-rank level is exercised on #70: 4,752 collective edges, 0 mismatches.
- **The record Builds are now stored:** #101 `art:9cb3a4df…` reproduces `ccc21347…` / `90f81868…`. #4 `art:8578b716…` reproduces all
  16 recorded request Programs and manifest `3bbd860f…`. The graphs with `param_inputs`, for the export redraw, are `art:983c79f8…`.
- **Tests:**
  - my jdiff of main 8515c79e against main + #108, over `tests/pipeline`, the lints (P8 and P10 included), `test_no_by_name_rules` and
    `test_imports_resolve`: 5 new tests, all pass; 0 changed, 0 new failures or skips;
  - the lane's pod run: 115 passed, 1 skipped.

## Worth noting (from the lane; not blocking)

- **`--custody-r2` preserves only a run's `evidence/`,** not `builds/` or `program-graphs/`. Lanes must `research data put` Build outputs
  before terminating. This is for the research tooling owner.
- **main's regression record for #101 still pins the r19 Program `079ee0a8…`,** while the headline record is `ccc21347…`. That's for
  the re-baseline.
