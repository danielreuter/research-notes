---
id: 20261001T0947Z-handoff-from-circuits-inputs-and-embedding
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: a correction. `Input32_v1` needs NO Boolean version. And a warning about the served `Embedding_v2` Call

1. **Inputs, which replaces my 2:12 AM decision.** Per circuits-bool-casts (`cursor/bool-casts-8c79` @ `35bcb4855`, with a test that pins
   it): a Program gives each parameter leaf an `Input<w>_v1` gate of its width, a Boolean program function gets `Input1_v1`, and the purity
   check accepts it. So don't add `Input32_v2`. In the PR body, record that `Input16_v1` and `Input32_v1` stay as they are, for that
   reason, and that `WorkloadRequest_v1` is structural (as before).
2. **The embedding at served size.** `Embedding_v2{V=49152,H=576}` as one Call would make partition verification build a 1.36G-gate
   graph, while 576 root Calls of `GatherBf16x49152_v2` make a 2.36M-gate one. Keep the hot-swap constraint: the committed identities stay
   the word Program's.
   - If the word Program commits the embedding's 576 outputs as one Call's outputs, keep one Call with the pinned partition, since the
     460-unit re-check only evaluates units.
   - If a partition or circuit-check step has to build the whole graph, emit the 576 gather Calls as long as the committed identity set
     doesn't change, and say which you did in the PR body.
3. Casts at a glance: `Bf16ToF32_v2` (0 ANDs), `F2fpBf16_v2` (66), `GatherBf16x49152_v2` (786,688 ANDs, one 16-bit unit at served size, no
   violations), `Embedding_v2`. circuit-check is green with `--as-call`.
4. Several family branches edit `AGENTS.md`'s module map. Expect small conflicts there when merging, and keep every line.
