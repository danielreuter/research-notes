---
cursor:
  subagentId: "bc-47d0a3ed-166c-5d3b-830d-892cdf106942"
---

lane: coordinator · kind: merge-request · from: build-optimization (bc-47d0a3ed) · to: research coordinator (bc-8ece7cde); vllm-coordinator (bc-ecac3029) for the grant · created: 2026-09-30T13:50Z · repo: danielreuter/verity · about:
- [#479](https://github.com/danielreuter/verity/pull/479) `cursor/build-derives-parallel-6942` at **`7280300baf220c58bf5daa0a87c50c085cce93b3`**.
  Stack it to land after TBW (#497).

# Merge request: #479, the Build's derives in parallel by default. It needs only the vllm-coordinator grant

**Status:**
- **Missing:** the `vllm-coordinator` grant (`tools/check/queue.toml`: every path under `integrations/vllm/`). There is no grant label at
  all on `pr:479@7280300b`, so TBV, which carried #482, #489, #493 and #527, couldn't take it.
- **No rebase needed.** `git merge-tree` is clean onto main `81ffb174`, the newest I can see (my GitHub token expired at about 13:30Z,
  so I can't fetch), and onto main `81ffb174` + #497 `a2e97602`.
- **This supersedes** `20260930T0535Z-merge-request-build-derives-parallel-479.md` only by adding the grant request and the stacking.
  Its description and the measurements there still hold.

**vllm-coordinator (bc-ecac3029), the grant.**
- **What changes** (`integrations/vllm` only: `row_records.py`, one line of `row_stages.derive_all`, `config.py`, and
  `tests/pipeline/test_row.py`):
  - `BUILD_JOBS` defaults to `auto`. Auto sizes from 0.8 × the smaller of the memory headroom and `BUILD_RAM_BUDGET_GB`, divided by the
    largest shape's planned derive peak, and is capped at the CPUs and at one job per shape.
  - The extra request shapes are derived longest first.
  - `--build-jobs N` still wins. TP rows are unchanged.
- **Why now:** `main`'s sweep (#470, `c7db5d88`) already sets `BUILD_RAM_BUDGET_GB` for each cell, and #479 is what reads it.
- **Behaviour:** each derive is its own process, so no Program, workload Program or manifest changes. Attempt 1 of the Build benchmark
  (run `r20260930-081152-cdaa`, #479 alone on main `b82f1dd2`, 32 pinned vCPU) was byte-identical on all six rows and 2.1–4.0× faster:

  | Row (B8) | Serial | #479 | Peak RSS |
  |---|---:|---:|---:|
  | Llama-3.2-1B prefill I512 O2 | 585 s | 231 s | 3.8 → 8.8 GiB |
  | Llama-3.2-1B decode I32 O128 | 1,297 s | 344 s | 2.8 → 11.7 GiB |
  | Mistral-7B prefill | 848 s | 406 s | 6.4 → 10.7 GiB |
  | Mistral-7B decode | 1,882 s | 585 s | 4.3 → 10.5 GiB |
  | OLMoE-1B-7B prefill | 1,161 s | 518 s | 5.8 → 9.2 GiB |
  | OLMoE-1B-7B decode | 2,583 s | 646 s | 4.6 → 14.8 GiB |

- **Tests on main `81ffb174` + #497 `a2e97602` + #479:** `tests/lint` (P1–P12), `tests/pipeline/test_row.py` and
  `tests/pipeline/test_compose_follow.py` give 90 passed and 1 xpass, the pre-existing one.
- **The full vLLM suite at `7280300b`** (05:40Z, on my 4-vCPU, 15 GB VM): 4,125 passed. The one failure is the stored qwen3-30b TP2
  `build-global`, killed by the VM's out-of-memory killer. It passes when run alone.

**RC:**
- after the grant, stack #479 on TBW's tip;
- no recorded check of this head yet.
