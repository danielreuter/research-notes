---
cursor:
  subagentId: "bc-ea0126bf-bf03-596f-a835-f4c8d8da987d"
---

lane: vllm-coordinator · kind: finding (blocks task 1 as directed) · from: vllm-coverage-defs (bc-ea0126bf) · cc: vllm-epoch-run · created: 2026-09-30T09:31Z

# Top-p: the per-split `_v3` composite can't pass the word check as directed. I need a decision.

## The threshold

`GumbelTopPTokenSelect_v2{V,S=32}` word gates, measured on main `cc0f4688`. S is 32 for a single request on every SM count, so every single-request cell has S = 32.

| V | gates | vs `MAX_GATES` = 24,000,000 |
|---:|---:|---|
| 24,576 | 21.36 M | passes |
| **27,995** | 23,999,904 | **the largest V that passes** |
| 27,996 | 24,000,658 | fails |
| 32,000 (TinyLlama) | 27.0 M | too-large |
| 49,152 (SmolLM2) | 40.0 M | too-large |
| 50,304 (Pythia) | 40.8 M | too-large |
| 128,256 (Llama 3) | 102.4 M | too-large |
| 151,936 (Qwen) | 122.9 M | too-large |
| 256,000 (Gemma 2) | 204.3 M | too-large |

- **Every top-p cell in the coverage table fails.** The SmolLM2 cell the sweep lane is running will fail the same way, at 40 M gates.
- The keep word accounts for about 98% of the gates, roughly 800 per lane. Its step kernel dominates: 5 rounds × 8 pivots × about 20 operations per lane.
- `too-large` is `word.MAX_GATES`, a memory budget of about 0.6 KB per gate. It is not a width violation. On a big-memory pod, `VERITY_QWORD_MAX_GATES=GumbelTopPTokenSelect_v2=120000000` would pass today's `_v2` at Llama's 128k (about 60 GB). The cut would be one unit per Call (the token id), about 10¹¹ ANDs. `docs/backend-sweep.md` already records this.

## No expected record binds `_v2`

- `integrations/vllm/tests/regression/expected/` has 5 records. The only stochastic one, `llama32-1b__…l40s…stoch-t0.8-p0.95`, binds `GumbelTopPTokenSelect_v1{V=128256}` (the primitive keep word), not `_v2`.
- So binding a new `_v3` moves no expected digest.

## Why the composite doesn't fix it

`Q_word` v1 is pinned in core (`verity/ir/cut.py` steps 2–4, vectors in `tests/ir/qword_vectors.json`).
- It recurses into a body's nodes **only when the body is separable**: every node reads only parameters, and the body returns every leaf.
- It cuts any other body as **one flat `CallGraph`** (`word.unit_rule`, `cut.evaluate_definition`).
- A top-p select is a chain: stats, then a merge, then 5 rounds of per-split step and combine, then a mask, then Gumbel. So a `_v3` composite made of per-split sub-Calls is non-separable. The word check would still flatten it into one Call of about 100 M gates at V = 128256, still too-large, and one unit.

"Each Call is one split plus a merge Call, each within budget" only holds if the pieces are **separate Calls of the Program's root body**. A body node of one Definition doesn't count.

## Options (each is a decision for you)

1. **Root-level pieces (a program change).** The frontend emits roughly R·(S+1) + 2S + 2 Calls per sampling event: per-split stats, step and mask Calls plus merge and combine Calls. The last is a sampling-event Call that reads the keep bits or the masked row.
   - Q_word v1 then cuts each piece on its own, and each fits: a split step is about 0.6 M gates at 128k.
   - But every value between pieces must be a required value, or it's an `input-not-committed` violation. That needs a `Q_module_body_v1` policy extension (a new protocol-required class: the sampler's interior boundary values).
   - Serving then has to commit them: the per-split partials, pivots and keep bits, which are interior top-p kernel buffers. That means reading them at serving, or recomputing them from the committed logits.
   - It also touches the sampling-event machinery (`SAMPLING_EVENT_FAMILIES`, the step segmentation, the fold/Match compare `35b35236`, the replay row evaluator `edc217cf`, `stoch_recompute`).
   - It's large, and it changes what serving commits.
2. **Q_word v2: commit a nested composite's node boundaries.** This is a new query version of record in core, so every digest's query id moves. I don't recommend it.
3. **Raise the sampler's gate limit** (existing machinery, `VERITY_QWORD_MAX_GATES=GumbelTopPTokenSelect_v2=…`, allowed per row by a GO in `epoch.py`) and run the word check on a big-memory host.
   - It needs no code, and the word check passes. vy-nebius-1's CPU should hold about 60 GB for 128k, and Gemma at 256k needs about 120 GB.
   - The Call stays one unit, so it's unprovable in practice, but that's already true for `_v2` below the threshold.
   - I can run the Llama-3.2-1B rtxpro6000 Build and word check this way on vy-nebius-1 as evidence if you want.

I'm not building `_v3` until you pick. Nothing I could write as a single Definition changes the word-check outcome. Meanwhile I'm doing task 2 (Pythia `LayerNorm_v1`).
