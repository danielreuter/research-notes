---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-epoch-prep · kind: handoff · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-28T05:25Z

# S1/S2 up as draft PRs #232/#233; the Call-boundary gap is exactly #57, #74 and #39 (others clean)

**PRs** (drafts, CPU-tested, not merge-ready until the jdiff and S3/S4 land):
- [#233](https://github.com/danielreuter/verity/pull/233) S2, `cursor/epoch-s2-source-ids-150d` @ `c0db84e1`: Program ids name the wrapper's declared, versioned source (`DERIVE_SOURCE`, e.g. `verity-vllm/engine-step/v1`), not its module path.
- [#232](https://github.com/danielreuter/verity/pull/232) S1, `cursor/epoch-s1-q-word-record-150d` @ `4e6ce10f`: Q_word v1 as the partition of record. It covers the population, the header with the `verity/partition/v1` object and digest, the strict word check by default, the Commit's partition check, and the binding-map entry. Roots don't bind the partition digest (E6, out of scope).

**The row map for today's 0448Z finding.** "Extra" counts the Values Q_word requires that the module-body population doesn't commit. Each row is measured on its stored Build or programs artifact, smallest request Program. Evidence: notes `lanes/vllm-epoch-prep/evidence/s1_*`.

| Rows | Extra | Why |
|---|---|---|
| #23, #60, #67, #68, #70, #75, #73 (both FA3 constructions), #101 (known) | **0** | fused kernels. The MoE experts' interiors are already committed as `moe_block_stream` planes, and S1 counts them that way (fixed in `4e6ce10f`) |
| #57 | 62,330 (unset), 56,870 (`once`) | Gemma's ATen norm chain |
| #74 | 21,312 | `Fp8GroupQuant` x_q / x_s, read by the FP8 GEMM inside each linear |
| #39 | not measurable here (single 1.5 GB Program) | Qwen2.5's biased `qkv_proj` derives as `Gemm_v1` → `BiasAdd_v1` in one module (MAN-07), so the pre-bias output is a Call boundary |
| #4, #11 | not measured (no stored Program, or too big) | same structure as #23 and #101 (Llama); expected 0 |

**Consequence for the GPU run:** under S1, #57, #74 and #39 fail at Commit, because their `call_boundaries` identities have no source.
- #39 is GREEN; #74 is GREEN.
- The pre-bias Gemm output can't be recovered on the host: bf16 addition isn't invertible. So #39 needs a tap, or `Gemm_v1` + `BiasAdd_v1` restated as one Definition (the add inside each coordinate unit).
- #74's x_q / x_s are shared by every output coordinate, so they are committed words either way. The host can compute them exactly from the committed bf16 input (quant is deterministic), the `scale_products` pattern.
- #57: a host-evaluated chain, or one Definition.

**Asks:**
1. Which fix per row: host source, restated Definition, or defer. My order: #74 host source, #39 restated `GemmBias`, #57 host chain. Each is its own PR and CPU-testable; none is ready by 08:00Z.
2. Meanwhile, plan the GPU wave on the 10 clean rows, and hold #57, #74 and #39.
