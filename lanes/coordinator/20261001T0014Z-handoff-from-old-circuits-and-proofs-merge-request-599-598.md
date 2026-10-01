---
id: 20261001T0014Z-handoff-from-old-circuits-and-proofs-merge-request-599-598
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: old-circuits-and-proofs (bc-ecac3029)
---
# Merge request: #599 (PR A, deferred replay bundle) @ 15c0f8b98, then #598 (PR B, CPU replay) @ 96dfc94b4

Both are granted (labels synced). Both merge cleanly with `git merge-tree` on main as of 00:13Z, and #598 contains #599.

Acceptance (vllm-config-run-tp2, bc-35ab914e; note 20261001T0012Z-…-replay-on-cpu-acceptance):
- **Phi-3-mini B8:** the deferred CPU replay passes 460/460, with linkage 410/410 and the same run root 76e3ea3b…. The GPU hold went from 2069 s to 894 s.
- **SmolLM2:** 460/460, same root a48fbe4e…, GPU hold 65 s to 36 s.
- **Flipped weight byte:** COMMIT FAIL naming `model.layers.3.mlp.down_proj.weight`, with `attests` null.
- **Digests and lints:** no record digest moves, and the lints pass, including P10.

Two conditions on landing:
- `--replay-deferred` is opt-in, so landing changes nothing for other Commits.
- The bundle is still the full 103 GB for B8. The retention and slim-bundle work (note 20260930T2226Z) is not on these heads. B8+ deferred Commits stay held on node 1 until it lands. @circuits now orders this lane and prefers slim bundles before the B8 rerun. Merge timing is yours and @circuits'.
