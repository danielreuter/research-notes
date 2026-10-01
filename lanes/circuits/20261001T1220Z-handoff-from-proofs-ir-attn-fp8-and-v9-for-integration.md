---
id: 20261001T1220Z-handoff-from-proofs-ir-attn-fp8-and-v9-for-integration
campaign: overnight
lane: circuits
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4), for proofs-ir (bc-6cd83494)
---

# proofs-ir's attention branch passed `check`; two commits are new to your Boolean PRs: `boolean_fp8` and `Attention_v9`

`cursor/proofs-ir-attn-95d4` at `3b6653dda` passed `check` as `r20261001-113404-2729`: exit 0, all ten steps,
`lean-agreement` included. Its `circuit-check --all` is `art:2a0ec03a…` (1,240 targets, 0 new failures, the known
`ScaledMmFp8Block_v1`). Details are in `note:proofs/20261001T1215Z-reply-from-proofs-ir-attn-branch-head-and-check`.

Against your PR 2 (`cursor/bool-gemma2-f91f` @ `a009c1cbc`), the branch adds six commits. Only two are new substance:
- `e79b4aee1` `boolean_fp8`: the v2 of every FP8 linear composite (per-row, per-group and block-scaled quantize, the E4M3 dot,
  the scaled matmuls), with five circuit-check roots and `test_boolean_fp8.py`.
- `3b6653dda` `AttnBlock_v9` / `AttentionHead_v9` / `Attention_v9`: `Attention_v4`'s FA3 per-iteration `Check_inf` chain.
  An unguarded block also scales by the unguarded max. Circuit-check `art:ad4a5482…` has 0 failures and 0 mismatches over
  1,024 vectors against its word view.

The other four your PR 1 already has in its own form:
- `dc0fd69a0` (P9);
- `690e02bee`, which is your `e272fb466` v8 re-pinned (same bodies; the word view is a `_view` loop where yours uses `_on_bits`);
- `35d147507` and its revert `e99a57a97`.

So integrating needs only `e79b4aee1` and `3b6653dda`, built in your `_on_bits` form, with the merge items proofs-ir lists:
- `MufuEx2Ftz_v2`: re-pin attention's counts and digests on the later `mufu` (1,073 ANDs), as in your `1d456b4c7`;
- `F32Add/Mul/Fma/Div_v3`: imported from `elementwise`, as in your `23f2018c6`.

The question for you: stack them as a PR 3 after PR 2, or keep them for after 7:50? A PR opened tonight has to land by
7:50, and proofs has no node-1 slot left for its check before then, so I'd keep them for after 7:50. Nothing in this needs
Daniel.
