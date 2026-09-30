---
cursor:
  subagentId: "bc-47d0a3ed-166c-5d3b-830d-892cdf106942"
---

lane: coordinator · kind: merge-request · from: build-optimization (bc-47d0a3ed) · to: research coordinator (bc-8ece7cde); cc vllm-coordinator (bc-ecac3029) · created: 2026-09-30T05:35Z · updated 09:05Z · repo: danielreuter/verity · about:
- [#479](https://github.com/danielreuter/verity/pull/479) `cursor/build-derives-parallel-6942` at **`7280300b`**, on main `3c924ab9`.

# Merge request: the vLLM Build's derives run in parallel by default (#479). Root: land it first tonight

**Why.** Derives are 55–78% of every B ≥ 8 Build, and the 29 Sep epoch ran every Build 1-wide (`build.jobs = 1`). This is the
overnight Build workstream's first change (`docs/overnight-objectives.md` §1, `docs/build-optimization-plan.md`).

**What changes** (`integrations/vllm` only: `row_records.py`, one line of `row_stages.derive_all`, and `config.py`):
- **`BUILD_JOBS` defaults to `auto`.** Auto sizes from 0.8 × min(memory headroom, `--build-ram-budget-gb`) over the largest shape's
  planned derive peak, capped at the CPUs this process may use and at one job per shape.
- **The planned peak** is a fit over the epoch's 89 stored derives, which bounds each of them without doubling any.
- **The extra request shapes are derived longest first.**
- `--build-jobs N` still wins, and TP rows are unchanged. The RAM budget is the epoch-run lane's request for the sweep driver.

**Behaviour.** No Program or manifest changes: each derive is its own process.
- A SmolLM2 B8 row's ten derives give equal digests serially and three-wide (736 s → 311 s on 4 vCPUs).
- On `vy-nebius-1` at 32 pinned vCPU, attempt 1 (run `r20260930-081152-cdaa`) is #479 alone on main b82f1dd2. It sped up every
  benchmark Build 2.1–4.0× against the serial baseline `r20260930-053403-c8cb`:

  | Row (B8) | Serial | #479 | Peak RSS |
  |---|---:|---:|---:|
  | Llama-3.2-1B prefill | 585 s | 231 s | 3.8 → 8.8 GiB |
  | Llama-3.2-1B decode | 1,297 s | 344 s | 2.8 → 11.7 GiB |
  | Mistral-7B prefill | 848 s | 406 s | 6.4 → 10.7 GiB |
  | Mistral-7B decode | 1,882 s | 585 s | 4.3 → 10.5 GiB |
  | OLMoE-1B-7B prefill | 1,161 s | 518 s | 5.8 → 9.2 GiB |
  | OLMoE-1B-7B decode | 2,583 s | 646 s | 4.6 → 14.8 GiB |

  Every Program, workload and manifest digest is unchanged. Peak RSS rises because derives now overlap, and the plan keeps it under the
  host's headroom and any `BUILD_RAM_BUDGET_GB`.
- **The benchmark numbers are also on the dashboard:** the `ov.*` labels on the attempt-1 run.
- **`main` is ready for it:** its sweep driver (#470) already exports `BUILD_RAM_BUDGET_GB`, which #479 is what reads.

**Tests.** New tests in `tests/pipeline/test_row.py`:
- the planned peak bounds the measured epoch derives;
- auto's sizing by memory, CPUs, shapes and the budget;
- the model's layers are read from the checkpoint's config;
- the row derives in parallel by default, and `--build-jobs 1` still gives one;
- the budget reaches auto;
- longest first.

**Suite** (`uv run tools/check/suites.py integrations/vllm --quick` at `7280300b`, on my 4-vCPU, 15 GB VM):
- 4,125 passed, 318 skipped and 1 failed;
- the failure is `test_the_stored_tp2_moe_builds_merge_with_every_peer_bound[qwen3-30b-a3b…]`: `manifest build-global` was killed
  with signal 9, out of memory on this VM. It fails the same way on the #482 branch, and #479 doesn't touch its path.

**No recorded check yet:** I have no check pod, so it needs a train.

**Merge.** `git merge-tree` onto main `f0da69ad` (09:00Z) is clean. On that merge, `tests/lint` and `tests/pipeline/test_row.py` pass.

**The rest of the line** is in `20260930T0900Z-merge-request-build-v1-482-489-493-497`: #482 (the word-check cache), #489 (one export
per derive), #493 (streamed `instances.json.gz`) and #497 (compose once, beside the derives). #479 goes first. It doesn't depend on
them, and they merge cleanly on top of it.
