---
cursor:
  subagentId: "bc-819f6247-2b10-5a85-9352-4e1d932f2125"
---

lane: one-stage-e2e · kind: handoff · from: vllm-serving-commit · created: 2026-09-27T09:37Z · status: open · repo: danielreuter/verity ·
origin: PR #83 @ 967b8d06 (M0's shared-row writer), PR #116 §3 (the grid rule)

# P6 blocker: M0's `share()` dedupes rows by value, the grid rule doesn't, and #101's layer-0 `qkv` rows do repeat

**The conflict.**
- `verity_flock.circuit.write(..., share_rows=True)` builds each table with `share()`: the distinct rows in first-occurrence
  order, with refs into them.
- The grid rule `verity/one-stage/gemm-grid/v0` fixes the tables independently of the values: `qkv_proj`'s `x` rows are t = 0..286
  (287 rows), and the refs are `(x_base + t, w_base + c)`. The verifier refuses refs that differ.

**It happens on #101.**
- The prompt has 256 tokens but only 156 distinct, so 100 are repeats (from the workload file).
- Layer 0's `qkv_proj` input is RMSNorm of the embedding, with no position before attention. So every repeated prompt token has
  an identical `x` row, and decode tokens that repeat one may add more.
- M0's writer would give `x` fewer than 861 rows, with refs that aren't the grid rule. No served file could pass both M0's writer
  byte-match and the verifier's rule.
- **Deduping by value also leaks.** The table size and the refs would reveal which prompt positions hold the same token, which is
  private. The grid rule depends only on the layout, so it reveals nothing.

**The ask (M0):** a writer mode that takes the tables and refs as given, with no dedupe. For example,
`write(..., share_rows=True, tables={port: (R_p, K)}, refs={port: (n,)})`: the same body layout, the tables in the given order,
salts per table row. Serving commits the grid's tables (duplicate rows included, each with its own fresh salt), and I byte-match
against that mode. The loader and the prover need no change: they already take any refs.

**The ask (one-stage-e2e):** please confirm the grid rule stays value-independent, so duplicates are committed as separate table
rows. P4 is running now (`r20260927-092505-bee3`); P6 goes when this mode lands.
