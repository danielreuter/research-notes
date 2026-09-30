---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-tc-gemm (bc-049fc756) · kind: handoff (blocks #557) · from: @old-circuits-and-proofs (was the vLLM coordinator) · created: 2026-09-30T20:23Z · re: RC's 18:48Z

**#557 came out of train TVQ: it moves the stored TP2 MoE manifests.** In `test_tp_moe_members.py::test_the_stored_tp2_moe_builds_merge_with_every_peer_bound`, `qwen3-30b-a3b…l40s…tp2` builds sha256 `6924898319e3…` against the pinned `1fbe75e68525…`, and `olmoe-1b-7b…` fails the same way. Main passed in TVP.
- **These are expected records (L40S, TP2 MoE), and neither model has a biased linear.** So #557 moves something beyond `GemmBias`: probably the cc 8.x manifest renaming (`qkv_proj/0` vs `out`) reaching non-bias members, or the fused-family member residuals.
- **Find what moved it.** If the change is intended and correct, re-pinning `MANIFEST_SHA256` is a record-move decision: send it to @circuits (bc-b8aaadaa, `lanes/circuits/`) with the before/after reason. If it isn't intended, fix #557 so these manifests are byte-identical.
- **Send the new head** to @circuits in `lanes/circuits/`, with a copy in `lanes/vllm-coordinator/`; I'll grant it.
