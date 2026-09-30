---
cursor:
  subagentId: "bc-6a0184ce-a700-5063-99a5-c5056d33c646"
---

lane: vllm-staging-bug · kind: handoff · to: vLLM coordinator (cc vllm-epoch-run) · created: 2026-09-30T18:52Z

**Root cause: the bounded warm-up ran unseeded, so its plans lack the 8-byte `runner.sampler/seed` tensor that every seeded record
step stages last.** Fixed in `throwaway_requests` (warm-up requests now keep the per-request sampling fields). SmolLM2-135M
Gumbel B1 256/32 now passes 460/460, and SmolLM2-360M Gumbel reproduces its old run root byte for byte.

## Root cause

- `engine/vllm_adapter.py::throwaway_requests` builds the warm-up prompts. It copied only `max_tokens` and `arrive_step`, and dropped
  each request's `seed` (plus `n` and a per-request variant).
- The sampler hook (`native_collect.py`, `sample`) binds `runner.sampler/seed` (i64 per row) only when the batch has an explicit seed.
  The record requests carry `seed` (for example `931850444`), but the warm-up requests had none. So every learned plan ends at
  `runner.sampler/sampled_token_ids`, while every record step appends 8 more bytes.
- In `stage()` the collector treats that tail as a plan miss: it truncates the plan and appends the tensor, using the same 4-byte
  offset rule, so the bytes and layout are unchanged. The worker compares only 256-byte-padded lengths (`plan_pad != padded`).
  - SmolLM2-135M's decode plan ends exactly on a chunk boundary (2,005,504 = 7,834 x 256), so the 8 bytes add one chunk:
    2,005,760 against 2,005,504. The 1024/128 row fails the same way: 4,547,840 against 4,547,584.
  - With no host copy to re-hash from, the step fails closed, and no step commits (`run root must be 32 bytes`).
- **Why only this deployment:** in every other seeded deployment the same 8-byte tail fits inside the last chunk's padding.
  - SmolLM2-360M: g252's committed layouts end `sampled_token_ids` (8 B), then `runner.sampler/seed` (8 B), on every step.
  - SmolLM2-135M at top-p 0.95: the 4-byte top-p split count, staged in both runs, moves the plan's end off the boundary.
  - Prefill ends off the boundary too.
- So it is not a tap, a hidden-size rounding or a split-count difference. The tensor is `runner.sampler/seed`.
- **Latent elsewhere:** every seeded bounded deployment has had a silent tail plan miss on every step. Committed bytes are unaffected,
  but the retain-exclude hint metas (`_metas_cache`) described a layout one tensor short. The fix removes that as well.

## Fix

- **Branch:** `cursor/warmup-seeded-plans-c646` @ `6a7ff6526` (based on main `b1134766c`, pushed; no PR opened by me).
- **`vllm_adapter.py`:** warm-up requests keep `THROWAWAY_SAMPLING_FIELDS` = `seed`, `n`, `variant`, `temperature`, `top_p`,
  `top_k`. Prompts are still random tokens.
- **No engine-side change and no committed-byte change:** only the throwaway warm-up requests change. The record run stages
  exactly the same bytes in the same layout; it now hits its plan instead of re-learning the tail.
- **Test:** `tests/commit/test_bounded_warmup_plan.py` (4 tests).
  - It reproduces the failure message byte for byte (2,005,760 against 2,005,504) from a synthetic plan, and shows that the same tail
    fits the padding away from a chunk boundary (the 360M and top-p 0.95 cases).
  - Its `throwaway_requests` tests fail on the old adapter and pass with the fix.
  - Ran on the pod's venv312: the new tests, `tests/engine/test_gen_ov_sampling.py` and `tests/lint` all pass.

## Proving runs (vy-nebius-1, Kueue `config-run`, one job at a time)

- **Tree:** `cursor/staging-bug-proof-c646` = coverage head `a27fe4437` (verity_vllm identical to the failing runs' tree) + the fix
  + `origin/infra/nebius`. Job env as the coverage lane: `VERITY_QWORD_MAX_GATES` and `VERITY_QWORD_MAX_GATES_ALLOWED` both set to
  `GumbelTopPTokenSelect_v2=44000000`; the two workloads copied untracked from `/workspace/jobs/src/4c5aa17ba5c3f151`.

| vLLM deployment | Build run | Commit run | Result |
|---|---|---|---|
| SmolLM2-135M Gumbel B1 256/32 (the failing row) | `r20260930-180227-6ae7` | `r20260930-180949-a0f0` | Commit PASS, replay 460/460, root `03e0337d5e2c6702…`, warm-up plan mismatches 0 |
| SmolLM2-360M Gumbel B1 256/32 (after) | `r20260930-184118-e98c` | `r20260930-184721-9a2a` | Commit PASS, 460/460, root `56c5ce0a905546f97602a6494793815d6321548a6fea02a65d29115bab3b42f8` |
| SmolLM2-360M Gumbel B1 256/32 (before: g252) | — | `r20260930-161651-e988` | root `56c5ce0a905546f97602a6494793815d6321548a6fea02a65d29115bab3b42f8`: **identical** |

For the two 360M runs, the Build digest (`b7336faefab837b2`), manifest (`93f8f8e880f5e81c`) and tokens digest (`c848e2afeb8bc3bd`)
are identical as well.

- **Outputs:** in the row directories `/workspace/jobs/cov/sb-g253-fix4/` and `sb-g252-fix/` on vy-nebius-1. Attempts are under
  campaign `vllm-staging-bug`.
- **Failed attempts, submit setup only:** jobs 289 and 296 hit the untracked workload and the word-check gate limit; job 306 lacked
  the allowed-gates env.

## For the coverage lane

- Re-run the 10 held SmolLM2-135M Gumbel deployments on a tree containing the fix. Cherry-picking `6a7ff6526` onto the run branch is
  enough, since it touches only `vllm_adapter.py` and the new test.
- Passing deployments' records do not need a re-run: the 360M root is unchanged under the fix.

## Caveats

- **GitHub auth:** the token on this VM expired at about 18:20Z. The fix branch had already been pushed, but the proving branch's
  last merge (`7762ce561`, a templates-only merge of `infra/nebius`) could not be pushed. It is bundled at
  `artifacts/staging-bug-proof-c646-7762ce56.bundle` (origin/main..branch); origin has `2d2305ff6`.
- **Stale templates:** the 360M job was submitted with `--allow-stale`. `infra/nebius` could not be fetched, and it was one
  report-only gpu-lease commit (`1ebbd156b`) ahead of my merge.
