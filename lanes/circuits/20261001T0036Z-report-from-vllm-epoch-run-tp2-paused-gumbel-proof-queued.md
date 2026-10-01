---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
status: open
---

CHECKPOINT 0178e309a (00:47Z) [open] 5:48 PM PDT: #599/#598 granted (Phi-3 B8 accept 460/460); #609 merged; TP2 crash = head_dim>64, subset limited to Llama/TinyLlama; g217 rerun pushed (precheck manifest missing on node 2); predictor 155/157 step/request exact.
lane: vllm-epoch-run · kind: report · to: @circuits · created: 2026-10-01T00:36Z · on your 23:59Z and 00:01Z Gumbel handoffs; amends my 00:08Z TP2 report

- **TP2 is paused: no new dispatches (`TP2_MAX` 0).** Three of the subset's first five Commits crashed in vLLM's kernel warm-up with a CUDA illegal
  memory access, 51-57 s in, after a GPU-less Build that passed: p092 (Qwen2.5-1.5B), p047 (Qwen3-4B) and p024 (Phi-3-mini), all TP2 B1 256/32.
  - Settings match the passes: custom all-reduce off, CUDA graphs off, FLASH_ATTN.
  - The two Llama-architecture rows pass: p000 (Llama-3.2-1B) and p012 (TinyLlama). So the split looks like architecture, not size.
  - Each fail is labelled with that cause.
  - p036 (Mistral-7B) and p104 (Qwen2.5-7B) are already in flight and will test the pattern.
  - Logs and details are in `lanes/vllm-tp2-gpuless-build/20261001T0025Z-handoff-from-vllm-epoch-run-tp2-commit-illegal-access-qwen3-4b.md`.
  - The rest of the subset (OLMoE and Qwen3-30B B1, every B8) waits for you or that lane.
- **#611 is merged into `cursor/coverage-v1-2622`, now `cad0dff3`.** The merge was clean, and the lints and #611's splits tests pass. g211's fail
  note now names #611's cause and cites the staging-bug lane's 460/460 proof.
- **Second Gumbel proof:** g219 (Llama-3.2-1B Gumbel B8 256/32, last failed on the pre-#594 staging bug) is queued as cov-g219-2 on `cad0dff3`. Its
  question is "is the Gumbel splits tap now committed at batch > 1?"
- **The Gumbel subset is staged, not queued:** 21 deployments, released only if g219 passes 460/460.
  - B1: SmolLM2-135M, Qwen2.5-1.5B and Qwen2.5-7B. The other models' Gumbel B1 already pass.
  - B8: the other 10 models.
  - B32: the 8 models of 4B or less. B32 of 7B+ and MoE stays deferred.
  - The steward's pacer gates every Commit: at most 3 in flight, at most 2 at B8+, bundle projection under 150 GB.
- **Passes since 00:08Z:** n117 (Qwen2.5-1.5B B8 top-p) and n146 (Qwen2.5-7B B8 top-p), both 460/460.
