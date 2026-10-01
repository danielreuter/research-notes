---
cursor:
  subagentId: "bc-2840854d-2bab-5494-9ec4-56acb28b827a"
---

lane: circuits-commit-phases · kind: checkpoint · to: @circuits · created: 2026-10-01T16:58Z

**Route 1 debug row: the served logits equal the Program's call-boundary words exactly (9:58 AM PDT).** On Gemma-2-2B B1, all
24,576,000 of 24,576,000 words agree, on every one of the 32 engine steps and all three logits-processor targets: the `lm_head` GEMM output
(`triton_launch_N/out`), `div_N/out` and `tanh_N/out`. There are no mismatches, so there are no first mismatches to report.

**What ran.**
- Branch: `cursor/served-logits-tap-827a` @ `dff455907`. It is debug code, not for merge: the off-hold cov tree plus `served_tap_debug.py`,
  switched on by `VERITY_SERVED_TAP`.
- Tree: synced to node 1 as `cursor-served-logits-tap-827a`.
- Row: `cov-cg04-served-tap`, with cg04-2's config, through the queue.
  - The Build was offloaded to node 2, where the 9:00 AM PDT timed window paused it for 16 min.
  - The first GPU try failed on a permission error: the sweep directory is owned by root, so the tap's output directory now lives inside the
    row directory. I resumed at the GPU task as try 1.

**How the comparison works.**
- During each `logits_processor` forward, a `TorchFunctionMode` clones every tensor that a torch function returns on the GPU. It is
  installed by a pre-hook that runs after the call-boundary source's pre-hook and removed by a forward hook.
- Each target's host-evaluated words are compared, word for word, with the capture of the target's own op, and also with whichever capture
  of the same size agrees with them most.
- `div` and `tanh` match their own ops.
- The GEMM output matches at `logits[..., :org_vocab_size]`. This slice is a full-width view of the output buffer of the batch-invariant
  Triton matmul. The view is the first torch-function result to hold the GEMM's words, because `linear_batch_invariant` passes through
  `matmul_batch_invariant`, which fills a `torch.empty` buffer.

**The run itself is unchanged.** Compared with `cov-cg04-oh-after`, all of these are the same:
- run root `c22469530fd2f335`;
- the binding map, tokens, and manifest and program digests;
- the commit reason, openings 64/64 and seed `13989422147988288309`;
- replay 460/460 and `commit_pass`.

The tap's own clones and host copies (each step it also copies the transposed 256000 × 2304 weight view) put the recorded pass at 99.6 s,
against 62.2 s without it. That is the cost of debugging, not of the design.

Evidence: `art:b427d3daa9ecf37d49e3b88a6f2c5b0caca31b457cd4a67575ec85fd51ca3dc1`.

**What it gives Route 1, and its limits.**
- On this row, the root can bind the served `lm_head`, `div` and `tanh` from before release. A source would claim these identities through
  `call_boundary_source.CLAIMS` and acquire the GPU tensors, and the logits body's host evaluation would leave the recorded pass. That
  evaluation is the `dense_rows` GEMM emulation that dominates the hold.
- Because the words are equal, the root stays `c22469530fd2f335`, which makes the golden a strong one.
- What the root attests changes. Today these words are the Program's by construction. With the tap they are served words, checked only
  through the replay's sampled openings of their producing Calls.
- The 105 GemmaRMSNorm bodies are not tested here and would stay host-evaluated.
- The evidence covers one row: RTX PRO 6000, bi-eager, B1.

**Yours to decide:**
1. **The claiming source.** Build it on a branch, with a golden that requires the same root; no PR until you say so.
2. **The norm bodies.** Point the same debug tap at them (`VERITY_SERVED_TAP_MODULES=layernorm`), which costs one more row.
3. **Wider evidence.** A B>1 row or a non-bi row first, since a non-bi row's `lm_head` is not the batch-invariant Triton matmul.
