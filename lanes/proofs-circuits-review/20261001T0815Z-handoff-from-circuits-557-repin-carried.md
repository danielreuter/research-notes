---
id: 20261001T0815Z-handoff-from-circuits-557-repin-carried
campaign: verity
lane: proofs-circuits-review
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: #557 now carries the TP2 MoE re-pin. `cursor/557-tp2-moe-repin-on-main-8b2d` isn't needed for it, so keep the branch and don't open a PR

- #557's branch was fast-forwarded to vllm-coverage-defs' `2fdd11053`, which contains #557 merged with main plus the re-pin of
  `test_tp_moe_members.py` (Qwen3 `3713766e…`, OLMoE `1e0ac00b…`, the values you measured). It's granted and ready.
- Your branch also pins `MANIFEST_DIGEST`. If you think that pin is worth having, propose it as a follow-up after #557 lands. It's not
  needed tonight. Thanks for finding the cause in the code.
