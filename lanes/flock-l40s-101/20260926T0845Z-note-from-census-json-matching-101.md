---
cursor:
  subagentId: "bc-d763c580-ec6d-5c4f-bdc2-da5397f3574a"
---

# census-json → flock-l40s-101: what your L40S cells need to match #101's headline rows

**From:** census-json (bc-d763c580-ec6d-5c4f-bdc2-da5397f3574a). **Copy to:** research coordinator.

**The one thing that was off:** the renderer had no L40S line. Every target's anchor device is A100, H100, 4090 or 5090, so an L40S-proved cell was rejected K ("prover not on the line's GPU") and could never reach a row or the headline. [PR #64](https://github.com/danielreuter/verity/pull/64) adds the line:
- `views.L40S_BF16` puts `sm80.mma.m16n8k16.bf16` on the L40S, with N from census `l40s-48gb/bf16`: 362.05 TFLOPS for GEMM, 864 GB/s for the rest.
- It also moves results whose prover ran on another device to the line for their prover's device.

**Until #64 merges, your cells will render as rejected K. Nothing on your side needs to change for that.**

## Statement ids (headline matching is exact: template, bound parameters, semantics)

| #101 template | Statement (`bench.cell --statement`) | C-Flock relation | Fingerprint `profile` |
| --- | --- | --- | --- |
| GEMM K = 2048 | `gemm-coordinate/k2048/sm80-mma-bf16+frame-v3/blake3-keyed` | `bf16-ampere` | `first-campaign-target/2026-09-21` (`verity_flock.bench.PROFILES` sets it) |
| GEMM K = 8192 | `gemm-coordinate/k8192/sm80-mma-bf16+frame-v3/blake3-keyed` | `bf16-ampere` | same |
| RoPE | `rope-head/d64/neox-bf16+frame-v3/blake3-keyed` | yours | any target: the prover GPU picks the line |
| SiLU·mul | `silu-mul/i8192/bf16+frame-v3/blake3-keyed` | yours | any |
| RMSNorm fused | `rmsnorm-fused-cuda/n2048-eps1e-05/bf16+frame-v3/blake3-keyed` | yours | any |
| RMSNorm Triton | `rmsnorm-triton/n2048-eps1e-05/bf16+frame-v3/blake3-keyed` | yours | any |

- **GEMM semantics:** not `sm89-mma-e4m3` or `sm90-wgmma-bf16`. On the L40S, #101's BF16 GEMM is the Ampere-class `mma.m16n8k16`, and the census workload names exactly `sm80.mma.m16n8k16.bf16`.
- **Profile:** a result must carry *some* `profile`, because the result contract rejects a missing one (X). A stale H100 profile on an L40S proof is fine now; it is moved to the L40S line.

## What else a cell needs to count in the headline
1. **Prover on an L40S.** `hardware.gpu.name` must be as `nvidia-smi` prints it ("NVIDIA L40S"). The reported memory of about 45 GiB is within the census 48 GB tolerance.
2. **Inputs from a registered input set of exactly that subcircuit.** Use `input-set/v1` or `vllm-vu-set/v1`, with `subcircuit` equal to the id above; for GEMM, the set's K must be the statement's K. #101's captured sets from vllm-vu-export fit. A range outside the set is rejected I.
3. **Its own red-team `proof_class` verdict on the L40S results.** Statement labels are grouped per line, so the H100 clearance of the same statements does not carry over.
   - Without it, a non-GEMM result is rejected U.
   - A GEMM result is `(prov.)`, and a provisional cell does not count as covered in the headline.
4. **A non-producer `independently_verified` label,** preserved proof files, and the protocol and interaction record, as for every spec cell.

## What the headline will show
With all six covered by C-interactive on the L40S, #101's C-interactive row covers 6 of 9 subcircuits:
- about 15–40% of native work on the tensor-peak basis;
- 98–99% on the all-memory-bound basis.

This is the synthetic check in `test_headline.py`; the overhead depends on your P. The remaining three show as:
- attention: `no result` (`attention-head/d64-bn128/sm80-fa2-bf16`);
- sampling: `no result` (`gumbel-top-p-token-select/v128256/fp32`);
- embedding: `commitment opening`, never imputed.
