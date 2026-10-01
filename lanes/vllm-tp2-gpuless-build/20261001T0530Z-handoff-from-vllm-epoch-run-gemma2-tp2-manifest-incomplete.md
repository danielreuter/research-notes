---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: handoff · to: vllm-tp2-gpuless-build, cc vllm-coverage-defs and @circuits · created: 2026-10-01T05:30Z

# Gemma-2-2B TP2 B1 (cov-p058-2) Build: the manifest is incomplete at TP2: the logits softcap after the vocab all-gather has two producers

- **The row:** `gemma2-2b__bf16__rtxpro6000__tp2__b1__i256__o32__mixed__greedy__bi-eager`. The tree is `5bab849b` (#619–#624, your `4009ec30` and
  `b642a4a4b`), and the attempt is `r20261001-051040-a589`. The Build gave rc 1 and manifest rc 4.
- **manifest.log:** `manifest INCOMPLETE: 1 unmodelled key(s), first ['Bf16MulScalar_v1 under logits_processor (out: two producers AllGather2_v1
  256000 / Bf16MulScalar_v1 256000)']; tp_peer_binding n_unbound 0`. 73482 identities, `complete: false`.
- **Reading:** at TP2, vLLM all-gathers the vocab-parallel logits, and Gemma-2's final-logit softcap scaling (`Bf16MulScalar`) then writes the same
  output. The manifest has no model for that pair. Gemma-2 TP1 passes (k06, m006, n031, n035 and others).
- The other 10 Gemma-2 TP2 rows are held until this is modelled. The log is on vy-nebius-1, under `/workspace/jobs/cov/cov-p058-2/<row>/manifest.log`.
