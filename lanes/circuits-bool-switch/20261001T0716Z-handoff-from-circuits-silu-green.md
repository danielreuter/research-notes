---
id: 20261001T0716Z-handoff-from-circuits-silu-green
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: SiLU is green (2/2). Merge `cursor/bool-silu-8c79` @ `2b2e176f8`

- **Definitions:** `SiluMulBf16_v3` (1,372 ANDs) and `SiluMul_v3{I}` (10,976 ANDs at I=8). They're pure Boolean with no word-id sub-Calls, and
  circuit-check is green (`--as-call --fail-on-warnings`).
- **Units:** `SiluMul_v3{I}` cuts into the same I units as `SiluMul_v1{I}`, so your sampled-unit comparison lines up one to one.
- The module is `integrations/vllm/verity_vllm/program/registry/boolean_silu.py`. It merges with elementwise in either order.
