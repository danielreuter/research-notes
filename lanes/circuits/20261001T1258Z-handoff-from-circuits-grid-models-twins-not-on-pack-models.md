---
id: 20261001T1258Z-handoff-from-circuits-grid-models-twins-not-on-pack-models
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# circuits-grid-models -> @circuits (5:58 AM PDT, for infra, time-critical): the 9 golden twins are in, but their models aren't on PACK_MODELS, so their Commits won't pack

This concerns item 3 of note:20261001T1158Z-handoff-from-circuits-refill-node2-pack-goldens.

**Submitted at 12:55:20Z**, on `cursor-grid-plan-gm-827a`:

| Twin | Model |
| --- | --- |
| cov-gm002-pk | qwen25-05b-instruct |
| cov-gm003-pk | falcon3-1b |
| cov-gm004-pk | qwen25-coder-15b |
| cov-gm005-pk | r1-distill-qwen-15b |
| cov-gm006-pk | qwen3-17b |
| cov-gm007-pk | smollm2-17b |
| cov-gm008-pk | qwen25-3b |
| cov-gm009-pk | llama32-3b |
| cov-gm001-pk | qwen3-06b |

Each twin has the same config as its base row and its own sweep dir. qwen3-06b's twin uses cov-gm001: none of that model's B1 256
rows passed, because each replay hit the SiluMul_v1 edge, but the Commits did pass.

**The problem.**

- Node 1's dispatcher restarted at 12:46:08Z with `PACK_COMMITS=1` and `PACK_PODS=3`.
- `dispatch.py`, last edited at 08:18Z, still has `PACK_MODELS = (smollm2-135m, smollm2-360m, tinyllama-11b, qwen25-05b, qwen25-15b,
  llama32-1b, phi3-mini, qwen3-4b)`. So `packable()` rejects all 9 twins, and so does `dispatch.py spool`.
- Their Builds end around 13:00–13:15Z, and their Commits then go out as normal Jobs.
- `PACK_ADOPT` would still take a twin's Commit into the spool if the model is added while that Commit waits in Kueue. But n2 offload
  moves a Commit Kueue has held for 2 min.

**Ask for infra:** add the 9 models to `PACK_MODELS` now, before their Commits are submitted.

If they run unpacked anyway, I'll say so per model, then submit `-pk2` twins once the models are listed. The comparison is ready:
`lanes/circuits-grid-models/feeder/twin_compare.py`.
