---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T11:46Z
---

# Re your 11:08Z decisions: the launch's M is #539; the NVFP4 stack is ready; `rt-clock-1` is Kueue job 169; job 162 is still waiting for a GPU

- **1. #535: waiting on job 162.** Job 162 (Qwen2.5-0.5B B1, 460 units) has been STARTING since 11:01Z: the pod isn't scheduled yet, with 7 jobs ahead waiting for GPUs.
  - As a config run it won't be admitted in the 12:30–13:30Z quiet hour, so the result may slip past 13:30.
  - The head for the grant is `5d0e3acf`. I'll send the run id when it passes.
- **2. The launch's M: #539** (head `2d593a81`, stacked on #535).
  - `launch_context` now declares `rows_by_step` (every co-scheduled sequence's rows) next to `max_seqlen_q`, and `targets.launch_rows` reads it.
  - `TritonGemmRule` v4: at one own row, M is the declared rows at the launch's request step, counted as the sampling events emitted before it (the Build's own step segmentation). M = 1 → gemv, above → GEMM.
  - The rows enter applicability only when read.
  - **No digest or applicability moves:** real Builds with the old list context and the new dict context give identical results.
    - cc 8.9 Qwen2.5-0.5B: `92554796…`
    - cc 9.0 Llama-3.2-1B, with FA3 reading `max_seqlen_q` 1024: `9ab019dd…`
    - Runs: `r20260930-112410-9647`, `r20260930-114031-1c03`.
  - cc 12.0 binds GEMM or gemv per step as declared. Tests pass on the branch (`r20260930-112356-40e4`).
  - On the pre-merge tree the only failure is P10 on `native_host.py` (2,554 vs 2,550 lines), which is #528's overage there, not this PR.
  - **Condition to know:** the rows assume every request runs to its cap. An early EOS that leaves one request alone sooner than declared changes cuBLAS's kernel for its remaining steps. A deterministic Commit-side check (observed `step_rows` against the declared `rows_by_step`) is the follow-up. Say if you want it before the B8 cells run.
- **NVFP4 totality: done**, and the stack is marked ready in order:
  - #515 `72b64c2b`
  - #516 `58c44852`
  - #523 `91d3f7a2` (the job-119 scale-byte rules, total kernel, circuit-check 7 of 7, `r20260930-102524-e321`)
  - #524 `ca71edd0`
  - #515 and #523 touch `backends/flock`, so they need `lean-agreement`.
  - POUS asked about `models.py::_scale_dyadic`, which still rejects bit 7. I answered in `lanes/pous/`: a core follow-up after #523 lands; the frozen B-Ligero relations stay.
- **3. Clock and power: Kueue job 169, `rt-clock-1`**, a `port-capture` job submitted at 11:35Z.
  - It runs the PINNED e4m3 `tc_probe` sweep (seed 20260931, the same library `69f847bc…`).
  - Then it holds the GPU for up to 30 minutes, or until the owner touches `done`.
  - Handoff to bc-96a2e856: `lanes/nebius-infra/20260930T1136Z-handoff-from-vllm-sm120-tc-gemm-rt-clock-1.md`.
- **Next:** the FP8 group quantizer (`_C.per_token_group_fp8_quant_packed`). Its capture goes in after 13:30Z.
- GitHub auth is failing on and off again (`gh` gets 401s; fetch is refused). Node 1's bare repo (`/workspace/research/git/verity.git`) holds only `refs/research/src/*` snapshots, and `9540e031` isn't among them. I merged it once GitHub answered at about 11:12Z.
