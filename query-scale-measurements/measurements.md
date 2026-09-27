---
cursor:
  subagentId: "bc-ba86b98f-8e28-5ab5-bbf1-6b43a33e9fe9"
---

# Query-scale measurements (evidence for `docs/query-scale-benchmark-proposal.md`)

Taken Thu Sep 24, about 8:45 PM PT, on a 4-core cloud VM against `main` `bbbe936c` (`packages/verity/src` and vLLM's `query/partition.py`). These are single runs, good to about ±20%. Rerun with `VERITY_REPO=<checkout> python3 <script>`.

| Script | What it measures | Output |
|---|---|---|
| `exp_nested.py` | A synthetic Earth-scale Program from nested `batch`/`scan` nodes (1.9×10^29 gates): build, gate lookup, structural family `count`/`by_index`/`index_of`, partition and width validation, descriptor and digest; `default(32)` fails with `MemoryError` | `nested.json` |
| `exp_flat.py flat` / `het` / `banks` | The same workload as one root node per instance, with heterogeneous shapes, and as banks by shape (up to 10^15 requests) | `flat.jsonl`, `heterogeneous.jsonl`, `banks.jsonl` |
| `exp_misc.py` | Column-major batch gate lookup, `by_index` on whole-node sets, float64 geometric-gap bias at 10^25 labels, exact draw cost, Merkle opening verification at depths 20–100 | `misc.json` |
