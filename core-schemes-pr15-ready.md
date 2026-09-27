---
cursor:
  subagentId: "bc-ca9e6876-1d5d-5c10-a7cc-1cc77d01f2e6"
---

# core-schemes: PR #15 is ready to merge

**For:** the research coordinator (bc-4100fff0-95e2-5fbf-a7dd-2bcabac71388). **As of:** Fri Sep 25, 06:50 UTC.

[PR #15](https://github.com/danielreuter/verity/pull/15) (`danielreuter/verity`, branch `cursor/vllm-commitment-scheme-f2e6`, head `fa9c4594`) is ready for review, not a draft, and ready to merge. It is additive and changes no existing roots.

**Tests:** `uv run pytest` shows only the five failures already on `main` for this VM: the ligero blob limit, rsync pods, pythonpath, store honing and telemetry. The `integrations/vllm` `tests/commit` suite and `backends/direct/ligero/leaf/core_schema_test.py` pass; neither is in the root `testpaths`.

## What the downstream lanes can use once it merges

| lane | use |
|---|---|
| commit-gpu | vectors for both schemes: `frame_v3/vectors.json` (full row bytes, trees, paths) and `vllm_v1/vectors.json` (leaves, trees, openings with fold traces) |
| B-Ligero | `blake3-keyed/row/v2` promoted byte for byte; `sha256/row/v1`; `leaf_layout` for `vllm-v1` leaves (a 26-byte position-leaf prefix needs offset absorption) |
| A-GKR, SP1 | `sha256/row/v1` (a constant 64-byte first block); `FrameV3.tree_leaf` / `VllmV1.verify_path` for the native tree checks |
| all backends over `vllm-v1` | `vllm_v1/PROTOCOL.md` §8 (byte offsets, SHA-256 blocks, tree shape) and §9 (what a statement must bind externally, including `domain_digest`) |

## Open items, not blockers

- **The four vLLM CUDA copies** still have to be checked against the vectors, and that needs a GPU:
  - `native_tree.cu`
  - `hidden_gpu_tree.cu`
  - `native_leafhash.cu`
  - `verity_tap.h`

  The two tree kernels hard-wire chunk-header words 8 and 9 to 0, so they can only reproduce the legacy-tile chunk vectors.
- **The weights root** needs a live model, so only the reference vector checks it.
- **`vllm-v1` defines no multiproof encoding.** A backend opening many leaves has to define its own sharing rule (§8.2).
