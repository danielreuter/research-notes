---
id: 20261001T0915Z-report-from-vllm-config-run-tp2-p081-moe-gap-fixed
campaign: overnight-sep30
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: vllm-config-run-tp2 (bc-35ab914e), follows note:20261001T0810Z-report-from-vllm-config-run-tp2-p051-staging-fix-pass
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---

# @circuits: the Qwen3-30B-A3B TP2 gap (p081) is fixed and proven; its cause wasn't the MoE path

**Branch:** `cursor/tp2-gaps-3847` @ **`bf14650c8`** (the staging fix `d6d1e2aa1` plus this one; no PR).

**The cause:**
- vLLM's `Qwen3MoeSparseMoeBlock.forward` calls `tensor_model_parallel_all_gather` only under `if self.is_sequence_parallel:`.
- The TP partial source's static site finder (`collective_sites.mid_module_sites`) counted collective calls in the class source with a regex, so every `model.layers.N.mlp` became a mid-module site expecting one gather per step.
- Sequence parallelism is off, so 0 arrived. The identity check failed with `missing_modules … mlp`, `tp_sites_bad {…: 0}`, and 485 expected modules against TP1's 437 (exactly the 48 blocks).
- The committed bytes were right all along: the fixed run's root equals the failing one's.

**The fix:**
- `guarded_collective_calls` parses the class with `ast` and records the `self.<attr>` guards of each call (`if` body, and the `else` of `if not`).
- `mid_module_sites` counts only the calls whose guards hold on the module instance.
- A guard that isn't a plain attribute keeps the call, so OLMoE's `if self.tp_size > 1:` gathers still count 2. That's checked on the real vLLM classes, and covered in `tests/acquire/test_tp_partial_source_mid_module.py`.

**Proof:** `vllm-config-run-tp2/cov-p081-gaps1`, on the epoch tree `5bab849b1` plus both fixes, through the dispatcher with a research question.
- Build PASS.
- Commit PASS rc 0 (1248 s), warm-up 0 errors on both ranks, TP-12 296/296.
- Config PASS, replay 460/460 equal, run root `24f11e3097a137d7`.

**Next:**
- p085 (Qwen3-30B-A3B TP2 B8) should pass on the same tree; it's the epoch run's to release.
- The TP2 gaps now stand: staging (p051 proven; p108 and p040 have the same cause) and MoE identities (p081 proven) are fixed.
- Still open, waiting on your answer about ownership of the manifest/capture rule changes: Gemma-2's logits gather (p058) and OLMoE's q/k gather sites (p069, p073).
