---
id: vllm-tp-v2/20260923T2335Z-from-coordinator-p2p4-tp-hook
lane: vllm-tp-v2
kind: handoff
status: open
repo: verity
origin: lane/vllm-p2p4
---
# From the coordinator: p2p4 left a TP hook in the v2 query. It's yours to delete.

`lane/vllm-p2p4` is final at `6c4241a`. The integrator merges it into `lane/vllm-cleanup-2` right after sampler-literals. Base your v2-query work on staging *after* that merge. p2p4 moved the inline query in `query/v1_bridge.py` into a `Population` class, and sampler-literals is being ported into `Population.__init__`.

## The hook (`99bdf0f`)
- `integrations/vllm/verity_vllm/query/v1_bridge.py:353-357` @ `6c4241a`: `request_manifest` raises on a TP rank Program (`result.json` `tp.world > 1`). The comment there reads "TP HOOK: delete this refusal when Q_module_body_v1's policy names the rank-local partials and compose_global merges ranks".
- p2p4's reasoning: the row-parallel Gemm's `part_rank<r>` and lm_head's `shard_rank<r>` are interior to their module body, so `Q_module_body_v1` requires none of them. `compose_global` also has no rank merge / `tp_peer_binding` (TP-04). A v2 "TP manifest" built without both would silently under-populate TP-04's population of record.
- Test: `tests/query/test_module_body.py::test_request_manifest_refuses_a_tp_rank_program`. Replace it with tests that pin the real behaviour.

## What task 1 therefore needs
- A rank-partial policy that names those partials as required.
- A rank merge with `tp_peer_binding` in `compose_global`.
- Acceptance unchanged: #70 v2 manifest digest = `ede1ad81…` (357,796 ids), or every difference is a recorded `pending_review` correction. Same for #75 if its Programs are in R2.
- Delete the refusal and move `row_pod_tp2.sh` / `tp_stage.sh` off `required_manifest build-global`.

## After you land
Once TP is on the v2 query, the only live users of `members_for` / `build_manifest` / the `required_values` traversal are:
- the harness's v1 oracle (`BASELINE_ENGINE=v1`)
- pre-flip records, via `replay_partition` (addresses.rule absent → v1)

Say so in your report; that's what unblocks deleting the v1 query tables.
