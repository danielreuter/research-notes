---
lane: flock-vllm-v1
kind: report
created: 2026-09-25T22:27Z
status: open
---

CHECKPOINT ff1c1e3f (23:16Z) [open] cell v1 (host witness) done: H100 fp8-hopper plateau 8192 VUs 1070 VU/s (6.0e8x), same-DC verifier US-MO-1 RTT 0.81 ms, loopback probe same run; r20260925-225837-3a94 / verifier r20260925-225822-649f. PR #41. WAITING device-witness cell r20260925-231324-903c (ver r20260925-231313-fddc) check after 23:45Z; agent bc-9713144f
CHECKPOINT 2f3849f2 (22:59Z) [open] tip 2f3849f2: GPU selftest 21/21 at 8 VUs on H100 (r20260925-225318-3959, EU-FR-1; no hairpin there, verifier pod terminated). Cell running US-MO-1: prover r20260925-225837-3a94 (vy-flock-vllm-v1-mo) vs verifier r20260925-225822-649f (vy-flock-vllm-v1-ver cpu3c-32)
CHECKPOINT bf07377d (22:45Z) [open] tip bf07377d: flock-vllm-block/v1 statement + flock-vllm-v1 bin; CPU selftest 21/21 at 8/64 VUs (fp8-hopper); next: Flock-CUDA host-witness mode (SHA-256 slots), GPU selftest on H100
CHECKPOINT 48045063 (22:27Z) [open] started; branch cursor/flock-vllm-v1-4cdd from flock-gpu-link 48045063; agent bc-9713144f; reading vllm-v1 scheme + b-ligero-vllm-v1 + flock-pure-block
