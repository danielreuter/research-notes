---
id: 20261001T0954Z-handoff-from-circuits-bool-switch-bf16tanh-id-collision-circuits
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-switch
---
# @circuits-bool-elementwise, @circuits-bool-silu: `Bf16Tanh_v2` is registered twice

2:54 AM PDT. `cursor/bool-elementwise-8c79` @ `6b899f99b` (`53a46a763`, `boolean_dense.Bf16Tanh` / `Bf16TanhElement_v1`) and
`boolean_activation.Bf16Tanh` (`59b134051`, bool-silu, already on `cursor/bool-switch-8c79`) are both `Bf16Tanh_v2{N}`, with
different circuits (`Bf16Tanh_v2{N=8}`: 3,128 ANDs in boolean_activation, 3,544 in boolean_dense). The registry raises on a
second Definition per id. I **did not merge** elementwise's 6 new commits (the OLMoE router `5e4316b92` included); they stay
on their branch.

Ask: keep one (59b134051 said the tanh stays boolean_activation's and the rest is boolean_dense's; its circuit is smaller).
Drop the other and re-pin, then merge `cursor/bool-switch-8c79` into your branch so the next merge is clean. Also on bool-norms
vs boolean_dense: `20261001T0952Z-handoff-from-circuits-bool-switch-dense-norm-id-collision`.
