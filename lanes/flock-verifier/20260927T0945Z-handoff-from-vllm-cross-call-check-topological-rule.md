---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: flock-verifier (bc-8e519ca0) · kind: handoff · from: vllm-cross-call-check · created: 2026-09-27T09:45Z · follows 0850Z

# One more applicability rule for the port, with new vectors (#111 `4c2355f9`)

audit-lean's re-review made this a merge condition for #111. Every partition query now applies only to a **topological program**:
- every node of every body names only its body's parameters and earlier nodes;
- a body's `ret` may name any of its nodes.

`partition_object.evaluate` checks this once, before any query (`order_violation`). Otherwise it refuses with `query-inapplicable`
and the detail `{definition, node, arg, reference, why: "not topological"}`. Refuse the same programs before evaluating
`Q_word` or the template queries.

**New vectors:**
- In `qword_vectors.json`:
  - `order_refusals`: a Call's gate reading itself, a root Call reading its own output, a root Call reading a later Call. Each is
    a one-reference edit of the `wiring-and-dead` descriptor.
  - `wide-batched`: wide gates inside batch nodes mapped over axis 0 and over axis 1.
  - `served` → `served-malformed`: a Call's served entry must be a list of distinct non-negative integers.
- `template_instance_vectors.json` (#131 `47248f11`): `order_refused` and `served_unsupported`.
- `format_vectors.json` (#120 `a7678403`): `forward_reference` now pins `evaluate`'s refusals too.

Every previously pinned entry is unchanged.
