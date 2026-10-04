---
id: 20261004T2202Z-report-relay-docs-pous-vllm-integration
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/pous-vllm-integration.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/pous-vllm-integration.md`, sha256 `12e3b20d03f56855eb9acaf576119c77d6c37624a111618d3c3980ef04b8c8a6`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# POUS in Verity's vLLM integration: scoping

27 Sep 2026, revised 15:20Z. Builds on the prior porep-inference code ("prior", under `internal/sources/porep-inference/`) and the [prior GPU notes](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/prior-gpu-notes.md) §3–4 and §6. Also read: Verity `origin/main` `5a7061c0`, vLLM at the pin `d9105ea80`, and the [P3 scheme](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/p3-scheme.md). **†** = inferred, not seen in code or run. The prior's tests were not in the export.

## 1. Insertion points: start from `vllm_porep`

**What the prior plugin does** (`vllm_porep/quant.py`, vLLM 0.28):

- A `vllm.general_plugins` entry point registers `"porep"` in every process, for every `LinearBase` and for `ParallelLMHead`.
- `create_weights` makes a plain bf16 parameter, so stock loaders do the TP slicing and the qkv / gate_up merges.
- `process_weights_after_loading` encodes on the GPU and replaces `layer.weight` with the uint8 buffer.
- `apply` is one opaque custom op (`direct_register_custom_op` + fake implementation), a leaf for `torch.compile` and CUDA graphs.
- Scratch is sized at load time. M ≤ 128 runs the fused decode→WGMMA kernel; larger M decodes, then calls `F.linear`.

Every vLLM API it imports exists at Verity's pin (checked statically). **Keep this skeleton, renamed `pous`:** it is the insertion point I proposed, already built and measured.

**What must change for Verity:**

- **One GEMM function for all M.** The prior switches kernels at M = 128, so a token's output bits depend on the batch size. The unfused path should call what `UnquantizedLinearMethod.apply` calls under `VLLM_BATCH_INVARIANT=1` (`linear_batch_invariant`), not `F.linear`.
- **A deterministic fused kernel.** `porep_fused.cu` reduces split-K partials with `atomicAdd(float2)`, so the sum order follows arrival†. It is therefore neither bit-identical to plaintext (the prior measured "near-identical") nor, I infer, repeatable run to run.
  - Verity needs a fixed-order reduction plus a new GEMM Definition, which must pass `circuit-check`. The prior's `sched=1` mode (nt-major, M ≤ 64) may already be one when a CTA owns a whole n-tile†.
  - Until then, Verity rows use the unfused path.
- **Hopper only.** The prior needs capability 90 and sm_90a WGMMA, so the integration's sm89 profiles get only the unfused path.

**What must change for P3: the decoder core.** The prior is a 4-layer DRG over 32-byte nodes, where one 64 KB block is one 64×512 bf16 tile. P3 is 2 layers of 220 × 1 KiB labels (band graph with 12 parents, full-width P⁻¹, transpose), and its decode unit is the whole 220 KiB segment†. The prior's two 65 KB stages plus a 64 KB X slab already fill most of the 227 KB of SMEM, so a P3 segment does not fit in one CTA beside the GEMM. The options are a thread-block cluster with distributed SMEM, decode → scratch → GEMM, or a smaller segment (for the scheme and `pous-gpu` lanes).

**Encoding.** The prior encodes on the server at load time. Keeping that for P3 is simplest, because the stock loaders, TP handling and merges come for free. It is sound only if the verifier computes `vk` (the per-block tags) itself from W and the salt, which P3 permits since it has no trapdoor†; the scheme owners must confirm. The alternative is an offline trusted encoder that writes a checkpoint per TP layout.

## 2. Audit path

**What the prior measured** (H100, under a harness load, not under vLLM):

| Placement | p99.9 excess | Verdict |
|---|---|---|
| Challenger in-process, on its own highest-priority stream, serving kernels with bounded CTA lifetime | 0.11–0.34 ms | passes |
| Challenger in a separate process | 2.45 ms (GPU time slicing) | fails |
| Persistent-grid serving kernels | 1.8–2.4 ms | fails |

**What that means for POUS:**

- **Challenger placement.** The challenger lives in each vLLM worker process, installed through `worker_extension_cls` (the integration's existing seam). A host thread polls a mailbox in pinned, device-mapped host memory and launches the bounded gather kernel (`audit_kernels.cu`) on its own stream. The kernel writes raw blocks into mapped host memory, and M checks them against keyed BLAKE2b-128 tags.
- **Withdrawn from my earlier draft:** the separate-process / IPC responder, the persistent responder, and `pause_generation` audit windows (a pause is a "prepare signal", which the prior's rules forbid).
- **Every serving kernel needs a bounded CTA lifetime.**
  - Verity's batch-invariant `matmul_kernel_persistent` is a persistent grid (`min(NUM_SMS, tiles)` programs). It needs a bounded variant with grid = ⌈tiles/bpc⌉. The per-tile K loop is untouched, so the bits and `Gemm_v1` should stay the same†.
  - The POUS kernels take the prior's `bpc` / `auto4` knobs, which cost +1.0–1.2% step time.
  - Attention and every other kernel should be checked with the integration's kernel census.
- **Deadline gap, a decision for Daniel and Track C.** P3 §2a assumes Δ = 5 µs (k = 423 in about 2.1 ms).
  - The prior's per-answer probe (one 4 KB read from HBM to pinned host memory, an RDMA proxy) measured p50 10 µs and p99.9 73 µs under HBM load, max 266 µs. A strict all-on-time policy needs Δ ≳ 300 µs.
  - The prior's raw-block audit revealed all indices at once (k = 207, 1 ms per round). So honest completeness at 5 µs is not demonstrated.
  - Options: raise Δ, which raises D far beyond the band certificate's d ≤ 10–14†; NIC-initiated GPUDirect RDMA reads, which use no SMs (unmeasured†); or hash-chained reveal on the GPU, which is unmeasured (about 1.7 µs per hop) and pools the deadline, which the per-answer theorem may not cover†.

**What vLLM must expose:** challenger install and close per rank; the block map (block → parameter, offset) after encoding; residency (sleep mode off, no reload, `weight_transfer` or re-layout without re-registering); and bounded-CTA kernels as an engine-profile setting.

## 3. Fit with Verity's integration

The integration reaches ranks through `worker_extension_cls` + `collective_rpc`, observes through forward hooks and a `TorchDispatchMode`, and has one patch owner (`engine/hooks.py`). The FP8 row is the precedent for weights derived at load time.

**Constraints:** `protocols/pous` is stdlib + `verity` only (reference Enc/Dec, verifier), so all torch, CUDA and vLLM code goes in `verity_vllm`. Challenges come from `verity.randomness`. New Definitions pass `circuit-check`, and merges go through `check` + `research merge`. Lints P8 and P10 apply.

**Decision (recommended†): treat decode as input provenance, not as a Program Call.** The Program keeps W and the served root is C. The weights of record pin the checkpoint W, plus Dec(pp, C) = composed W or Enc(W, salt) = C.

**Coordinate with the vLLM coordinator:**

1. an "encoded weight" root class in the PROTECTED `root_policy.py` (gate G3), and the pin and decode rule in `weights_of_record`;
2. fold patterns, the kernel census and allowlist, `code_identity`, and the opaque op in the observer's `REENTER_OPS`, without which Match cannot see the decode or GEMM inside it;
3. the serving rows' GEMM `w` table (#119), which must read decoded W;
4. an opt-in `TargetProfile` and a `quantization="pous"` profile (`verity_vllm.LLM` rejects the prior's `hf_overrides`), the plugin entry point, and the bounded batch-invariant GEMM.

The coordinator's recent work is all opt-in and digest-neutral; POUS should be too.

## 4. What carries over from the prior code

| Component | Carries over | Changes for POUS / Verity |
|---|---|---|
| `vllm_porep/` plugin | entry point, quantization config and linear method, stock-loader path, encode-at-load, opaque custom op + fake impl, scratch sized at load, `lm_head` | P3 codec; one GEMM for all M; `linear_batch_invariant`; `REENTER_OPS` |
| `porep_fused.cu` | tile-major encoded layout equal to the WGMMA SW128 SMEM layout (TMA-loaded, decoded in place), warp specialization, 2 stages, bf16 + bias epilogue, `bpc` | P3 decode core; a segment larger than SMEM; deterministic split-K; a Verity Definition |
| `porep/reference.py` + KATs | the pattern of a numpy twin checked against pinned vectors | P3 reference in `protocols/pous`, stdlib only |
| RBA harness (`research/trusted4/audit/`) | mailbox, bounded gather kernel, priority streams, BLAKE2b tags, false-reject and attacker harness, device clock | per-answer deadline; runs inside the vLLM worker |
| `porep/challenge/` S-W MAC, methodology (§6) | the bulk bandwidth audit, needed once locality is relaxed; same-run baselines, device clock, SASS checks | not needed under perfect isolation |

## 5. Staged plan

| Stage | Deliverable | Test (pass criterion) |
|---|---|---|
| 1. CPU reference | `protocols/pous` Enc/Dec, block map, verifier; numpy twin in `verity_vllm` | Dec(Enc(W)) = W bit-exact for random, all-zero and repeated-segment W; pinned vectors; twin = reference; SmolLM2-135M round trip |
| 2. Decode, then GEMM | `vllm_porep` ported to `pous`: a bounded P3 decode kernel into scratch, then `linear_batch_invariant` for all M | Decoded scratch bit-exact against the twin on every segment; then logits and tokens bit-identical to plaintext, since this path is exact; the Verity row passes with the plaintext Program digest; cost against a same-run baseline |
| 3. Fused | P3 decode in `porep_fused.cu`'s scaffolding (a cluster for the segment), deterministic split-K | Exactness on decoded weights, not logits: identity slices of X through the production kernel return W exactly under any accumulation order (one nonzero product per output†), compared with the twin; repeated runs bit-equal; a new GEMM Definition passes `circuit-check` and replay; cost against the 2× line |
| 4. Audit | the RBA harness as a worker extension; a bounded batch-invariant GEMM | Under live vLLM serving: 0 late in 30,000 rounds at the chosen Δ on the device clock; attackers (blocks in host DRAM, blocks regenerated from W) fail; serving bits unchanged; step cost ≤ about 1.2% |
