---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T06:13Z
---

# RunPod pod terminated (06:11Z, about $6.40); #483 final head 60549d3b with 720/720; #487 extended for the PINNED route; plan for your 05:57Z decisions

- **Pod `vy-sm120-tc-gemm-1`:** terminated at 06:11Z and unregistered. It was up 03:07–06:11Z, about 3.07 h at $2.09/h, so **about $6.40 of my $25** share.
  - Every run's pod-side custody verdict is `preserved: true`, and the VM-side `research data preserved` agreed for all except the 3.5 GB correspondence run, where its read-back was slow; that run's pod verdict was verified on R2 at 03:45Z.
  - `r20260930-030729-37ea` never ran (a bad `--timeout` argument) and recorded no attempt.
- **#483 final head `cursor/vllm-sm120-bias-epilogue-422d` @ `60549d3b`,** for your grant.
  - Acceptance run `r20260930-044225-355c`: circuit-check 3/3 bindings with 0 failures.
  - The registered row kernel against the GPU words of every captured M >= 2 bias case: **720/720 cases, 29,733,056/29,733,056 coordinates exact.**
  - M = 1 (the gemv) is 4/24, as expected.
  - The PR body carries the record.
- **#487** (`cursor/vllm-sm120-fp8-probe-422d` @ `8c2b4d4c`) adds:
  - **The probe fix** (`3669e3fb`): `tc_probe`'s fp8_floor_probe pool looked the declared model up in `S.PIPELINES`. The sm_120 models live only in `MODELS`, so every worker died in its initializer and the pool respawned them forever. That was the hour-long "hang" of the 25M sweep, not slowness.
  - **The `rtxpro6000` SKU-family row** in `research.env` and in `trust.py`'s copy (`8c2b4d4c`). Without it a PRO 6000 record has family `unknown`, and a PRO 6000-anchored Target can never match its evidence. The sm_120 instruction default (the 5090) is untouched.
  - The e4m3 model's 25,040,128-element fresh-seed result (0 mismatches, specials included; evaluated from the stopped sweep's tiles by `r20260930-052000-e32d`).
  - Mark it ready once the Target lands on it (next item).
- **Plan for your decisions, in your order:**
  - **(2) PINNED on the PRO 6000:** add a core Target `fp8-sm120-mma-draft` (pipeline `BLACKWELL_SM120_E4M3_M16N8K32`, anchor `NVIDIA RTX PRO 6000 Blackwell Server Edition`, instruction `sm120.mma.m16n8k32.e4m3`) with its family, digest and reference vectors, on #487. Then one `port-capture` job on vy-nebius-1 for the fresh e4m3 + e5m2 sweeps, which record the 2,100 MHz clock and the driver; then `trust.py --publish`.
  - **(1) `GemvBiasF32_v1`:** one `port-capture` job to re-measure (V, T) for the biased models' shapes in vy-nebius-1's cuBLAS, then the Definition, the table and the acceptance.
  - **(3) registry, then (4) fold,** as ordered.
- **Blocker to check:** this VM has neither `sky` nor `kubectl`. `submit.sh` installs the SkyPilot client through uv (which the VM also lacks), so the first submission may take some setup. I'll say so if it fails.
- **Acknowledged:** lane C's 05:03Z note. #481 adds `moe_expert_dot` to the `blackwell_consumer` TARGETS record, and #483 doesn't touch that record.
