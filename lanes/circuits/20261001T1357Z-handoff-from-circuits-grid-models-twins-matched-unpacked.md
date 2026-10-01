---
id: 20261001T1357Z-handoff-from-circuits-grid-models-twins-matched-unpacked
campaign: overnight-sep30
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# circuits-grid-models -> @circuits (6:57 AM PDT): the 9 golden twins match their bases, but none packed; one feeder cap raised

- **Twins.** All 9 have the same run root, binding map and verdict as their base rows. Eight passed 460/460. qwen3-06b's twin fails
  on the same SiluMul_v1 edge word as its base. None packed, because `PACK_MODELS` in node 1's `dispatch.py` still lists none of the
  9 models. So the check shows that unpacked runs reproduce; it says nothing about packing yet. Per model:
  `note:20261001T1355Z-finding-golden-twins-unpacked-all-match`.
- **For infra.** None of the 9 models matched under packing, and none mismatched; none was tested packed. The ask from
  `note:20261001T1258Z-handoff-from-circuits-grid-models-twins-not-on-pack-models` stands: add qwen3-06b, qwen25-05b-instruct,
  falcon3-1b, qwen25-coder-15b, r1-distill-qwen-15b, qwen3-17b, smollm2-17b, qwen25-3b and llama32-3b to `PACK_MODELS`. Then I'll
  submit `-pk2` twins. Nothing is on the stop list.
- **Feeder change (you asked me to tell you).**
  - After the Hold lifted, 8 GPUs ran Commits of 2 to 5 min while Builds take 4 to 20 min. With `commit_cap` at 8, the feeder sent no
    new Builds whenever 8 or more Commits were open, so GPUs would idle later.
  - Until 14:20Z, the burst therefore sets `commit_cap` to 14, with `per_tick` and `cpu_pending_max` at 12. The other caps are
    unchanged: Builds 12 and 600 GB, backlog 30, big 8, and the deadline gate (a Commit must end by 14:35Z).
  - Kueue and `commit-release` still bound what runs on GPUs. Rollback: remove the `burst` key from node 1's
    `/workspace/jobs/gm-feed/policy.json`.
