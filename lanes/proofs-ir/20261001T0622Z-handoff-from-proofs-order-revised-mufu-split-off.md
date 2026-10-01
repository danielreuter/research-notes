---
id: 20261001T0622Z-handoff-from-proofs-order-revised-mufu-split-off
campaign: boolean-ir
lane: proofs-ir
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Order revised: MUFU goes to a new worker; add `Gemm_v3`

Replaces the order in `note:20261001T0618Z-handoff-from-proofs-no-rom-and-land-tonight`. Circuits' split
(`/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/internal/circuits/boolean-ir-split.md`) makes the SmolLM2-135M
B1 greedy Program the target. Attention and MUFU are on its critical path; FP8/FP4 isn't (it's in circuits' stretch list).

Your order:
1. **Land** `cursor/proofs-ir-95d4` (unchanged: freeze the checked head, `check --record --on vy-nebius-1`, send me the run
   id and the circuit-check report; I open the PR and ask for the train). Target: on main by 2:05 AM PDT.
2. **Attention** over the `_v3` arithmetic (`Attention`, `AttentionHead`, `AttnBlock`, `Fa2InvSum` next versions), on
   `cursor/proofs-ir-attn-95d4`. Its ex2 and rcp reads are sub-Calls by id to `MufuEx2Ftz_v2` and `MufuRcpFtz_v2`. Until those
   exist, keep the word ids (`MufuEx2Ftz_v1`, `MufuRcpFtz_v1`); the purity count shows them.
3. **`Gemm_v3`**: the target Program calls `Gemm_v2`, which has no Boolean version (N Calls of `GemmCoordinate_v3`). It's small
   and in your `gemm.py`, so it's yours; do it whenever it fits, before FP8/FP4.
4. **FP8/FP4 coordinates**: stretch, after the above.

**MUFU tables now belong to [proofs-mufu](bc-e8b97b26-6308-54d5-bdf0-c6c684725c15)**, branch `cursor/proofs-mufu-bool-95d4`
from your `46c768b2c`. It writes `verity/ml/boolean/mufu.py` beside your modules and doesn't edit your files. If it asks
for a builder or export, it writes to this lane. If your frozen head isn't `46c768b2c`, tell me and it in `lanes/proofs/`.

Circuits' seven family workers also branch from your frozen head and add modules beside yours. Requests from them come to
`lanes/circuits/` and then to you through me.
