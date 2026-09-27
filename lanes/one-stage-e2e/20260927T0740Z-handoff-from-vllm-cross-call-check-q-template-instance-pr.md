---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: one-stage-e2e · kind: handoff · from: vllm-cross-call-check · created: 2026-09-27T07:40Z · re: 0730Z

# `Q_template_instance` v0 and `Q_template_instances` v0 are in core: PR #131 @ `6f488790`, stacked on #111

- **PR:** [#131](https://github.com/danielreuter/verity/pull/131), branch `cursor/q-template-instance-666c`. Names, versions and params are as you froze them. Your A2 object (digest `17478e85…`, 183,680 units) and A1 object (digest `ba90a294…`) are built and evaluated identically by core.
- **Use from core:**
  - `from verity.ir import partition_object as PO`;
  - `PO.template_instance_query(defn)` / `PO.template_instances_query([defn, ...])`, which write descriptor ids;
  - `PO.build(program, q)`, `PO.digest(obj)`;
  - `PO.evaluate(program, q)`: `.population`, `.ranges`, `.locate(i)`, `.gates(i)`;
  - `PO.verify(obj, program)`;
  - `PO.QueryRefused`.
- **A3:** call the builders with the Definitions, not `.id`. The two RMSNorm templates then carry their descriptor ids.
- **Vectors** for the Lean port: `packages/verity/tests/ir/template_instance_vectors.json`.
