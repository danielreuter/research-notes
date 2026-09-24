### Δ_commit — HuggingFaceTB/SmolLM2-135M (B0), workload `smollm2-135m__bf16__l40s__tp1__b1__i256__o32__mixed__greedy__bi-eager.json`, committer `native_collect_v2b`, 1 interleaved pairs [measured]

| metric | control (mean) | instrumented (mean) | Δ (mean over pairs) | 95% CI (bootstrap over pairs) |
|---|---:|---:|---:|---:|
| end-to-end wall (ms) | 588.27 | 912.34 | **+55.09 %** (+324.07 ms) | [+nan %, +nan %] |
| decode step wall (ms, mean) | 17.682 | 21.783 | +23.19 % | [+nan %, +nan %] |
| prefill step wall (ms) | 22.436 | 215.270 | +859.50 % | [+nan %, +nan %] |
| generated tokens/s | 54.4 | 35.1 | -35.52 % | |
| peak GPU alloc (GB) | 24.333 | 24.388 | | |
| host RSS after run (MB) | 2598 | 2854 | | |

tokens identical across all runs/arms: **True** (BI=1)

| component (instrumented, per run, mean) | ms | bytes | note |
|---|---:|---:|---|
| acquisition | 2.72 |  | host wall of the component (hashing/root on the worker thread, overlapped) |
| movement | 11.64 | 439732860 | host wall of the component (hashing/root on the worker thread, overlapped) |
| hashing | 907.63 | 439732860 | host wall of the component (hashing/root on the worker thread, overlapped) |
| root_finalisation | 0.76 |  | host wall of the component (hashing/root on the worker thread, overlapped) |
| opening_generation | 0.00 |  | host wall of the component (hashing/root on the worker thread, overlapped) |
| wait | 0.57 |  | host wall of the component (hashing/root on the worker thread, overlapped) |

root-ready delay (last step end → run root): mean 1.60 ms, max 1.60 ms; backlog max 0 steps; bytes bound per run 439,732,860 in 1,717,737 leaves (12640 tensors, 32 steps); persistent 903,359 B; staging (pinned, in use) 740,700,160 B; values retained 439,732,860 B; openings 64/64 verified (884 B mean); weight registration 2.78 s for 270,079,072 B (once, excluded)

steady state — mean hashing time per decode step (ms) by step index: 1:14.03, 2:25.14, 3:21.60, 4:22.47, 5:21.95, 6:21.58, 7:21.48, 8:21.54, 9:22.61, 10:22.38, 11:22.35, 12:21.28, 13:21.66, 14:22.28, 15:21.61, 16:22.09, 17:21.49, 18:23.21, 19:21.84, 20:21.68, 21:22.83, 22:22.97, 23:22.09, 24:22.11, 25:22.50, 26:23.20, 27:21.97, 28:22.36, 29:22.03, 30:21.96, 31:21.90
growth second half / first half: +3.1%
