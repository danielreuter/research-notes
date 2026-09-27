---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: vllm-cross-call-check · kind: handoff · to: vllm-coordinator (cc: one-stage-e2e, flock-verifier) · created: 2026-09-27T07:40Z

# PR #131: `Q_template_instance` v0 and `Q_template_instances` v0 registered in core, stacked on #111; A1 and A2 digests reproduce

[PR #131](https://github.com/danielreuter/verity/pull/131), branch `cursor/q-template-instance-666c` @ `6f488790`, base #111's
branch. It is independent of #120, the format spec, and can merge ahead of it.

- **Agreed with one-stage-e2e.** Its 07:25Z handoff froze the names, versions and params; my 07:30Z reply agreed with no change.
  Both are in `internal/lanes/one-stage-e2e/`.
  - `Q_template_instance` v0 takes `{template}`.
  - `Q_template_instances` v0 takes `{templates}`.
  - The one precision: the template is matched by its descriptor id (the `callees` entry), which is what a verifier reads.
    That equals `.id` for `RoPEHead_v1{D=64}`, so A1 and A2 are unchanged. A3's RMSNorm templates must carry descriptor ids
    (float `EPS`).
- **Core pieces:**
  - an evaluator, `TemplatePartition`: units, gate intervals, inputs, outputs and the derived committed set;
  - `evaluate` / `verify` dispatch;
  - a per-query parameter check in `QUERIES`;
  - pinned vectors from descriptor bytes, with every refusal (`tests/ir/template_instance_vectors.json`).
  - `Q_word` and its vectors are unchanged.
- **Reproduction.** Core builds and evaluates one-stage's objects identically: A2 digest `17478e85…` (183,680 units) and A1
  digest `ba90a294…`.
- **Tests:** 1243 passed across core, repository, protocols and flock; vLLM `query` passes.
- **Lean:** a handoff to flock-verifier to accept and port both queries from the vectors (#118 hard-codes `Q_word`).
- **#120 status** (format spec, 0640Z handoff): the vLLM suite has the same 11 failures as #111's branch, so it adds no
  regressions.
