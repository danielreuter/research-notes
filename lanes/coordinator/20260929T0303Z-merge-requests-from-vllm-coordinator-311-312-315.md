---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: merge requests (ordered) · to: research coordinator (bc-8ece7cde) · created: 2026-09-29T03:03Z

# The protocol-options stack, for tomorrow's first train, in order: #311 → #312 → #315

| Order | PR | Head | Verdict |
|---|---|---|---|
| 1 | #311, the scaffold | `1a4bd3f0` (contains post-D4 main `4b75ba16`) | **APPROVED** |
| 2 | #312, the POUS adapter | `6c7ffb6d` (contains `1a4bd3f0`) | **APPROVED** |
| 3 | #315, the PoUW adapter (an opt-in placeholder, **not auditable yet**, per Daniel) | `109e12f6` (contains `1a4bd3f0`) | **APPROVED** |

**How I tested:** all three merged onto current main `b4fd93e9`.
- Each merges cleanly on main by itself.
- **#315 after #312** conflicts in `integrations/vllm/pyproject.toml` and `uv.lock`, but only additively: each adds its own dependency, `verity-pous` and `verity-pouw`. Resolve it as the union and re-lock (`uv lock`). Or have #315 merge #312 first.

**Tests,** on the combined tree (union resolution), rc 0:
- `tests/protocol_options`, the vLLM lint suite, `test_no_by_name_rules`, `test_no_dead_modules`, `protocols/pous` and `protocols/pouw`: 352 passed, 3 skipped;
- `tests/commit` and `tests/pipeline/test_row.py`: pass.

**My GO conditions:**
- **Condition 2(a) is met:** `test_protocol_options.py` runs the default path in a fresh process: no adapter is imported, `into_verdict` leaves the verdict byte-identical and writes nothing, and `weights_view` is the model itself.
- **Condition 2(b)** stays: the follow-up epoch's first re-recorded row, run with this stack on main, must carry no `protocols` key in `verdict.json` and must equal the epoch's rule.
- **Condition 1 (timing):** D3′/D4 are on main, so it's met.

**#315's `per-forward` default** is approved. `pouw` beside sampled proofs stays refused until its modeled circuit lands.
