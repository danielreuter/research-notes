---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: handoff (rule, from now on) · from: vllm-coordinator · created: 2026-09-30T16:53Z

**MUFU tables: use `verity.ml.mufu` in all new code.** Don't use `verity_vllm.program.registry.prims`' `_tanh_shards` or the related MUFU table names.
- #250 (consolidation) moves the MUFU tables (ex2, rcp, rsq, sqrt, tanh shards) and `div.full` into core `verity.ml.mufu`, and removes those names from `prims`.
- #569's new uses of `prims._tanh_shards` made #250 fail a second time.
- **In any open branch of yours:** if you read a MUFU table or shard through `prims`, switch it to `verity.ml.mufu` now. If you do it before #250 lands, take the names #250 exports (on `cursor/…` @ `da4261e5`, `packages/verity/src/verity/ml/mufu.py`), or ask the consolidation lane (bc-e373566b).
