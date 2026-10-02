---
id: red-team-proofs-806/20261002T1444Z-reply-from-red-team-proofs-806-vllm-peak-denominators
campaign: private-overheads-oct2
lane: red-team-proofs-806
kind: handoff
status: open
repo: verity
origin: red-team-proofs-806 (agent bc-7b6772b1-42d3-5a07-9701-82e182ea5921; started by proofs bc-8416bc72)
---

# red-team-proofs-806 → proofs: peak-normalized denominators, both vLLM rows: GRANT, GRANT

This lane id was earlier written `red-team-proofs-554` (the coordinator's ruling, 7:42 AM PDT). Past notes and labels keep
that id.

| row | matmul FLOPs | at 500 TFLOP/s | `--zk` prover s | peak-normalized | verdict |
|---|---|---|---|---|---|
| Llama-3.1-8B, attempt 13 | 1.6548475 × 10^13 | 33.097 ms | 1,309,794.57 | 39,574,478× | **GRANT** |
| Qwen3-30B-A3B-2507, step 6, opened model | 6.8866361 × 10^12 | 13.773 ms | 1,010,211.27 | 73,345,770× | **GRANT** |

Every figure reproduces from the unrounded prover seconds: 39,574,478.5 and 73,345,770.5. So do the phases:
- Llama prefill 39,147,930× and decode 42,715,419×;
- Qwen prefill 71,959,215× and decode 82,794,659×.

Each `--zk` record points at its row's breakdown (`rollup_art`, with a matching sha256):
- Llama: `r20261002-123349-4059` → `art:c343ae88…`.
- Qwen: `r20261002-105057-da28` → `art:5d019e2e…`, sha256 `55506e53…`.

The numerators are the ones granted before:
- Llama: `note:red-team-proofs-554/20261002T1436Z-reply-from-red-team-proofs-554-vllm-dense-zk-numerator`, with N1 still open
  there.
- Qwen: `note:proofs/20261002T1129Z-reply-from-red-team-proofs-554-vllm-moe-step6`, zkaudit of all 33 shapes,
  `r20261002-111936-8f31`.

## The FLOP count, three ways

1. **From the model configs and the run's shape, with no input from the worker.**
   - **Configs.** The public `config.json` files are `unsloth/Meta-Llama-3.1-8B` and
     `Qwen/Qwen3-30B-A3B-Instruct-2507`. The 2507 config equals the repo's pinned
     `engine/profiles/hf_configs/QWEN3_30B_A3B.config.json` in every matmul shape:
     - Llama: H 4096, I 14336, 32 layers, 32 heads, 8 KV heads, head dim 128, vocab 128256, untied;
     - Qwen: H 2048, moe I 768, 48 layers, 32 heads, 4 KV heads, head dim 128, 128 experts, top 8, every layer sparse, no
       shared expert, vocab 151936, untied.
   - **Run shape.** Batch 1, 1,024 prompt tokens and 128 generated: 1,151 positions pass through the layers (1,024 plus 127
     fed back), the LM head runs on 128 rows (the last prefill position and 127 decode steps), and the key counts are
     T = 1 … 1,151, causal.
   - **Rule.** 2 FLOP per multiply-add (the census's convention); attention counts QKᵀ + PV at 4·NH·D·T a layer-position.
   - **Llama** comes to 1.6548475e13: 1.6066e13 per-position GEMMs, 1.345e11 LM head and 3.476e11 attention. QKV, O,
     gate-up and down equal the lead's line items to the FLOP.
   - **Qwen** comes to 6.8866361e12. The experts are 441,984 routed Calls each way, 4.1711e12, which is 60.57% of the
     total.
2. **From each run's own Calls.**
   - **Qwen.** `counts-opened.json` (in `art:1ee42a7f…`) has 55,248 = 1,151 × 48 Calls of each per-position GEMM, 441,984
     of each expert GEMM, 128 of the LM head and 48 of each `Attention_v5{T}` for T = 1 … 1,151. They give 6.8866361e12.
   - **Llama.** I used the breakdown's units: 36,832 = 1,151 × 32 rows of each per-position GEMM, 128 LM-head rows, and
     1,151 `Attention_v5{T}` Definitions, none missing. Each Definition has 32 Calls, since its units are exactly 32/48 of
     Qwen's at the same T. They give 1.6548475e13.
3. **The leads.** Both leads state these same totals and line items.

**Nothing matmul is missed.** Each breakdown's other families are non-matmul: RMSNorm (Qwen's QK-norm included), SiluMul,
RoPE, MoeSum, the router top-k, the embedding gather, and the routing-weight multiply. The router logits GEMM is counted.
`TokenSelect` is excluded.

**The prefill/decode split is the prover seconds' own.** It follows each Definition's `prefill_fraction`: 1,024/1,151 of
a per-position Calls, 1/128 of the LM head, and attention with T ≤ 1,024 in prefill. My split from the configs gives the
same numbers:
- Llama: prefill 1.4569848e13, decode 1.9786273e12;
- Qwen: prefill 6.0053893e12, decode 8.8124686e11.

## The peak

`census/hardware.json` `rtx-pro-6000-server/bf16` (on main since `2b318553a`) is 500e12: dense, FP32 accumulate. It is the
right entry, for the chip both rows ran on (zkaudit `host.txt`: RTX PRO 6000 Blackwell Server Edition) and the dtype of
both rows' GEMMs (bf16).

## Findings (none blocking)

- **F1, peak, at most 6.4%, against the prover.** The 500 TFLOP/s is a datasheet figure, not measured. The census marks it
  "to be confirmed by a native-peak/v1 measurement".
  - **The clock-adjusted rate.** The census's own note gives 467.8 TFLOP/s at the 2,430 MHz maximum SM clock that
    nvidia-smi reports. That is the whitepaper's per-clock rate.
  - **Effect.** At that rate both overheads fall 6.4% (×0.9356), to 37.0 million× and 68.6 million×.
  - **Why it doesn't block.** 500 is Daniel's ruled datasheet peak, and it is the choice that reads higher.
- **F2, non-matmul work, about 0.1% (Llama) and 0.3% (Qwen).** This work is excluded, as both leads say, and the
  exclusion overstates the overhead. A rough bound: the non-matmul families' units at about 10 FLOP each, plus softmax at
  about 5 FLOP a score, come to about 1.7e10 FLOP for Llama (0.10%) and 1.9e10 for Qwen (0.28%).
- **F3, attention counted causal-exact, overstates the overhead by much less than 1%.** A BN = 64 tile kernel also
  computes the masked half of its diagonal tiles, and the count leaves that work out.

## Labels

- `grant=red-team` on `art:c343ae88d618f9b5ffc8699951fb2a7bf0e36f151a450a671305c88c7bee1996` (Llama).
- `grant=red-team` on `art:5d019e2e90b1d59aeae5908f4fc03d9aab72a9955552b2467295ba29676e8b24` (Qwen, opened).

Both are by `red-team-proofs-806`, with ref this note.
