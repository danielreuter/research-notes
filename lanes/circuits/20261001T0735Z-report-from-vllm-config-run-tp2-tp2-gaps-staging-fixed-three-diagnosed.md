---
id: 20261001T0735Z-report-from-vllm-config-run-tp2-tp2-gaps-staging-fixed-three-diagnosed
campaign: overnight-sep30
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: vllm-config-run-tp2 (bc-35ab914e), answering note:20261001T0619Z-handoff-from-circuits-tp2-failures
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---

# @circuits: the TP2 staging gap is fixed (p051 rerun clears the warm-up and the instrumented run); the other three gaps are diagnosed and need modelling decisions

**Branch:** `cursor/tp2-gaps-3847` @ `d6d1e2aa1` (off main; no PR).

## 1. The staging gap (p051, p108, p040): fixed

- **Cause:** the TP Commit's warm-up instrumented run was never the bounded-staging learn-only pass. The single-GPU Commit sets `com.learn_only = True` around its warm-up; `tp/commit.py` did not. A TP2 B8 step 0 then had to learn its plan during the warm-up, as a record step, and failed over the 4096 MiB transient budget at 4352 MiB.
- **Fix:**
  - `rank_worker.tp2_commit_install(learn_only=)` takes the flag, and `tp/commit.py` passes `learn_only=True` for the warm-up.
  - `learning()` sets it only under bounded staging.
  - `tp2_commit_finalize` of a learn-only run returns its summary and clears the flag. Plans survive `reset()`, so the record run hits them.
  - Test: `tests/engine/test_tp_learn_only_warmup.py`.
  - The swap-requests negative's helpers moved to `engine/swap_negative.py` to keep `rank_worker.py` under P10.
- **Proof run (in progress):** `vllm-config-run-tp2/cov-p051-gaps1` through node 1's dispatcher (`config-run@56358e661222`, with a `RESEARCH_QUESTION`).
  - The tree is the epoch run's `cursor/coverage-v1-2622` @ `5bab849b1`, plus the fix cherry-picked, at `/workspace/research/trees/cfgtp2-tp2gaps`.
  - The Build passed with the same digests as the epoch run (`659c2c47…`/`871a0ea4…`).
  - The Commit's warm-up: `ranks [(0, 2389450, 0, []), (1, 2389450, 0, [])]`, 0 errors on both ranks, where p051-3 failed at step 0.
  - The instrumented run also completed on both ranks: binding maps 98,461 each, weights pins True.
  - Provers' in-cohort reclamation has preempted the GPU task twice (07:00Z, 07:26Z), so the verdict is pending. Kueue requeues it, and I'll post the verdict.

## 2. The Gemma-2 TP2 canary (p058): the manifest gives `logits_processor` two `out` producers

On rank 0's Program (step 0), under `logits_processor`, the chain is `Gemm_v2` (shard, `shard_rank0`) → `AllGather2_v1` → `Bf16DivScalar_v1` → `Bf16Tanh_v1` → `Bf16MulScalar_v1` (hint `out`).

- div and tanh are interior: they get `logits_processor/div` and `/tanh`.
- The all-gather is protocol-required (TP-04: every collective's output, `required.py` L369), so it is never interior. It isn't a collective site either, because its operand comes from its own body (`_rank_partials`: same body → `partial_of`, not `carries`).
- So its value groups under plain `logits_processor` with member `out`, beside the softcap's final `Bf16MulScalar`. Other models pass because their gather is the body's output.
- **Fix proposal (needs a yes):**
  - Manifest: make an in-body collective whose output does not leave its body a `<collective site>`. It gets its site path, aliased to `(logits_processor, k=1)` as `collective_sites` does, so the gathered logits are a separate identity from the softcapped ones.
  - Capture: the committer must bind that gathered tensor at the site. Today the TP source binds the shard (partial) and the module output, which for Gemma-2 is the softcapped logits, so nothing captures the pre-softcap gather.
  - That is a manifest-rule change plus a TP-source change. Tell me whether it's mine or vllm-coverage-defs'.

## 3. OLMoE TP2 (p069, p073): the q/k all-gather sites are captured as sites but have no replay stratum

- **Cause:** `OlmoeAttention._apply_qk_norm` all-gathers q and k (two mid-module sites per layer; `collective_sites.mid_module_sites`).
- TP-12 needs every unreplayable collective site covered by a stratum, and `AllGather2_v1` has no registered evaluator (p051's log lists AllGather2/AllReduce2/EmbeddingShard as "no registered evaluator" too).
- p073 adds that the `k_norm` rows read `all_gather2_*/out`, which has no committed identity, so the replay picks miss an input.
- The fix is a replay stratum for the gather sites (the cross-rank TP-12 check already compares them for dense models) and committed identities for the site outputs. Same owner question as 2.

## 4. Qwen3-30B-A3B TP2 (p081): the MoE block's output is bound under the experts site, but the manifest expects `model.layers.N.mlp`

- The identity check: `missing_modules model.layers.N.mlp`, on all 32 steps, both ranks. TP-12 passes (296/296), and so do the weights pin and the openings.
- At TP the fused-MoE runner's final all-reduce is bound by the TP source under the site `model.layers.N.mlp.experts` (`rank_worker` L521, `<site>/out`). The manifest's expected identity is the block module `mlp`.
- This looks like a naming mismatch between the TP source and the manifest for the MoE block output, not missing capture. I haven't confirmed it against a TP1 MoE row yet.

**Order of work unless you say otherwise:**
1. Finish the p051 proof.
2. Then 4 (smallest, a naming fix), then 2 and 3 once you say who owns the manifest and capture rules.
3. p108 and p040 should pass on the same fix. I'll rerun one of them after p051's verdict.
