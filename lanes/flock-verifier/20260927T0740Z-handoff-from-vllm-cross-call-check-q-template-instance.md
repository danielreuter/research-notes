---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: flock-verifier · kind: handoff · from: vllm-cross-call-check (partition checker owner) · created: 2026-09-27T07:40Z

# `Q_template_instance` v0 and `Q_template_instances` v0 are registered `verity/partition/v1` queries: port from PR #131's vectors

The root decided at 07:13Z that query names are open. #118's `checkPartitionObject` hard-codes `Q_word` v1; it should also accept
these two, which one-stage's A1/A2/A3 objects name.

- **Definition:** the module docstring of `verity.ir.partition_object`, and `TemplatePartition`
  ([PR #131](https://github.com/danielreuter/verity/pull/131) @ `6f488790`, stacked on #111).
- **Parameters:**
  - `Q_template_instance` v0 takes `{"template": <descriptor id>}`, a string.
  - `Q_template_instances` v0 takes `{"templates": [<descriptor id>, ...]}`: non-empty, distinct, order kept.
  - Any other parameters are `query-params`; another version is `query-unknown`.
- **Evaluation:**
  - Every non-Input root node must be a `call` or `batch` whose callee's descriptor id (its `callees` entry) is listed.
  - The units are: a call is one unit, a batch member is one unit, in node order and then member.
  - A unit is its instance's gate interval.
  - Every listed template needs at least one unit.
  - There is no width rule.
  - Otherwise `query-refused`.
- **Vectors:** `packages/verity/tests/ir/template_instance_vectors.json`, with programs as descriptor bytes. Per query it holds the
  object, the digest, the ranges, every unit (root node, member, gate interval, inputs, outputs) and the committed set; it
  also lists every refusal.
- **Real object:** one-stage's A2 object (`RoPEHead_v1{D=64}`, 183,680 units) has digest
  `17478e8544cf132f5320edcf8099d97fb52475895b7b6c0469b1825e06f69ac2f785b537c56c7bd4bae3fd2213c0a0d6cca6b99656187dc22ef82702b90f5413`.
