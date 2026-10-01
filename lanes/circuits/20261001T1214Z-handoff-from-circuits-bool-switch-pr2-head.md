---
id: 20261001T1214Z-handoff-from-circuits-bool-switch-pr2-head
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-switch
---

# @circuits (5:14 AM PDT): PR 2 (Gemma-2's norm chain) is `cursor/bool-gemma2-f91f` @ `a009c1cbc`, stacked on PR 1; body in the store at `internal/circuits/bool-integration-pr2-body.md`

**The branch.**
- `a009c1cbc` is bool-norms' head as they sent it (note:20261001T1158Z-handoff-from-circuits-bool-norms-gemma2-head). It merges PR 1's `443538fed`.
- PR 2 gets its own branch so that PR 1's head stays at `443538fed`.
- Its diff against PR 1 is 6 files: `boolean_dense_norm` with its three Definitions over `boolean_dense`'s rows (per your ruling), `boolean_norms`' word views at construction, the tests, and circuit-check's targets and pins.

**circuit-check.**
- Locally, in `--all` mode, the 5 new roots and the 2 Boolean-MUFU norm roots give 0 failures.
- Norms' 2 `partition/gate-recomputed` failures are `--as-call` only: a recompute across an opaque Boolean MUFU Call, which #667 allows. `--all` doesn't check Boolean families as Calls, so they don't fail `check`, and there are no `known.py` entries.
- Running on node 1: `circuit-check --all`, the `verity-circuit-check` suite, and vllm's Boolean, norm, lint and frontend tests at `a009c1cbc` (`r20261001-121243-db76`). I'll fill the body's two *(running)* lines.

**Not in PR 2.**
- Softcap: proofs' `MufuTanh_v2` is at `abc153b55`; adding it is a revert of `eb8cb9169` plus one binding.
- SiLU v4: bool-silu's `7e5711a92`.
- Without softcap, Gemma-2 isn't yet pure Boolean. I can stack softcap on PR 2 if you want it in. Say so.

**Not re-established:** the chain's 80k-row comparison was taken on norms' former copies of the eight shared ids. Re-running it needs a pod (about 3 hours on one core), and nobody has started it.
