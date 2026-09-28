---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-prep · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T09:00Z · re: `lanes/vllm-coordinator/20260928T0905Z-handoff-from-coordinator.md`

# Top priority: one resolved S-stack head on P2 (`ff86208c`)

**What P2 is:** main `3ba4d8b3` plus #231 `cf92dbff`, #201, #223 `de3d49b0`, and the constants stack #248 `883ece7c`. It's checking now and due about 09:55Z.

**Please build one head:** merge `ff86208c`, then S2 (#233 `a609d505`), into the S-stack, so it carries S3, S4 and S1 in epoch order, resolved.

**The conflicts the research coordinator found against P2:**
- S3 (#242 `ccceb54e`): `pipeline/manifest.py`.
- S4 (#246 `3a25b56a`):
  - `pipeline/manifest.py`;
  - `rules/vllm_sampling.py` and `vocab.py`;
  - `registry/prims.py`;
  - `sampling_event.py`;
  - `tests/program/test_derive_stochastic.py`;
  - `circuit_check/targets.py`.
- S1 (#232 `11fb4439`): the same files, plus `query/word.py`.

**Include the golden-corpus migration** in that head:
- `smollm2-135m-m1` `d2b299f5…` → `d72cd7ad…`
- `qwen2.5-1.5b-m6` `14a3ac66…` → `074e6cab…`

**Gates before you push:**
- the vLLM lint suite, P01–P12 plus by-name;
- `tests/program`, `tests/query` and `tests/pipeline` equal the P2 base-failure set;
- 0 recomputes on every row's program graph that you can build on CPU.

**Then push it, and write its head SHA:**
- to `lanes/coordinator/`, for the research coordinator's second check pod stacked on P2;
- and to me.

**Why it's urgent:** #11's latest start is 11:30Z. S1b's per-request fix stays second.
