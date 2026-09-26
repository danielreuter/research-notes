---
cursor:
  subagentId: "bc-231b1a72-2c21-58bc-b207-c9ee2ac71772"
lane: coordinator
kind: handoff
from: sp1-evaluator (bc-231b1a72)
created: 2026-09-26T02:50Z
---

# sp1-evaluator: first non-GEMM proofs done (RMSNorm fused + Triton, RoPE), GEMM through the same path; merge-ready

**To:** research coordinator (bc-8ece7cde). Branch `lane/sp1-evaluator`, tip in the FINAL checkpoint.

## What was proved

The approved SP1 guest, unchanged (ELF `cef2b78a…`, vk `0x007d9347…`, reproduced on the pod), re-runs the IR evaluator's own gate list for a #101 subcircuit and compares it with the committed outputs.

- **Gate list:** `verity.evaluation.reference.standalone_call(spec)`, the gates `evaluate()` walks, one guest gate per IR primitive.
- **Inputs:** from #101's export `art:b5bb0ca9` (PR #42).
- **Commitment:** every boundary word is committed and opened under `verity-vllm/leaf/v1`: the inputs root, the outputs root, a constants root, and the MUFU table roots. The format-3 statement and packed witness are `typed-obligation/v0`.
- **Public values:** `h_O || h_L || 01`, checked by `verify_object` under the APPROVED key.
- **Pipeline:** `prepare` (recorded run on the VM, needs `verity_vllm`) re-runs the IR oracle and requires the recorded outputs. It then lowers the instances, requires the Python reference to accept, and builds 3 negatives. `run` (the pod) executes the honest bundle and the negatives, then proves core and compressed.
- **Negatives:** a wrong first output word, a wrong last output word, and a tampered output leaf. The guest rejected all 3 in every run, and so did the Python reference.

RTX 4090 (`vy-sp1-evaluator`), core proofs unless noted. "Verify" is the in-process verifier. A fresh `verify` process adds about 15 s of key setup, and every prove adds about 13–15 s of `fixed.setup_seconds`.

| Template (#101 set) | B | Run | Cycles | Core prove | Per instance | Shards | Proof | Verify | Soundness | Compressed prove / verify |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| RMSNormFusedCuda_v2 N=2048 (15,362 gates) | 1 | r20260926-020127-276d | 33.5M | 5.73 s | 5.73 s | 8 | 12.0 MB | 0.46 s | 2^-97.0 | 7.69 s, 1.27 MB / 0.07 s |
| same | 8 | r20260926-020407-72ea | 108.1M | 14.53 s | 1.82 s | 24 | 36.1 MB | 1.34 s | 2^-95.4 | 18.32 s / 0.07 s |
| same | 32 | r20260926-020747-8318 | 364.5M | 43.84 s | 1.37 s (marginal 1.22) | 77 | 116 MB | 4.31 s | 2^-93.7 | 56.87 s / 0.05 s |
| RMSNormTriton_v1 N=2048 (13,582 gates) | 1 | r20260926-022135-44cd | 29.4M | 5.21 s | 5.21 s | 7 | 10.5 MB | 0.41 s | 2^-97.2 | 6.93 s / 0.06 s |
| same | 32 | r20260926-022415-0528 | 313.2M | 35.24 s | 1.10 s (marginal 0.97) | 62 | 93.8 MB | 3.60 s | 2^-94.0 | 46.42 s / 0.04 s |
| RoPE head D=64 (64 gates) | 1 | r20260926-023353-4da0 | 0.42M | 0.80 s | 0.80 s | 2 | 2.8 MB | 0.12 s | 2^-99.0 | 1.57 s / 0.06 s |
| same, the whole set | 1024 | r20260926-022907-c2c3 | 210.1M | 28.82 s | 28 ms | 49 | 74.2 MB | 2.97 s | 2^-94.4 | 41.20 s / 0.07 s |
| GemmCoordinate K=2048 (129 gates) | 64 | r20260926-023829-49aa | 72.8M | 12.63 s | 0.197 s | 19 | 28.6 MB | 1.05 s | 2^-95.8 | 15.86 s / 0.05 s |
| GemmCoordinate K=8192 (513 gates) | 16 | r20260926-024138-fa0c | 70.8M | 12.61 s | 0.788 s | 19 | 28.6 MB | 1.07 s | 2^-95.8 | 15.69 s / 0.07 s |

**Notes on the table:**
- **Soundness** is SP1's own accounting: 100 bits per STARK proof, union-bounded over the core shards. The compressed proof is 2^-100. All of it is below the tables' 2^-128.
- **Batching:** at B=1 the RMSNorm guest spends 55% of its cycles parsing the statement (the 15k-gate body, once per statement). At B=32 the gate relation is 82% of cycles, about 600 cycles per soft-float FP32 gate.
- **Result artifacts** (`bench-result/v1`, PRESERVED), in table order: `art:f1d4da61`, `art:dc494b62`, `art:47a673f7`, `art:19a4fdb3`, `art:095d5306`, `art:56fa0faf`, `art:34bb8329`, `art:fd92bd86`, `art:a38566af`. Proofs are in each run's `run_files`.
- **Labels:** each run carries 15 labels by `sp1-evaluator`: `candidate=SP1`, `proof_class=NON_ZK_PROOF`, `authentication=included`, `B`, `relation`, `soundness`, `seconds_per_vu`, `instances_dataset` = set art, `campaign=vllm-coverage`, and so on. A `note` label names the prepare run it came from (`--ref`).
- **Prepare runs:** r20260926-021431-b737, -021447-0aea, -021508-c25f (fused, B=1/8/32), -021548-d751, -021607-5ffd (Triton), -021638-e31f, -021646-8547 (RoPE), -023728-40bc (K=2048 B=64), -023802-cef8 (K=8192 B=16).
- **Fused bundles:** the three fused proofs used exploratory bundles. The recorded prepare reproduces their object digest and statement sha256 exactly, and a label on each run says so.

## What it would take to cover every #101 template, and the overhead

These are exhaustive-coverage estimates for #101 on a 4090, core proofs. GEMM, RMSNorm and RoPE rates are measured; the rest are estimated from the measured cycle rates.
- **Hardware bases:** the prover is a 4090 and the native hardware is L40S.
- **Native denominators:** GEMM uses the BF16 tensor peak of 362 TFLOPS, the Table 2 convention. The other templates use their HBM traffic at 864 GB/s, because no per-family work model is agreed.

| Template | #101 instances | SP1 per instance | SP1 total | Overhead vs native | What it takes |
| --- | ---: | --- | ---: | ---: | --- |
| GEMM K=2048 (qkv, o, gate_up, lm_head) | 102.85M coords | 0.197 s (measured) | 20.3M s | 1.7e10× | Nothing new: run the sets. Deduplicating the shared x row per token-row saves about 25–30% of cycles (merkle 31%, parse 15%). |
| GEMM K=8192 (down) | 9.40M coords | 0.788 s (measured) | 7.4M s | 1.7e10× | Same. |
| Attention FA2 head D=64 | 146,944 heads (mean T≈144) | ≈0.95 s (estimate) | 0.14M s | ≈2e7× | **Guest change.** No single guest family has `tc_dot16`, the FTZ gates and `f2fp_bf16` together. Needs a combined family (new ELF and vk, approval), a Python mirror of `ftz.rs`, and ex2/rcp tables. The alternative is chaining per-family statements through committed intermediates. |
| RMSNormFusedCuda_v2 | 9,184 rows | 1.22 s (measured) | 11.2k s | 5.1e7× | Done. |
| RMSNormTriton_v1 | 287 rows | 0.97 s (measured) | 0.3k s | 6.8e7× | Done. |
| RoPE | 183,680 heads | 27 ms (measured) | 5.0k s | 6.2e7× | Done. |
| SiluMul I=8192 | 4,592 rows | ≈1.2 s (estimate) | 5.5k s | ≈2e7× | No guest change. Promote `veritor.elem-bf16@1` to Python (its SiLU table plus a digest pin), then add a `FAMILIES` entry and a binding. |
| GumbelTopP V=128256 | 32 | ≈190 s (estimate; 2.18M gates) | 6.1k s | n/a | **Guest change.** New gates are needed: Philox plus libdevice `logf` noise lanes, V-wide bit/mask gates, `F32GtStrict`, `SelectF32`, `F32Eq`. |
| Embedding_v1 | 287 | — | — | — | A commitment opening, not a subcircuit. |

- **Total, exhaustive:** about 27.8M GPU-seconds, roughly 7,700 4090-hours or $5.7k. GEMM is 99.4% of it.
  - **Work-weighted overhead:** about 3.3e9× (27.8M s of proving against about 8.5 ms of native work).
  - **Sampled coverage:** at the protocol's 1,374 of 46,558 VUs (2.95%), about 230 GPU-hours, roughly $170.
- **With the specialized `relation-bare` guest for GEMM** (sp1-table `art:7233a6a3`: 33k cycles per K=1536 VU, but authentication excluded and a separate ELF): about 280 GPU-hours exhaustive, roughly $210, or about $6 sampled, and about 1.2e8× work-weighted.
- **Main lever inside this path:** the soft-float FP32 gate cost, about 600 rv32 cycles per gate. Only a precompile removes it, and that changes SP1 itself.

## Merge-ready (branch `lane/sp1-evaluator`, base `main` 541d31d3)

- `verity.proofs.reduce_mufu` promotes `veritor.reduce-mufu@1` to Python. It is an integer-exact transcription of `reduce.rs`, with its digest pinned at `a348a7bb…` (the Rust test's value). It is registered in `family_gate_set` and `SUPPORTED_FAMILIES`.
- `verity.evaluation.reference.standalone_call` is now public; this is a rename of `_standalone_call`.
- `verity_sp1.ir_call.lower_call(spec, instances, tables=, family=)` covers `reduce-mufu@1` and `tc-ampere-bf16@2`; in the tensor-core family, a zero-accumulator step lowers to `tc_dot16_0`.
- `benchmarks/ir_call/sp1_ir_call.py` provides `prepare` and `run`.
- **Tests:**
  - New: `packages/verity/tests/proofs/test_reduce_mufu.py` (digest, IEEE agreement, exact FMA, table-row rejection) and `backends/sp1/tests/test_ir_call.py`. Both pass.
  - The core, SP1 and protocols suites pass, except three failures that also occur on `main`:
    - `test_every_registered_kernel_is_self_checked_here`;
    - `test_repository` size caps, from `backends/ligero-verify/DISCREPANCIES.md` at 49 KB;
    - `test_repository` blob limits, from three `ligero-verify` proof fixtures over 5 MB.
- No Rust changes and no change to the ELF or verifying key.

## Open items for you

1. **Discrepancy without a home.** On two NaN operands, the guest's `f32_add`/`f32_mul` return the first operand quieted (Rust `reduce.rs`, and so the Python mirror). The IR primitives (numpy on x86) return the second.
   - None of the three templates can see this: every NaN path ends in `rsqrt_approx`, `f2fp_bf16` or bf16 canonicalization.
   - A subcircuit that outputs raw f32 words would see it.
   - `fixtures/discrepancy_log.json` only admits tensor-core targets and instructions, so I didn't log it. It needs an owner.
2. **Table admission, which needs Daniel.** Captured sets, a non-GEMM work model, an L40S class, and SP1's 2^-94…2^-100 against 2^-128.
3. **Independent verification.** Every proof is preserved in `run_files` for a verify lane to replay.
4. **Authentication scope.** The inputs and outputs roots are over the exported words, not #101's own commitment tree: the export keeps the replay's openings but not their paths.

**Pods and spend:** `vy-sp1-evaluator` (4090, $0.74/h), 01:41–02:46Z, drained and terminated. About $0.80 of the $20 budget.
