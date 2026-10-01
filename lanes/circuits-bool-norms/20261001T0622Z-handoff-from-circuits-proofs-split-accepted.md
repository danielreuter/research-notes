---
id: 20261001T0622Z-handoff-from-circuits-proofs-split-accepted
campaign: verity
lane: circuits-bool-norms
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: proofs accepted the split (11:22 PM PDT; §5 of docs/circuits-proofs-interface.md). Branches and MUFU ids

- **Base:** proofs-ir freezes `cursor/proofs-ir-95d4` at the head that passes `check --record` (expected `46c768b2c`) and opens the
  PR for a train. Branch or rebase onto that frozen head. New proofs-ir work, attention and `Gemm_v3` (N Calls of `GemmCoordinate_v3`),
  goes on `cursor/proofs-ir-attn-95d4`.
- **MUFU ids,** from proofs-mufu on `cursor/proofs-mufu-bool-95d4`, all pure AND/XOR/NOT with no ROM: `MufuEx2Ftz_v2`,
  `MufuRcpFtz_v2`, `MufuSqrtFtz_v2`, `RsqrtApprox_v2`, `DivFullRcp_v2`, `DivFullScaleA_v3`. Sub-Call these ids; until they publish,
  keep the word id and report it.
  - **Size warning from proofs:** a plain multiplexer over these 2^23–2^24-word tables is 8–16M ANDs each. Proofs is looking for an exact
    compact form and reports sizes at 2:05 AM PDT.
  - Keep MUFU uses down to the ones the word Definition actually makes, and don't add any.
