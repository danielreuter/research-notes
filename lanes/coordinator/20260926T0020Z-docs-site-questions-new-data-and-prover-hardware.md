---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# From the docs site: new benchmark data, and prover hardware as an axis

**To:** coordinator, to pass on to the research coordinator and the census-json lane as fits. **From:** the docs-site worker, for Daniel. **Written:** Fri Sep 25, 5:20 PM PT.

1. **Is there newer benchmark data than the 12:55 PM PT render?** The laptop copy of `docs/proof-optimization-tables.md` still says "Last render: Fri Sep 25, 12:55 PM PT · main `7da00370`", but the sync may be lagging.
   - Are there new cells, such as A-GKR, C-Flock or D-SP1 results, SHA-256 on the 4090 or A100, or `vllm-v1` lines?
   - When the 6 PM switch render lands, where will PR #40's `--format entities` JSON be written in the store, so the site can snapshot it?
2. **Prover hardware is a third axis, separate from the subcircuit.** Daniel's point: a subcircuit's semantics name a chip ("computed bit for bit as the H100's FP8 tensor cores do it"), and that chip supplies N. But the prover runs on some device too, and that supplies P. They're the same device today, but they needn't be: an H100-semantics subcircuit could be proven on a B200.
   - PR #40's `circuits` carry one `hardware` id. Could each result carry `prover_hardware` (a Census id), with the subcircuit keeping the chip its semantics model?
3. **Terms in PR #40 versus the ontology.** The PR body uses `instances` for backends, `subcircuit_kind` for the template, and `circuits` for subcircuits. The ontology note says the JSON will use `backends`, `backend_families` and `subcircuit_template`, and Daniel wants no "kind" for computations. Worth aligning before merge, since the site will key on these names.
4. **A stable id and display name for each subcircuit.** For example `gemm-coordinate/k1536/sm90-wgmma-e4m3` as the id, with display "H100 · FP8 (E4M3)". The site plans to organize the tables around subcircuits and treat everything else as filters.
