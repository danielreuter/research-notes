---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: vllm-coordinator
kind: handoff
from: coordinator
created: 2026-09-30T18:48Z
---

# #557 came out of train TVQ: it changes the stored TP2 MoE manifests without re-pinning them

- **The failure:** TVQ's check `r20260930-182113-0a2c` (`main` `d079ac2c` + #557 `470cf59d`) failed both rows of `integrations/vllm/tests/query/test_tp_moe_members.py::test_the_stored_tp2_moe_builds_merge_with_every_peer_bound`.
  - `qwen3-30b-a3b__bf16__l40s__tp2__…` builds a manifest with sha256 `6924898319e3…903625c80ccd1`, but `MANIFEST_SHA256` pins `1fbe75e68525…8ae906d5f3ae2`.
  - `olmoe-1b-7b__…` fails the same way.
- **Not a flake:** `main` passed this test in TVP just before.
- **Please:** if #557 is meant to change the manifest, re-pin both digests in `MANIFEST_SHA256` and say why in the PR. If it isn't, find what moved it. Then re-grant; it takes the next vLLM train.
