### Δ_commit — HuggingFaceTB/SmolLM2-135M (B0), workload `smollm2-135m__bf16__l40s__tp1__b1__i256__o32__mixed__greedy__bi-eager.json`, committer `native_collect_v2b`, 1 interleaved pairs [measured]

| metric | control (mean) | instrumented (mean) | Δ (mean over pairs) | 95% CI (bootstrap over pairs) |
|---|---:|---:|---:|---:|
| end-to-end wall (ms) | 565.19 | 902.34 | **+59.65 %** (+337.15 ms) | [+nan %, +nan %] |
| decode step wall (ms, mean) | 17.097 | 21.249 | +24.29 % | [+nan %, +nan %] |
| prefill step wall (ms) | 18.085 | 222.368 | +1129.55 % | [+nan %, +nan %] |
| generated tokens/s | 56.6 | 35.5 | -37.36 % | |
| peak GPU alloc (GB) | 24.333 | 24.388 | | |
| host RSS after run (MB) | 2586 | 2842 | | |

tokens identical across all runs/arms: **True** (BI=1)

| component (instrumented, per run, mean) | ms | bytes | note |
|---|---:|---:|---|
| acquisition | 2.52 |  | host wall of the component (hashing/root on the worker thread, overlapped) |
| movement | 11.31 | 439732860 | host wall of the component (hashing/root on the worker thread, overlapped) |
| hashing | 898.86 | 439732860 | host wall of the component (hashing/root on the worker thread, overlapped) |
| root_finalisation | 0.71 |  | host wall of the component (hashing/root on the worker thread, overlapped) |
| opening_generation | 0.00 |  | host wall of the component (hashing/root on the worker thread, overlapped) |
| wait | 0.56 |  | host wall of the component (hashing/root on the worker thread, overlapped) |

root-ready delay (last step end → run root): mean 1.61 ms, max 1.61 ms; backlog max 0 steps; bytes bound per run 439,732,860 in 1,717,737 leaves (12640 tensors, 32 steps); persistent 903,359 B; staging (pinned, in use) 740,700,160 B; values retained 439,732,860 B; openings 64/64 verified (884 B mean); weight registration 2.69 s for 270,079,072 B (once, excluded)

steady state — mean hashing time per decode step (ms) by step index: 1:14.66, 2:25.10, 3:21.78, 4:21.53, 5:21.13, 6:20.80, 7:21.25, 8:21.06, 9:21.59, 10:21.12, 11:21.89, 12:21.02, 13:21.30, 14:26.61, 15:21.55, 16:21.43, 17:21.90, 18:21.48, 19:20.97, 20:21.85, 21:21.42, 22:20.92, 23:21.47, 24:21.21, 25:21.23, 26:21.34, 27:22.01, 28:20.93, 29:21.64, 30:21.16, 31:21.42
growth second half / first half: -0.4%
