---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T07:29Z
---

# (2) PINNED done; #487 ready; the target moved to a new core PR #502; #483's head changed (a lint fix); gemv PR #501 open; two decisions for you

## What landed since 06:13Z
- **(2) PINNED, computed by `trust.py`:** dossier `art:b3074aba4c9ddeef7f87454bfc23e73a5a3c5f73f1676260545115fe8589cc89` for `fp8-sm120-mma-draft/2026-09-30` (e4m3). It is PRESERVED, with its labels on the remote.
  - P1–P3: Kueue job 14, run `r20260930-063457-5410`, 25,041,024 elements, 0 mismatches.
  - P4: host compile check `r20260930-063200-8640`, 1 QMMA per tile.
  - P5: vacuous.
  - The clock lock and the driver are in the dossier's hardware records, as a `note` label on the sweep: `vy-clocks.service` locks 2,100 / 12,481 MHz; at job start nvidia-smi read SM 2,092 MHz, P0, no clock event reasons; driver 580.173.02. `clocks.txt` and `gpu.csv` are preserved in run `r20260930-065108-41b8`.
- **e5m2 computes HYPOTHESIS:** `art:164a66c8084c4afd42d3b4ecb2f30676e6364a17e6e5877bed07cefc8ddd04a5`, from run `r20260930-063527-4d6b` (25,041,024 elements, 0 mismatches). **The missing criterion is P1:** no target wraps the e5m2 id, so trust uses the sm_120 default anchor (the RTX 5090), where it has no run. I left the default alone as you decided.
- **#487 is marked ready.** It's now constants only: the models, tc_probe's sm_120 FP8 entries and fixes, and the `rtxpro6000` SKU family. On vy-nebius-1, run `r20260930-071347-585c`, the six affected suites show no failure that base lacks.
- **New core PR #502** (draft, stacked on #487): registry ids, target and census.
  - `sm120.mma.m16n8k32.e4m3` is `pinned`, with the e4m3 dossier.
  - `sm120.mma.m16n8k32.e5m2` is `hypothesis`, with the e5m2 dossier.
  - The target `FP8_SM120_MMA` and the census lines are here too. Run `r20260930-072548-9009` shows no failure that base lacks.
- **Why the target moved:** a Target in `TARGETS` needs its instruction in the registry, a census hardware line and a census subcircuit. #487 with the target broke `backends/numerical` (161 failures against 2 on base). So "(3) separate from #487" became "#502 stacked on #487", since the registry needs #487's models.
- **#483's head is now `7cea7a99`,** not `60549d3b`. `tests/test_no_by_name_rules.py` flagged `fam in F32_BIAS_EPILOGUE_FAMILIES` as a new by-name rule; the earlier lint scans didn't include this test. The epilogue is now a field on the target record (`GemmTarget.bias_epilogue = "f32"` on blackwell_consumer). The bindings are unchanged, so 720/720 still stands. **It needs your grant at 7cea7a99.** The full quick vLLM suite on it is running (below).
- **(1) gemv:** **#501** is open (draft, stacked on #483). `GemvBiasF32_v1{K,N,V,T}`, bound on blackwell_consumer, M = 1 with a bias; `unsupported:gemv-table` for an unlisted (K,N).
  - The 14-entry table was recovered on vy-nebius-1 (Kueue job 13, run `r20260930-063002-c5fe`), the same as on RunPod.
  - Acceptance run `r20260930-063644-caa1`: **exact on all 14 table entries** (22,848 of 22,848 row coordinates; 112 of 112 through the Definition), circuit-check 3/3 with 0 failures and 0 warnings.
  - Assumptions: `gemv-tree(cuBLAS table v1)`, `cublas-selection-stable(shape, workspace, streams)`.

## Decisions for you
1. **#502's census line.** A target's overhead divides by a census peak, so #502 adds `rtx-pro-6000-server/e4m3` = **1,000 TFLOPS dense at FP32 accumulate**. Sources: the Server Edition page (FP8 2 PFLOPS, the sparse figure) and the RTX PRO whitepaper's Table 4 (the Workstation Edition, where FP32 accumulate is full rate). The methodology notes the page is rounded; at the 2,430 MHz maximum SM clock the per-clock rate gives 935.6. **It also adds an empty draft row to Table 2.** Accept it, or name the figure you want.
2. **e5m2 PINNED:** would need an e5m2 target anchored on the PRO 6000 (like the e4m3 one), or one 5090 sweep. Say if you want either.

## Running and pending
- **Full quick vLLM suite, serial** (the job venv has no pytest-xdist), on vy-nebius-1: #501 head `r20260930-070123-ef8d`, #483 head `r20260930-070137-f224`, base `r20260930-070150-67fc`. I'll post the diff when they finish.
- **(4)** isn't started (low priority, no pods).
- **GitHub auth:** `git fetch` and `gh` from this VM return 401 since about 07:27Z. Pushes before that went through, and the PR tool still works. All heads above are on origin.

## Kueue notes (for the template owner)
- (a) The job tree isn't writable as uid 1000. I needed a local `pod_bootstrap.sh --cpu --out /workspace/jobs/bootstrap-out-<lane>` override in `port-capture.yaml`.
- (b) The containers have no nvcc or cuobjdump. I compile on the host with a direct CPU run, then `tc_probe --library`.
- (c) #485's telemetry fix is needed in job trees.
- (d) `/workspace/jobs/venv312` has no pytest-xdist.

## Spend
No new pods; vy-nebius-1 jobs only. My share stays about $6.40 of $25.
