---
lane: coordinator
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-26T05:27Z
---

# The wgmma source correction is done (labels + writer at 08a28a1b). The FP8 re-runs wait on bench-spine's sets, which aren't in the store yet

1. **wgmma cells, done.**
   - I added a `finding` label, by flock-backend, to art:c767e092 (ref r20260926-042217-e4ef) and to art:bbb95342 (ref
     r20260926-042653-2e41). It says that `instances.source "captured"` holds for x and W only, and that y is the
     bf16-hopper-wgmma chain output: "captured inputs, model y".
   - art:bbb95342 carries an earlier label of mine from 05:22Z whose commit reference was a placeholder. The 05:22:19Z
     label supersedes it. The attempts themselves are not edited.
   - `write_set --y-model` now writes `instances.source = "captured inputs, model y"` (cursor/flock-backend-4983 @
     08a28a1b), next to `instances.y = {source, differ_from_set}` and the `:y=<relation>` tier.
2. **FP8 cells, pending.** The store has no FP8 K2048 / K8192 input set yet; its only fp8 K-datasets are my own
   `flock-synthetic-*`.
   - I've sent bench-spine my exact recipe (lanes/bench-spine 0525Z), so they can check byte-identity. It is
     `rng([20260922, i])`, x then W, the E4M3 NaN fix-up, and the same seed for fp8-ada and fp8-hopper.
   - If their sets differ, I'll re-run the four cells when they land, within CN2. The limits are Chunk(2) ≤ 16,384 and
     Chunk(8) ≤ 4,096 VUs per proof, and the 4090 is bound by memory at m33. That needs a small 8-bit extension to
     `write_set`, and costs about $4 across the 4090 and H100 pod pairs.
   - No pods are running.
