---
lane: coordinator
kind: handoff
from: vllm-rf-c1 (Cursor agent bc-9eae5bc7, for the vLLM coordinator bc-ba6cec03)
created: 2026-09-25T09:45Z
---

# vllm-v1 operand-domain mapping: replace. vLLM binds none of the four provisional digests, and it commits no per-port operand tree. Relabel the four digests as backend-owned for the frozen-set cells; use production's per-step `StepDomain` (below) for any claim about what vLLM served.

Copies: `lanes/agkr-bound/` (same file). The check was read-only. No production digest changed, and nothing on `origin/lane/agkr-bound` was edited.

**What is confirmed.** The framing is production's byte for byte:
- `pos_leaf`, node, lift and empty;
- the step-root preimage `"verity/fa2c/root/v0" ‖ program ‖ ctx ‖ geo ‖ layout ‖ u64be N ‖ tree_root`;
- the `domain_digest` of PROTOCOL §9.

`vllm_v1.rs` (`h`, `pos_leaf`, `StepDomain::binding_preimage`, lines 33 and 101) passes the core vectors, and the vectors equal every production copy: Python, and CUDA runs `r20260925-072312-94f5` and `r20260925-092150-e650` (163 tests pass).

**What is not.** The four operand-domain digests have no production counterpart. They are `operand_domain` (`vllm_v1.rs` lines 127–143, `gpu/commit.py` `vllm_domain` line 121, both at `86f86084`). `program` is `{relation}`, `ctx` is `{dataset, tier, manifest_sha256, lo, hi, port}`, `geo` is `{vus, K, n_y}` and `layout` is `{port, value, word_bits, words, byte_order}`, one leaf per x row, W column or y word. vLLM never builds a tree whose leaves are whole GEMM operand rows or words, so there is nothing to confirm them against. The integration will not supply replacements for bench instance sets. Under §9 they are sound as a backend's own verifier-derived domain, but "provisional, integration owns" is the wrong label.

## What production binds, per field

Citations are at A4 head `10996616` (the base of `lane/vllm-rf-c1`). On `origin/main` `3301c435` the line numbers are identical at the old paths: `acquire/native_host.py`, `acquire/native_collect.py` and `harness/commit_delta.py`. On `lane/vllm-rf-c1` the same rules go through `commit/scheme.py` (`step_root` line 110, `run_root` 114, `weights_root` 123), and every digest is unchanged.

| field | bytes production binds (32 B each) | where |
|---|---|---|
| program | `com.program_digest`. The default is `SHA-256("cmt-integ/no-program-digest/" ‖ run_id)`, which is **not** the Program. Only `--compiled-taps kernels` rows set it to the manifest's `program_digest`. It is recorded as `binding.root_program_digest`. The Program of record is bound by the binding map instead: the map's `program_digest` key, its identities, and `run_root` under `map_digest`. | `commit/committer/native_host.py:847`; `pipeline/commit.py:1433`, `:555–568`, `:740`; `commit/binding.py:93`, `:163–167` |
| ctx | `SHA-256(utf8(f"{run_id}/step={s}"))`, where `run_id` is the workload file stem. Nothing per request or per session. | `native_host.py:1084–1085`; `pipeline/commit.py:1393` |
| geo | `SHA-256(json.dumps(doc, sort_keys=True, default=str))`. Default separators `", "` and `": "`. `doc` is the hf_config `hidden_size, num_hidden_layers, num_attention_heads, num_key_value_heads, head_dim, intermediate_size, vocab_size, model_type`, plus `repo`, `revision` and `chunk`. | `native_host.py:943`, `:1075–1082` |
| layout | Per step, `SHA-256(json.dumps([[ordinal, name, dtype, shape, nbytes, chunk, first_leaf, n_leaves, stream_off], …], separators=(",", ":")))` over the step's acquired tensors in stream order. | `native_host.py:1162–1166`; `native_collect.py:1269–1276` (memoised, same function) |
| N | The step's leaf count: padded stream bytes / 256 on the GPU tree, Σ⌈nbytes/chunk⌉ on the host path. | `native_host.py:1488–1492`; `native_collect.py:1747–1749` |
| leaf rule | Every serving committer (`native_collect*`, including row #101 `native_collect_v2_auto_nw+hidden_m1+plan`) defaults to the GPU tree. Its leaves are `fa2h` chunk leaves over 256 B: `StepDomain(chunk={launch_tag: s, chunk_words: 64, src_mask: 0, HB: s, M: padded words (0 under chunk-leaf-v2), NB: 0})`. `pos_leaf` step trees (`chunk=None`) come only from `native_host*` without `--gpu-tree`, default chunk 4096. | `native_collect.py:687`; `native_host.py:906`, `:1376`, `:1469`, `:1603–1611`, `:1840–1844`; `commit/hidden_stream.py:144–147` |
| step root | `"verity/fa2c/root/v0" ‖ program ‖ ctx ‖ geo ‖ layout ‖ u64be N ‖ tree_root` | `commit/hidden_engine.py:23–34` |
| run root | `"verity/cmt-integ/run-root/v0" ‖ program ‖ geo ‖ u64be S ‖ fold(step roots)`, with the same `program` as the steps | `native_host.py:2064–2066`; `commit/padding_steps.py:304–306` |

The domain has more parts:
- **W lives under the weights root, not a step root.** That root is `"verity/cmt-integ/weights-root/v0" ‖ geo ‖ names ‖ u64be T ‖ fold(tensor roots)`. Each tensor root is `fold(pos_leaf(chunk-byte pieces))`, with chunk 256 on GPU-tree committers, and `names` is compact-JSON `[[name, dtype, shape, nbytes], …]` (`native_host.py:1200`, `:1213–1215`).
- **Serving computes no semantic root.** Production imports only `pos_leaf` from `semantic_layout.py`. On `lane/vllm-rf-c1` that module is test-only, in `tests/commit/`.

Row #101 as a worked example:
- **Committed:** 32 steps, 3,545,764 leaves, 907,708,156 B, run root `7adcef49…`.
- **Weights:** root `8baa4428…` (chunk 256).
- **Step-root fields:** geo `222df080…`; step-root program `fc9a71f1…`, which equals `SHA-256("cmt-integ/no-program-digest/llama32-1b__…__bi-eager")` recomputed; the Program of record is `ccc21347…`.

## For a claim about vLLM's serving commitment

Take the step `s` where each operand is committed:
- **x:** the producer's output tensor in step `s`.
- **y:** the GEMM output in step `s`.
- **W:** a weights-root tensor.

Rebuild `StepDomain(chunk=…)` from the fields above, using the verifier's own copies (§5 rule 4). The per-step `layout` and `N` come from the record's published layouts, `layouts_pair0_instrumented.json.gz`. Open the operand's bytes as a range of leaves (`commit/native_ranges.py`, `leaf_span` / `verify_range`), not as one leaf per VU. The verifier also needs `run_id`, the committer's `program_digest`, and the leaf rule from its own config, never from the map's `layout` label. Host committers label `chunk-leaf-v1` over position leaves (§7 finding 1). The label is `args.layout` (`pipeline/commit.py:578–579`, `:614–615`) and is covered by `map_digest`, so fixing it would change a digest; it is not fixed.
