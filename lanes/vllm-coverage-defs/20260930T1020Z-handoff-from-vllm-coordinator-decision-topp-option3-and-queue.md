---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coverage-defs (bc-ea0126bf) · kind: decision · from: vllm-coordinator · created: 2026-09-30T10:20Z · re: your 09:31Z finding

# Top-p: option 3 for tonight's coverage; option 1 goes to Daniel. Drop `_v3`. Your queue after that

**Decision: option 3.** Raise the sampler's gate limit per row with the existing `VERITY_QWORD_MAX_GATES=GumbelTopPTokenSelect_v2=<n>` machinery, and run the word check on vy-nebius-1's big-memory CPU.
- **Why:** no code, no digest move, no new query version. The gate as defined is met: the strict word check passes, the commitment is made, and 460 units replay bit-exact.
- **The cost is stated, not hidden:** the sampler Call stays one unit, not provable in practice, as it already is below the threshold. Every such cell's `ov.note` says `sampler Call one unit (MAX_GATES raised to <n>); not provable in practice`.
- **Option 1** (root-level sampler pieces, committing the top-p kernel's interior values) is the real fix. It changes what serving commits, so it goes to Daniel as a proposal; don't start it. **Option 2** (Q_word v2): no.
- **Drop the `_v3` item.**

**Do now:**
1. **The evidence run:** the Llama-3.2-1B rtxpro6000 top-p Build + word check on vy-nebius-1, CPU direct (`CUDA_VISIBLE_DEVICES=`), with `n` just above the measured need. Also the Gumbel row, which is the same select at `top_p=1`. Record the peak RSS and the value of `n` used, and label them as `ov.ws build` points (keys: `ov.metric peak-rss`, `ov.value`, `ov.unit GiB`, `ov.config <row slug>`, `ov.line topp-maxgates`, `ov.attempt 0`, `ov.phase prefill`).
2. **The formula:** write the `n` that fits each cached vocabulary (32k, 49k, 50k, 128k, 152k, 256k) from your gates-per-V measurement, with about 10% margin, and the expected RSS for each. Hand that table to the sweep lane (`lanes/vllm-epoch-run/`) so it sets the variable per cell and requests matching memory.

**Then, in order:**
1. **Pythia `LayerNorm_v1`** (in progress).
2. **`SiluMul_v2`**, from the red team's 09:30Z handoff (`lanes/vllm-coordinator/20260930T0930Z-handoff-from-red-team-vllm-semantics-silu-rope-edges.md`, labels on `r20260930-092038-7dbc`). Model the kernel at our pin exactly: `ACT(gate) * ((float)up + 0.0f)`, so `up = −0` enters as +0; gate −inf gives NaN; the NaN word is `0x7FFF`; and the gates below −88.7 and gate −0 behave as measured.
   - This matters for coverage, not just the edges: any real `up = −0` word would fail a replay.
   - Make it a new version, and don't rebind existing records' `_v1`. Check against the red team's reproducers plus a capture.
3. **FA2 softcap** (Gemma-2), as in my 09:26Z note.
4. **Only then, `RoPE_v2`'s hi contraction** (`fma(x, s, RN(y*c))` on sm_120), low priority: 0 of 6.3M words differ with a real cos/sin cache. First check on source whether the contraction is per-architecture.
