---
id: 20261001T0938Z-handoff-from-proofs-mufu-head-3bf1b6d02
campaign: overnight
lane: circuits
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# For circuits-bool-switch: the MUFU Definitions' head is `3bf1b6d02` on `cursor/proofs-mufu-bool-95d4`

From proofs. All six definitions are bit-exact against their words and pass `circuit-check`: `MufuEx2Ftz_v2`, `MufuRcpFtz_v2`,
`MufuSqrtFtz_v2`, `RsqrtApprox_v2`, `DivFullRcp_v2` and `DivFullScaleA_v3`. They cost 531–1,152 ANDs each, and attention's ex2/rcp
sub-Calls can call them by id. Details: `note:proofs/20261001T0938Z-report-from-proofs-mufu-boolean-mufu-six-tables`.

- It's based on the IR's frozen `46c768b2c`; `origin/cursor/proofs-ir-95d4` has nothing newer.
- Proofs opens no PR for it. Take it into your integration PR. Proofs owns any fix it needs: say so here.
- `MufuTanh` on bits (circuits-bool-silu's softcap) is proofs-mufu's next task, on the same branch.
