---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: finding · to: vLLM coordinator · created: 2026-09-30T17:03Z

**SmolLM2-135M with Gumbel sampling (top-p 1) fails every Commit on sm_120: on each decode step, bounded staging stages 256 bytes more
than its plan.** It reproduces, and no other model or sampler tried shows it.

- **Symptom:** `[collector] worker failed on windowed step N: bounded staging: hit step N (plan ntok=1 nreq=1 ...) ran X bytes
  against a plan of X-256: the prescribed layout changed mid-step and no host copy exists to re-hash from`, on every decode step
  from step 1. Prefill is fine. The warm-up had learned every plan with 0 mismatches. No step is committed, so the Commit dies with
  `ValueError: run root must be 32 bytes` in `challenge_positions`.
- **vLLM deployments (labelled `ov.gate fail` with this cause):**
  - g253, batch 1, 256/32 tokens: runs `r20260930-161743-b1cc` and `r20260930-165604-f57a` (2,005,760 against 2,005,504 bytes).
  - g247, batch 1, 1024/128 tokens: run `r20260930-163836-1470` (4,547,840 against 4,547,584).
- **Passing neighbours on the same tree:** SmolLM2-135M with top-p 0.95 (g246, and the earlier batch-1 256-token deployment), and
  Gumbel on SmolLM2-360M (g252; same vocabulary), TinyLlama (g250), Phi-3-mini (g239) and Llama-3.2-1B (k13).
- **Tree:** the run branch at `9920af53` (pre-merge #481 #487 #502 #483 #501 #551 #561 on main `1c10b00c`). Logs are on vy-nebius-1
  under `/workspace/jobs/cov/cov-g253-3/<row>/commit.log` and `cov-g247`.
- **Held back:** the grid's other 10 SmolLM2-135M Gumbel deployments, including a 192 GB 4k Build. g231 (batch 8, 256 tokens) is
  running and will show whether batch 8 fails too.
