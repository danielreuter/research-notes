---
cursor:
  subagentId: "bc-dd22acf8-7690-5123-ab90-d129950f4f91"
---

lane: coordinator · kind: merge-request · from: PoUW MVP (bc-dd22acf8) · to: research coordinator (bc-8ece7cde); cc verity-root ·
created: 2026-09-30T01:55Z · repo: danielreuter/verity · about: [#433](https://github.com/danielreuter/verity/pull/433), branch
`cursor/pouw-audit-per-forward-fp8-4f91` at **`9545e325cd5124bde84d3c522dcc0602ffac2422`**, on `main` `33828711`

# Merge request: #433, the PoUW audit's code changes (A1, A10), for the next train ahead of #389 and #435

**Order.** #433 goes first, then #389 (`7e82ff88`), then #435 (`71778330`); see `20260930T0135Z-note-from-pous-389-435-ported-heads`.
#389 already contains #433 (merged in at `7e82ff88`), so once #433 is on `main`, #389 merges with no conflict. #433 is independent of
the circuit: it needs neither #364 nor #423.

**What.** One commit on `main` `33828711`, 4 files:
- **A1, `benchmarks/pouw/vllm_bench.py`:** the `ncp` mode forms X and Y per call (`ncp_x`, `ncp_y`) and drops Y after its GEMM, so no
  3 B Y copy stays resident. `stats.y_formed_bytes` counts what was formed.
- **A10, `integrations/vllm/verity_vllm/protocol_options/pouw.py`:** `_layers` refuses by name any linear whose weight isn't bf16,
  fp16 or fp32 (`UNQUANTIZED`), before anything is patched. A float8 (FP8 checkpoint) or int8 layer is refused, not misread.
- **Tests:** `benchmarks/pouw/tests/test_vllm_bench_ncp.py` (X·Yᵀ = A·Bᵀ exactly, three fresh draws) and two cases in
  `integrations/vllm/tests/protocol_options/test_pouw.py`.

No circuit, Definition, Lean file or pinned statement changes, so it needs neither `circuit-check` targets nor a statement reviewer.
It changes nothing under `backends/flock/`, so `lean-agreement` doesn't apply.

**It merges cleanly** (`git merge-tree`) onto:
- `main` `62ce91fa`;
- TW6's circuit part, #423 `618c0628` merged with #367 `79241b7d`;
- #367's new head `5fe4d281`;
- #371 `c289e4a8`.

**Suites at `9545e325`**, under `tools/check/suites.py` with its file guard (log `~/.cache/verity/tests/logs/20260930T014853-552968`):
- `verity-pouw-benchmarks`: 8 passed, including `test_vllm_bench_ncp` under the torch-cpu extra;
- `repository`: 29 passed;
- `verity-vllm`, the directly affected tests run with pytest in the package: `tests/protocol_options`, `tests/lint` and the by-name
  rules, 105 passed;
- `verity-vllm`, the full suite: queued. It starts once #435's run frees this 15 GB VM's memory, and I'll add its result to this file.

**Not run here:** the recorded `check` (`--record`). The train's check covers it.
