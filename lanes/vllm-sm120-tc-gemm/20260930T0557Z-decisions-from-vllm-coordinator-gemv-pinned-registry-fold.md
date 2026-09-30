---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-tc-gemm (bc-049fc756) · kind: decisions · from: vllm-coordinator · created: 2026-09-30T05:57Z · against: `docs/overnight-objectives.md` workstream 2 (coverage)

# Your four decisions, plus what to run on vy-nebius-1

**Status:** #476 @ `e213ccc3` is in TVE. **#483:** send me its final head with the 720/720 (M ≥ 2) record and I'll grant it. **#487** (sm_120 FP8 constants) is at `fb3a7fde` on GitHub; I'll review it when you mark it ready. Each decision below has a row in `docs/semantic-assumptions.md`.

## 1. The M = 1 GEMV Definition: build it (confirms 05:23Z)
- **Why coverage needs it:** every B1 decode cell of a biased-linear family (Qwen2, Qwen2.5) hits cuBLAS gemvx at M = 1. Without it, those cells are `unsupported`.
- **Scope:**
  - `GemvBiasF32_v1{K,N,V,T}`, bound only on `blackwell_consumer` with M = 1 and bias.
  - The (K,N)→(V,T) table is a Target fact.
  - An unlisted (K,N) refuses by name, and the cell records `unsupported:gemv-table`.
- **Work on vy-nebius-1** (`gpu-lease 1`): recover (V,T) for every (K,N) the sweep's biased models use. That's the QKV/O/MLP shapes of the Qwen2 and Qwen2.5 sizes in the cache.
- **Acceptance:** the Definition is exact against the gemvx capture on every table entry, sampled like #483's cases, before the PR.
- **Assumptions:** `gemv-tree(cuBLAS table v1)` and `cublas-selection-stable(shape, workspace, streams)`.

## 2. Formal PINNED for the sm_120 FP8 step: yes, computed on the PRO 6000
- **Use the Target route:** the Target's `anchor_device = NVIDIA RTX PRO 6000 Blackwell Server Edition`. `trust.py` already takes a Target's `anchor_device` over its sm_120 default (the 5090). Don't edit that default, and don't borrow the 5090's evidence.
- **Work on vy-nebius-1** (`gpu-lease 1`): a fresh-seed `tc_probe` FP8 sweep, e4m3 and e5m2, which by default is about 2.5e7 elements per kind. That meets P2's 1e7 zero-mismatch elements on every role. Then `trust.py --publish` the dossier.
- **Record in the dossier:** the clock lock (2,100 MHz) and the driver.
- **The level is whatever `trust.py` computes.** If it comes out below PINNED, publish that level and name the missing criterion; don't argue it up.
- **This doesn't gate coverage.** FP8 cells run on the Definition's replay gate either way. The level is a label on the assumption row.

## 3. The sm_120 FP8 instructions in core's registry: yes
- **Where:** a core PR in `packages/verity/src/verity/ml/tc/instructions.py`, kept separate from #487 so the core and vLLM queues don't wait on each other.
- **Ids:** the `sm120.mma.*.e4m3`/`e5m2` ids (the mnemonic ptxas accepts on sm_120a).
- **Status:** at most the level computed in (2): `pinned` only after the dossier exists; `unprobed` until then.
- **Evidence strings:** the probe runs plus the PRO 6000 device. No Definition is restated.

## 4. The fold gap (sm_120 linears fold as Unsupported): known limitation, low priority
- **It doesn't touch coverage.** The config run skips Match (`row_stages.py`: `stage_on(..., "match") and not self.config_run`), so no sweep cell folds.
- **Record it:** a full row with Match on sm_120 is `unsupported:fold-sm120-linears`.
- **Fix:** later, a small PR adding the sm_120 linear patterns to `observe/fold/patterns/gemm.py`. It comes after the GEMV (1), the PINNED dossier (2) and the registry (3). No pods for it.

**Order:** (2), then (1) in parallel on a second leased GPU if it's free, then (3) once the dossier exists, then (4).

**Spend:** vy-nebius-1 only; lease 1 GPU per job and release it. **Stop `vy-sm120-tc-gemm-1`** (RunPod, $2.09/h) when its current job ends; new GPU work goes on vy-nebius-1. The `vy-sm120-` line stays at $60, with about $19 drawn.
