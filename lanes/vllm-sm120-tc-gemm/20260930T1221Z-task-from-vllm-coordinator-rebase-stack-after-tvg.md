---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-tc-gemm (bc-049fc756) · kind: task (blocks your next train) · from: vllm-coordinator · created: 2026-09-30T12:21Z

# TVG landed (main `1c10b00c`: #486, #469, #528, #536). Your stack now conflicts with main. Two steps are already done for you

**Done by me** (merges only, pushed to your branches):
- **#483** `cursor/vllm-sm120-bias-epilogue-422d` → **`753864f7`**
- **#501** `cursor/vllm-sm120-gemv-bias-422d` → **`dd3006f3`**

Both merge main into the branch. `targets.py` is resolved as a union: your `gemm_bias_spec`/`gemv_bias_spec` kept, main's `attention_spec(…, own_rows)` taken, and your names added to main's `__all__`. The registry imports, and the GEMM/bias/FA2 tests pass.

**One thing I left for you: P10.** Main's `program/kernels/rows.py` is exactly 800 lines now, the module limit.
- On #483 it's **805** and on #501 **806**: your `EVALUATORS`/`_check_targets`/`_row` registrations. P10 fails.
- **Split, don't raise the cap:** e.g. move the bias-family evaluator entries and `_row` registrations into `bias_epilogue_rows.py` (or a `rows_bias.py`), registered from there, so `rows.py` drops back to ≤ 800.
- Do it on #483 first, then merge #483 into #501.

**Then, in stack order, merge main (or the updated parent) into each and send me the heads:**
- **#535** (`3595b5fb`): conflicts in `targets.py` and `rules/vocab.py`;
- **#539** (`6a96fdcd`): the same;
- **#516** (`58c44852`) and **#524** (`ca71edd0`): `targets.py`, plus `rows.py` growth.
- #515 and #523 (core) are clean on main.

**Decisions:**
- **#535:** job 162 may land after the quiet hour. I'll grant #535 on its pass at the rebased head.
- **#539's Commit-side `step_rows` check:** after, not before, the B8 cells. An early-EOS mismatch shows up as a replay `fail`, not a false pass.
- **DeepGEMM on sm_120:** `VLLM_USE_DEEP_GEMM=0` is an engine setting, so it's Daniel's decision; I'm raising it. **Keep going on the packed quantizer.** Hold the DeepGEMM `fp8_gemm_nt` Definition until Daniel answers.
