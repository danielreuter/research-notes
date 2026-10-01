---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits · created: 2026-10-01T01:10Z · on your 00:48Z handoff, vllm-coverage-defs' 00:53Z and the relays

- **The second Gumbel proof passed.** g219 (Llama-3.2-1B Gumbel B8 256/32, tree `cad0dff3` with #611) is `r20261001-003822-ca08`.
  - The Commit sealed its bundle, and the CPU replay passed 460/460. Run root `36234b03702162b8`.
  - With g211's proof, both pass. **The Gumbel subset is out:** 21 deployments at 256/32, each with its question, paced by the steward's
    release.py.
    - B1: SmolLM2-135M, Qwen2.5-1.5B and Qwen2.5-7B.
    - B8: the other 10 models.
    - B32: the 8 models of 4B or less.
  - B32 of 7B+ and MoE stays deferred, and the other Gumbel rows stay held.
- **TP2 is now head_dim 64 only.** p004 (Llama-3.2-1B TP2 B8) and p016 (TinyLlama TP2 B8) are dispatched (`TP2_MAX` 2). Their B1 rows,
  p000 and p012, already pass.
  - The other 9 queued TP2 cells are back in the deferred list until the TP2 lane's fix.
  - p036 (Mistral-7B) and p104 (Qwen2.5-7B) crashed like the rest, and are labelled with the head_dim > 64 cause.
- **Gemma-2: your call.** The 39 `grid_deferred_gemma2` deployments stay held. When you say go, I'll merge the six granted PRs into
  `cursor/coverage-v1-2622` pre-merge and release them, below B8 first.
- **Noted for the move to main:** main's Qwen2/2.5 Programs add call-boundary identities at `qkv_proj` that stall a Commit (vllm-coverage-defs). My
  Qwen2.5 runs stay on `cursor-coverage-v1-2622`, where #557's Programs pass.
