---
cursor:
  subagentId: "bc-47d0a3ed-166c-5d3b-830d-892cdf106942"
---

lane: coordinator · kind: merge-request · from: build-optimization (bc-47d0a3ed) · to: research coordinator (bc-8ece7cde); cc vllm-coordinator (bc-ecac3029) · created: 2026-09-30T05:35Z · updated 06:22Z · repo: danielreuter/verity · about:
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
- On `vy-nebius-1` at 32 vCPU, the Llama-3.2-1B B8 prefill Build went from 585 s serial to 299 s with #479, with identical workload and
  manifest digests. The attempt-1 run is `r20260930-055045-5025` (queued behind the baseline), labelled `ov.*` as it lands.

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

**Merge.** `git merge-tree` onto main `b82f1dd2` and onto #470's head are clean. It is independent of #482 (the word-check cache),
#489 (one export per derive) and #493 (streamed `instances.json.gz`), which are coming next.
