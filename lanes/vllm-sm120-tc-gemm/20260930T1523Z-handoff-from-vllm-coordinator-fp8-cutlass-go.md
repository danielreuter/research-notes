---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-tc-gemm (bc-049fc756) · kind: GO · from: vllm-coordinator · created: 2026-09-30T15:23Z · Daniel's decision, 15:22Z

# GO: sm_120 FP8 runs with `VLLM_USE_DEEP_GEMM=0` (the CUTLASS block-scaled path). Capture it on the RTX PRO 6000, then queue the 7 FP8 cells on node 1

**Daniel said yes (15:22Z).** On sm_120, block-FP8 rows run with `VLLM_USE_DEEP_GEMM=0`, as the H100 panel pins. vLLM then routes to `CutlassFp8BlockScaledMMKernel` (CUTLASS's sm_120 blockwise path), with the non-packed `per_token_group_quant_fp8`. It's in the postmortem's workstream-2 table: "FP8 through CUTLASS: captures on the RTX PRO 6000, then 7 cells" (`docs/gpu-utilization-postmortem.md`).

**Do, in order:**
1. **The engine pin, scoped.** Set `VLLM_USE_DEEP_GEMM=0` for block-FP8 rows on `blackwell_consumer` only, the way the H100 panel's pin is set (`engine/env.py` or the target's record).
   - It must be recorded in the config record's engine facts.
   - It must not change any other target's environment or any existing digest.
   - This is the one engine-side change Daniel approved; nothing else.
2. **The capture** on the PRO 6000: one Kueue `port-capture` job, not in 12:30–13:30Z (it's past that now). With the pin on, capture a real FP8 checkpoint's (one of #469's pins) linears:
   - confirm vLLM selects `CutlassFp8BlockScaledMMKernel` and the non-packed quantizer (kernel names, plus SASS if cheap);
   - check exactness of the quantizer (`Fp8GroupQuant_v1`, now on the PRO 6000) and of the GEMM (`ScaledMmFp8Block_v1` with the sm_120 e4m3 step, the promotion schedule, and the scale order from the source), over enough coordinates and groups, special values included;
   - whatever differs gets a new version bound only on `blackwell_consumer`, with a replay row.
3. **The PRs:** small ones against main (the pin, then any Definition or binding changes), after #557 if they touch `targets.py`. Send me the heads with the capture's run id; I'll grant them.
4. **Queue the 7 FP8 cells** on node 1 from a pre-merge branch (main + your FP8 PRs + #557 if it helps), `config-run-split`, campaign `overnight-sep30`, labelled as they finish (`ov.ws coverage`, `ov.config`, `ov.gate`, `ov.note "pre-merge … @ <commit>; VLLM_USE_DEEP_GEMM=0"`).
   - Take the 7 from the sweep lane's FP8 cell list (vllm-epoch-run, bc-75fd4007), or from #469's pins × B1/B8.
   - Tell the sweep lane which ones you're running, so it doesn't double-submit.

**Parked:** #546 (the DeepGEMM packed quantizer, UE8M0) and the DeepGEMM `fp8_gemm_nt` Definition. This path uses neither. Leave #546 as a draft; it's the record if DeepGEMM is ever wanted.

**Order against your other work:** #557's acceptance and the manifest check (15:08Z) first, since they're nearly done. Then this.
