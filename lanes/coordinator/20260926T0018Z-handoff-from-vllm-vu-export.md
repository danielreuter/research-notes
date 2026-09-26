---
lane: coordinator
kind: handoff
from: vllm-vu-export
created: 2026-09-26T00:18Z
---

# Handoff from vllm-vu-export: first vLLM VU instance sets registered (#101), exporter on PR #42 (00:18Z)


This is plan step 1 of `docs/vllm-subcircuit-coverage.md`. The tables spec is untouched, and nothing was added to Table 2. Admitting captured sets is still Daniel's call; every artifact's meta says so (`table2: not admitted`).

**Code:** PR [#42](https://github.com/danielreuter/verity/pull/42), branch `cursor/vllm-vu-export-289b`, head `140c637c` (merge-ready once reviewed; details in the vLLM coordinator's handoff).

- The Commit stage exports only on request (`--vu-export-dir`). It draws a stratified sample over the replay's population (the replay's strata, `verity.randomness.derive` from the run root), evaluates each VU exactly as the replay does, and exports only the VUs that replay bit-exactly.
- Each row is cut into the subcircuit a backend proves. Every instance is re-evaluated under that relation before it's written.
- Store kinds: `vllm-vu-set/v1` for one set and `vllm-vu-export/v1` for one row's export (`refs.sets`, `refs.run_record`). Each set's meta carries the row, model, run, run root, Program and manifest digests, source (commit, dirty, tree, branch), `epoch: pre-epoch` and `content_digest`.

**#101** (Llama-3.2-1B, B1 256/32, stochastic): run `r20260925-233347-8515` equals the record (program `ccc21347…`, manifest `90f81868…`, run root `7adcef49…`). Export `art:b5bb0ca9199c01289041f74c96577beaa045ff1b035796da7b264c378e54e5c4`. 256 VUs were drawn per family (all 32 for sampling), and all replayed equal.

| Family (population) | Set | Instances | MB | Art |
| --- | --- | ---: | ---: | --- |
| Gemm_v1 (18,400) | `gemm-coordinate-ampere-bf16-k2048` (x, w, y) | 6,272 | 52.0 | `art:123dc234…` |
| | `gemm-coordinate-ampere-bf16-k8192` (down_proj) | 1,920 | 63.1 | `art:927a4c3a…` |
| Attention_v3 (4,592) | `attention-head-fa2-d64-bn128` (q, k[T·64], v[T·64], out) | 1,024 | 41.3 | `art:6312cb50…` |
| RoPE_v1 (9,184) | `rope-head-d64` | 1,024 | 0.5 | `art:16825154…` |
| RMSNormFusedCuda_v2 (9,184) | `rmsnormfusedcuda-v2-n2048-00e4e4aa` | 256 | 5.3 | `art:a261c0c2…` |
| RMSNormTriton_v1 (287) | `rmsnormtriton-v1-n2048-00e4e4aa` | 256 | 3.2 | `art:9582a734…` |
| SiluMul_v1 (4,592) | `silumul-v1-i8192` | 256 | 12.6 | `art:d3e2d9b1…` |
| GumbelTopPTokenSelect_v1 (32) | `gumbeltopptokenselect-v1-v128256` | 32 | 8.2 | `art:ea781b02…` |
| Embedding_v1 (287) | not exported (a commitment opening, per the spec) | | | |

The total is 11,040 instances and 186 MB. The GEMM sets use the `fixtures/bench-instances/v1` layout at K 2048 and 8192, which is the same `GemmCoordinate<K>` relation over `AmpereBF16TcDot16_v1`.

**#4** (SmolLM2-135M, B16) is running now, `r20260926-000408-c3b4`. It's FAIL on record, so it's a fresh pre-epoch run on main plus the exporter. I expect it to finish around 03:30Z, provided Commit fits the 188 GB pod.
