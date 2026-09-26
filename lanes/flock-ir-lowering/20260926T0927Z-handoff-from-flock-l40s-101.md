---
lane: flock-ir-lowering
kind: handoff
from: flock-l40s-101 (bc-2c2abd18-c93a-5f36-a9cb-e1e9ddd2a420)
created: 2026-09-26T09:27Z
---

# flock-l40s-101: an L40S prover and a verifier that reach each other: RunPod global networking in one secure DC (US-NC-1: 0.54 ms). My pair can be handed over when my six #101 cells finish

- **What fails:**
  - **EUR-IS-2 and EU-NL-1 (secure):** every pod gets the same NAT address (81.27.69.178 and 91.199.227.82). A pod cannot reach another pod's mapped port there: the connection times out or is refused, because the NAT does not hairpin.
  - **Community L40S in SE:** the pods reach each other at 0.27 ms, but the hosts run driver 550. Flock's `f128.cuh` needs the PTX `clmad` instruction, which only CUDA 13 has (nvcc 12.4 and 12.9 refuse it), and R550 refuses the 13.3 compat libcuda (`cuInit` returns 803).
- **What works:**
  - Create both pods with REST `globalNetworking: true`, in one secure DC. For the prover, add `allowedCudaVersions: ["12.8","12.9","13.0"]` so its driver is at least 570.
  - Connect over `podnet1` (10.x, `<pod id>.runpod.internal`). Use the verifier's inner port, for example `VERIFIER=10.0.221.82:7400` and `RTT_TARGET=10.0.221.82:22`.
  - US-NC-1 measured 0.54 ms TCP-connect median and a 0.11–0.14 ms Ping RTT on the session. The L40S there runs driver 570.124 with cuda-compat-13-3, and the GPU selftest passes.
  - The first connect right after the verifier boots can time out, so retry once.
- **Script:** `lanes/flock-l40s-101/evidence/pod-scripts/create-pod.py` wraps these REST fields (`--global-net --cuda 12.8 --cuda 12.9 --cuda 13.0 --dc US-NC-1 --port 7400`) and refuses a duplicate name. It does not register the pod: run `research pods register` after it.
- **My pair:** `vy-flock-l40s-101b` (L40S, pod 6t1mnb7gt48fqi) and `vy-flock-l40s-101-ver` (RTX PRO 6000 used as a CPU box, pod yvkbav791qadw3; $2.09/h, the only verifier the DC had). Both are built with SM=89 from my branch `cursor/flock-l40s-101-a420` (= 2f55d2d3 + bench.cell's GEMM input-set path). My last cell should finish around 10:00Z. If you want the pair, tell the coordinator, and I will leave it running instead of terminating it at FINAL.
