# vllm-verify-optins: READY

Goal 10 (agent bc-a80fa085; coordinator vllm-coordinator bc-ecac3029): the three opt-ins were verified on real Builds, on the
verification merge `b7a4092a` (`cursor/verify-optins-merge-a795`, not for merging).

| task | row | opt-in | result |
|---|---|---|---|
| 1 | #57 | `weight_only_calls = "once"` | `cross_call` 0 recomputes (57,855 Calls / 133 M gates unset); 105 `+ 1` Calls per Program; unset = record |
| 2 | #73 | `fa3_construction = "check-inf-per-iteration"` | partition checker 0 violations / 0 recomputed (1,164 specializations); unset = record; H100 Match PASS (GM-01 G1..G8, `Attention_v4` fold) |
| 3 | #74 | `SHARED_SCALE` | member check 747,936 -> 0 violations, 146 G -> 0 recomputed gates; host products = `F32Mul_v1` at 2.72 G coordinates; unset = record |
| follow-up | #106 | `fp8.scale_products` through `F32Mul_v1` | [PR #128](https://github.com/danielreuter/verity/pull/128), merge-ready |

- **"Unset = record"** is shown row for row on every request Program and identity for identity on the manifest, with head = base main byte for byte. The record's digests differ only through the Program id's `SRC` (the wrapper's module path moved after 09-22).
- **Handoffs,** in `$STORE/internal/lanes/vllm-coordinator/`:
  - `20260927T1022Z-…-task1-57.md`, `…T1024Z-…-task2-73.md` (with the Match verdict) and `…T1137Z-…-task3-74.md`;
  - `…T0712Z-…-scale-products.md`;
  - `…T1220Z-…-status.md`, which includes the morning summary.
- **Evidence:** `evidence/` holds the scripts, and `evidence/results/{r57,r73,r74,base}/` the checker outputs, row comparisons, value checks and the Match.
- **Pods:** the CPU pod `l32zhicuc7ce1b` ($0.19), the L40S `69t3tqnpjam7kc` ($5.00) and the H100 `2m29px5hjgtci2` ($6.36). All are terminated. Total **$11.55** of $20.
