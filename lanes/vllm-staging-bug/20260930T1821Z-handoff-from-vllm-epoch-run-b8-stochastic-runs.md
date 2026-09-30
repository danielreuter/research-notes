---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: handoff · to: vllm-staging-bug · cc: vLLM coordinator · created: 2026-09-30T18:21Z

**The runs you asked for: 5 failing and 1 passing stochastic batch-8 Commits, plus the 3 failing batch-1 SmolLM2-135M Gumbel ones.** They're
all sm_120 (RTX PRO 6000) config runs on the same Verity content: the run branch `cursor/coverage-v0-2622`, pre-merge #481 #487 #502
#483 #501 #551 #561 on main `1c10b00c`. The trees listed differ only in infra/nebius merges. Every failure reads
`bounded staging: hit step N (plan ...) ran X bytes against a plan of X-256: the prescribed layout changed mid-step`, then
`ValueError: run root must be 32 bytes` in `challenge_positions`. The warm-up reports 0 plan mismatches each time.

| id | model, sampler, batch, tokens | run (store) | tree | failing steps |
|---|---|---|---|---|
| g218 | Llama-3.2-1B, top-p 0.95, b8, 256/32 | `r20260930-175139-751d` | `43092a5e` | 9–11 (5 tokens) |
| g219 | Llama-3.2-1B, Gumbel, b8, 256/32 | `r20260930-173955-4cda` | `aaf4ae3f` | 2 (7 tokens) |
| g222 | SmolLM2-360M, Gumbel, b8, 256/32 | `r20260930-173620-f7ab` | `aaf4ae3f` | 0 (prefill, 852 tokens) |
| g230 | SmolLM2-135M, top-p 0.95, b8, 256/32 | `r20260930-171519-ac88` | `aaf4ae3f` | 0 (prefill, 948 tokens) |
| g231 | SmolLM2-135M, Gumbel, b8, 256/32 | `r20260930-170004-ca9a` | `aaf4ae3f` | every decode step, 1–31 |
| g221 | SmolLM2-360M, top-p 0.95, b8, 256/32 | `r20260930-173751-e3c0` | `aaf4ae3f` | none: **passed** |
| g253 (1st) | SmolLM2-135M, Gumbel, b1, 256/32 | `r20260930-161743-b1cc` | `9920af53` | every decode step, 1–31 |
| g253 (2nd) | same | `r20260930-165604-f57a` | `aaf4ae3f` | every decode step, 1–31 |
| g247 | SmolLM2-135M, Gumbel, b1, 1024/128 | `r20260930-163836-1470` | `9920af53` | every decode step, 1–127 |

**Logs on vy-nebius-1:** `/workspace/jobs/cov/<name>/<row>/commit.log`, where `<name>` is `cov-g218`, `cov-g219`, `cov-g222`,
`cov-g230`, `cov-g231`, `cov-g221`, `cov-g253-2`, `cov-g253-3` or `cov-g247`, and `<row>` is the one row directory under it. The
same directory holds `timeline.jsonl`, `stages.txt` and `commit/` (the layouts and bounded-warm-up JSON). Run directories are under
`/workspace/jobs/runs/<run>`. Workloads are `integrations/vllm/workloads/<row>.json` in the run tree (the grid ones are untracked:
generate them with `verity-vllm workload --row-id <row> ... --target '{"compute_capability": [12, 0], "num_sms": 188}'`).

TinyLlama top-p and Gumbel at batch 8 (g210, g211) are still running; I'll add them here when they end. The 130 held deployments wait
for your fix.

**Update, 18:41Z: TinyLlama at batch 8, one each way.**
- g211, TinyLlama-1.1B, Gumbel, b8, 256/32: run `r20260930-181116-39ad`, tree `43092a5e`. It **failed** on steps 1, 11 and 12: 39,935,744 against 39,935,488 bytes at 8 tokens, and 19,968,000 against 19,967,744 at 4. Log: `/workspace/jobs/cov/cov-g211/<row>/commit.log`.
- g210, TinyLlama-1.1B, top-p 0.95, b8, 256/32: run `r20260930-180909-8ed9`. It **passed** 460/460.

Batch-8 stochastic Commits now stand at 6 failing and 2 passing (g221, g210). Both passes used top-p 0.95. Every Gumbel run at batch 8 has failed.
