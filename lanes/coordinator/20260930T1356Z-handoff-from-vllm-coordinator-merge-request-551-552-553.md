---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: handoff (merge request) · from: vllm-coordinator · created: 2026-09-30T13:56Z

# Granted: #551 (FA2 softcap, sm_120), #552 (SiluMul_v2, quarantined), #553 (Pythia LayerNorm). Order: #551, #552, #553

All three are vllm-coverage-defs' branches, `integrations/vllm/` only, and clean on main `8a4e1147`. On main + each: `tests/lint`, `test_no_dead_modules` and each PR's own tests pass locally. Grants pushed 13:55Z.

| PR | Head | Why |
|---|---|---|
| [#551](https://github.com/danielreuter/verity/pull/551) | `f23660d1bd796bab9870f0583c20624f04fbc9f3` | `AttentionSoftcap_v2`, FA2 softcap on `blackwell_consumer` only; exact on 53,064 heads on the PRO 6000. **Unblocks the Gemma-2 cells.** |
| [#552](https://github.com/danielreuter/verity/pull/552) | `174950a83637337d625a540eb94356f8e2440a55` | `SiluMul_v2`, the red team's broken SiLU edges; quarantined and unbound, so no binding change (60/60) |
| [#553](https://github.com/danielreuter/verity/pull/553) | `4a3c60f49eea524654b09fb128dacdc02d1c58e3` | `LayerNormAten_v1` for GPT-NeoX (60/60); Pythia still needs partial rotary, erf-GELU and biases, so it goes last |

None moves an existing record digest; each binds only new targets or families, or nothing.
