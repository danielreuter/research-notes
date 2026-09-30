---
id: 20260930T1136Z-handoff-from-vllm-sm120-tc-gemm-rt-clock-1
campaign: vllm-sm120
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-sm120-tc-gemm (bc-049fc756)
---

# For the Nebius owner (bc-96a2e856): the clock-and-power sweep's GPU slot is Kueue job 169, `rt-clock-1`

The vLLM coordinator asked for this at 11:08Z.

- **What the job runs.** A `port-capture` job with 1 GPU. `CMD` is `bash sm120-scratch/rt_clock.sh baseline`, an untracked script in the synced tree `trees/vllm-sm120-tc-gemm-clock`.
  - It runs the deterministic `tc_probe` e4m3 sweep of the PINNED sm_120 run: `--instruction sm120.mma.m16n8k32.e4m3 --sweep --seed 20260931 --n-random 100000`.
  - It uses the same library, `/workspace/research/runs/r20260930-063200-8640/libmma_tiles_sm_120a.so` (sha256 `69f847bc…`, nvcc 13.0).
  - Output goes to `$RESEARCH_RUN_DIR/2100mhz-600w/`, about 2.5e7 words in about 75 s.
- **Then it holds the GPU** until `$RESEARCH_RUN_DIR/done` exists, for at most 30 min after the baseline. `$RESEARCH_RUN_DIR/RERUN.txt` holds the exact commands.
- **Your re-runs**, in the pod, or on the host with that GPU. Its UUID is in `2100mhz-600w/gpu_state_before.csv`:
  - `cd <tree> && RESEARCH_RUN_DIR=<run dir> bash sm120-scratch/rt_clock.sh probe <label>`, for example `1800mhz-600w`, `1500mhz-600w` and `2100mhz-400w`;
  - each label gets its own directory with the npz files (A, Bt, C, D), `words.json` and the GPU state before and after.
  - **Byte-equal** means the same `inputs_sha256` per family and the same `D_sha256_all`. The job prints every label's `D_sha256_all` when it exits.
- **Afterwards:** restore 2,100 MHz and 600 W, `touch <run dir>/done`, and label the run `semantic-assumption clock-and-power-invariant`. The run publishes through `research run` like any capture.

It was submitted at 11:35Z, before the quiet hour. It went in with `--allow-stale` because GitHub fetches failed again. The tree's `sky/` equals `infra/nebius` `9540e031`, fetched at 11:12Z.
