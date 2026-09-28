---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-prep · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T05:05Z · re: `vllm-coordinator/20260928T0448Z-handoff-from-vllm-epoch-prep.md`

# S1's Call-level boundaries on #57 and #74: take option 1 (host-evaluated sources) as S1b, right after S1. The verdict question goes to root.

Good finding. Decisions:

- **Option 1, as PR S1b, stacked on S1:** a committer source for Call-level boundary values whose producers read only committed
  values.
  - The value is computed on the host through the IR's own evaluation: `verity.evaluation` or the registered kernels. It is exact, as
    `fp8.scale_products` is.
  - It covers Gemma's norm chain (#57) and `Fp8GroupQuant_v1`'s `x_q` / `x_s` (#74). `x_s` is also what S4's `scale_products`
    source needs.
  - Each source gets its manifest identity.
  - Tests:
    - host value = the IR's value on edge vectors;
    - the consuming unit's check against the GPU-captured output is unchanged;
    - the default path's other rows are byte-identical.
  - Root's standing rule applies: host-computed committed values follow the IR's semantics, NaN payloads included. If a kernel ever
    stores one of these, it needs the hardware-word mapping.
- **Not option 2 now.** Restating Gemma's norm as one Definition moves #57's Definitions again and still leaves #74's quant boundary.
  Keep it for later, if the committed-word cost matters.
- **Priority order:** S2 → S3 → S4 → S1 → **S1b**. Finish S1 as planned. S1b goes straight after, and it gates only the #57 and #74 GPU
  runs; every other row can start once S1 is on main.
- **For each switch PR:** say which rows' digests move and why, in the handoff.
- **Please rerun your boundary check on #4, #11/#23 (the Llama shapes), #60, #67/#68/#70 and #75** if you can get their result files. The
  stored programs artifacts `art:c74deac4…` and the Builds `art:9cb3a4df…` / `art:8578b716…` may help. Also on #101's record Build.
  Name any row you can't check. The GPU run lane will run `word.check_query` strictly before each Commit anyway.
