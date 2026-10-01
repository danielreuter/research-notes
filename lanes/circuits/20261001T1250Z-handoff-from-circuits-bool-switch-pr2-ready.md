---
id: 20261001T1250Z-handoff-from-circuits-bool-switch-pr2-ready
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-switch
---

# @circuits (5:50 AM PDT): PR 2 is ready. `cursor/bool-gemma2-f91f` @ `1361a9fe4`, on #672's `80703ab0e`; body: store `internal/circuits/bool-integration-pr2-body.md`

**What `1361a9fe4` is.** Norms' `a009c1cbc`, plus #672's `80703ab0e`, plus bool-silu's softcap `54a75c7a3`, with every merge clean. It is 11 files over #672.

**The node-1 run: `r20261001-121525-d743` at `63f836e28` (norms on `80703ab0e`), rc 0.** It replaces `db76`, which I stopped when PR 1's head moved.
- `circuit-check --all`: 1,413 targets, 0 new failures, 1 known (`ScaledMmFp8Block_v1`, on `main`), 0 mismatches.
- The `verity-circuit-check` suite passed.
- vllm's Boolean, norm, lint and frontend tests passed.

**The softcap part, locally on a merge whose tree is identical to `1361a9fe4`'s.**
- circuit-check passes all 5 softcap and `MufuTanh_v2` targets (0 failures, every pin matched).
- vllm's `test_boolean_softcap`, `test_boolean_attention`, `test_boolean_norms`, `test_boolean_switch` and lints pass, and so do core's `test_boolean_mufu` and `test_boolean_attention` (55 tests). `MufuTanh_v2` moves no pinned digest.

**What the body says.**
- The `call_families` gap: the two norm roots fail `--as-call` with one recompute each, even with #667 in the tree, but they don't fail `--all`.
- The 80k-row comparison is re-running (bool-norms).
- fp8, `Attention_v9` and SiLU v4 are out.
- Gemma-2's purity is not claimed: no Gemma-2 Build at `ir=boolean` has been run.
