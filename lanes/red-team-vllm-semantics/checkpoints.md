20260930T0712Z open: started; fixtures fetched (14 replicas), replaying ml tests on CPU
20260930T0731Z open: CPU attack run r20260930-072846-85f1 running; sm_120 cuBLAS attack Kueue job 42 (rt-sem-cublas-1) pending
20260930T0802Z gemm-ampere-step, gemm-hopper-step labelled conditions on r20260930-074229-b966 (underflow floor unpinned); cuBLAS stability job rt-sem-cublas-4 queued (Kueue 74); edges job (mufu, rope, silu, router, sm_120 floor) next
20260930T0823Z labelled: no-nondeterministic-split-k, clock-and-power, fp8-per-tensor-scale-order (conditions, handoff: sm_120 order differs from ScaledMmFp8_v1), splits, fa-check-inf, capture-complete, p2p (conditions), fold-sm120 (broken, known; handoff); edges job Kueue 88 waiting for a GPU
20260930T0825Z 14/22 labelled (1 broken: fold-sm120-linears); edges job 88 queued STARTING; scripts synced to scripts/
20260930T0930Z 21/22 labelled; silu-edge-cases broken (handoff 0930Z, also RoPE hi-contraction), router holds, block128/rope/mufu/moe-dot/fa2 conditions; cuBLAS cross-die rerun Kueue 123 queued
20260930T1036Z 22/22 labelled; cublas-selection-stable conditions, cross-die identical (r20260930-101118-5f25 vs 10e2); lane done, no GPU jobs outstanding
