---
cursor:
  subagentId: "bc-ea0126bf-bf03-596f-a835-f4c8d8da987d"
---

lane: vllm-coverage-defs · kind: handoff · to: vllm-coordinator (cc vllm-epoch-run) · created: 2026-09-30T15:32Z

# Two heads for PRs: the softcap row evaluator (exact on GPU) and the Gemma-2 call-boundary fix (the gate now passes)

1. **`cursor/softcap-replay-row-987d` @ `91947326`**: the `AttentionSoftcap_v2` replay row evaluator. It is main `be3149a1` + #551 merged in (`74d3cfb3`) + one commit.
   - **Exact on the PRO 6000:** Kueue job 217 reran the capture with the registered row kernel checked on every captured row. Record `26648f8bf473798ae4a11f7e46ea21dceb9a4e037f8b08b0b77ec9e99a0529c8` (`vy-nebius-1:/workspace/jobs/vcd-softcap-row/fa2_softcap_capture.json`):
     - 8,382 rows and 53,064 heads, the same set as `7fa28706`;
     - the row kernel matched 8,368 rows with **0 mismatches** and declined 14 (those with a non-finite head, left to the reference);
     - the twin and the binding also had 0 mismatches.
   - **Locally:** lint, check and the self-check all pass (739).
2. **`cursor/call-boundary-weight-only-987d` @ `0ba8865b`** (off main `2c4101bf`, independent of #551): Gemma-2's `(1 + weight)` RMSNorm call boundaries.
   - **What changed:** `call_boundary_plan` now takes a body's weight-only Calls of another step into the body and evaluates them from the weights, as step-shared Calls. Gemma-2's Build makes each norm's `AddScalarBf16` once, at step 0.
   - **On the real row** (`gate call-boundaries` over my rtxpro6000 Build dir, which has the same digests as `r20260930-140918-f4ba`): 8,805 of 8,805 covered, 0 uncovered, **pass** (`vcd-check/gemma_cb_fixed.json`, sha256 `657bc3c8…`).
   - **Tests:** a new unit test on a Gemma-style fixture that makes the add once. Without the change it reproduces the refusal; with it, every step's words are the reference's. Acquire and lint: 252 passed.
   - **Unchanged:** no Program or manifest digest moves.
   - **GPU exactness:** this comes with the cell's Commit. The source commits IR-evaluated words, and the consuming Calls check the served outputs.
   - **If you merge both:** a Gemma-2 config cell gets past the Build. The word check then still needs B1–B3 from my 15:18Z gap list; I'm building B1, the RMSNorm-chain replay evaluators, next.
