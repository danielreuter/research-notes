---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T04:25Z

# Re-baseline epoch: the plan, and three asks (the re-key, the sweep lane, merge order)

The plan is `lanes/coordinator/20260928T0420Z-plan-vllm-rebaseline-epoch.md`. The vyv- guard is re-armed (cap $1,005, deadline
18:00Z).

1. **Please relay to the consolidation coordinator (bc-e373566b), about the `AmpereBF16TcDot16` v1/v2 re-key.** The vLLM side needs,
   before any GPU re-record:
   - the final id the served L40S rows bind (today `AmpereBF16TcDot16_v1`, with `_v2` in core);
   - whether the re-key changes the step's semantics or only its id;
   - the core PR number.
   The vLLM rebinding goes in with S4 (lane `vllm-epoch-prep`), so the L40S Program digests move once. Replies to
   `lanes/vllm-coordinator/`.
2. **Please relay to the sweep lane (bc-ea1c2c4f)** that it will receive every row's new digests from me, as a table: step, request and
   workload Programs, manifest, run root, partition digest. I couldn't find its lane folder; tell me where it wants them.
3. **Merge order for the epoch:**
   - #197, the composite top-p keep word (bc-9916bbb1) and the re-key;
   - #111, then the switch PRs S2 → S3 → S4 → S1;
   - then the GPU re-record.
   - No other PR that moves a digest of record should merge between G0 and the rows' writes.
