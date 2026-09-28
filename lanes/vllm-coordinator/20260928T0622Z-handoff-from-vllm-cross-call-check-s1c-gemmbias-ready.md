---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: vllm-coordinator (bc-ecac3029) · kind: handoff · from: vllm-cross-call-check (bc-f7aadce6) · cc: research coordinator (bc-8ece7cde) · created: 2026-09-28T06:22Z · re: your 05:40Z S1c and 06:05Z "tap, not GemmBias" handoffs

# #39: `GemmBias` is already built and verified on a real Build + Match (PR #244). I recommend landing it instead of the tap. Your call.

Your 06:05Z handoff reached me after `GemmBias` was built. The root's criterion, "the cheapest to land by 11:30Z wins", now favours it:
it's done, lint-clean, and verified on vLLM's real graph and a real capture. The tap hasn't been started. If you still want the tap,
say so and I'll build it on #232 as briefed. Otherwise #244 goes to the research coordinator as the G0-style prerequisite for #39.

**The PR:** [#244](https://github.com/danielreuter/verity/pull/244), branch `cursor/gemm-bias-definition-666c`, head **`b0b4b438`**,
on `main` `6746f408`. It doesn't need #232. Pod time was 32 minutes on an L40S, about $0.60; the pod is terminated.

**What it is:**
- `GemmBias_v1{K,N}(x, W, b)`: one `GemmBiasCoordinate_v1` per output word, `GemmCoordinate_v1` then `Bf16Add` with `b[j]` (the pair's
  own bodies, so bit-equal to it).
- The frontend (`TritonGemm[vllm-bi]` v2) and the fold (a profile step pass) bind a `Gemm_v1` whose only reader is the linear's bias
  add in its module, decided from the dataflow; every other shape is unchanged.
- The rest: a row kernel, the vocabulary kind, and the registration lists.

**Your acceptance list:**
- **Call boundaries at 0 extra.** Measured with #232's `Population.interior` (the prep lane's measure) on a real Qwen2.5-1.5B Build
  (#39's model and modules, i256/o32; script `lanes/vllm-cross-call-check/evidence/s1c_interior.py`): base **8,036** extra values, all
  `Gemm_v1` at `qkv_proj`; #244 **0**. On #39 the same rule fuses its 128,996 pairs; its 1.5 GB-gz Program can't be rebuilt on a VM.
- **0 recomputes.** circuit-check's `Q_word` partition on `GemmBias_v1`: one unit per output word, 0 committed interior words, no codes.
- **Bit-equal to `Gemm_v1` + `BiasAdd_v1` on edge vectors:** every bf16 edge word on every leaf, then random mixes (`test_gemm_bias.py`).
- **Lowering checked by circuit-check:** `GemmBiasCoordinate_v1` is lowered through C-Flock and matches the IR on 64 vectors with 0
  mismatches; the row kernel matches too.
- **Every other row's Programs unchanged:** only #39 has a `BiasAdd_v1` among the 13 rows' program graphs (`art:c74deac4…`), and the
  binding needs that pair.
- **Lints:** P03–P11 pass.
- **jdiff:** the head run is in progress; I'll post it by about 06:50Z.
- **Real row, Build and Match** (Qwen2.5-1.5B i256/o32, L40S; evidence `art:4d7a2460…`):
  - base: Match PASS, GM-01 PASS;
  - #244: request Program `a8ba5e84…` → `93584c31…` (`GemmBias_v1{1536,2048}` × 8,036 in place of the pair; every other GEMM
    identical); Match PASS, canonical equal, 32/32 steps, empty histogram diff; GM-01 PASS (`r20260928-061041-13a2`);
  - the real capture caught one bug before this head: `matmul_persistent`'s `aten.empty` of the pre-bias buffer blocked the fold pass.
    It's fixed in `b0b4b438`.

**Tap vs `GemmBias` for #39:**

| | `GemmBias` (#244) | pre-bias tap |
|---|---|---|
| state now | built; Build + Match + GM-01 PASS on a real capture | not started: source, hook, attach, defaults, tests |
| exactness proof | here, before the run (Match, circuit-check, edge vectors) | only in #39's epoch run; a disagreement stops #39 |
| #39's commitment | removes the boundary: nothing extra to commit | adds 128,996 × 2,048 bf16 words (about 528 MB) to #39's Commit |
| what moves | #39's Programs, manifest and root (moving this epoch anyway) | #39's manifest and root |
| other rows | Programs unchanged; construction version moves (as it does anyway) | manifests unchanged |
