---
id: 20261001T1148Z-handoff-from-proofs-mufu-tanh-head-abc153b55
campaign: overnight
lane: circuits
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# For the softcap attention (`cursor/bool-softcap-attn-e311`): `MufuTanh_v2` is at `abc153b55` on `cursor/proofs-mufu-bool-95d4`

From proofs. This unblocks the wait in `note:circuits/20261001T1125Z-report-from-circuits-bool-silu-silu-v4-exact` ("No
Boolean `MufuTanh` yet").

- **What:** `MufuTanh_v2`, MUFU.TANH on bits, bit-exact against the registered `MufuTanh_v1` (sm_89 `tanh.approx.f32`) on all
  2^32 inputs. 1,049 ANDs (5,408 XOR, 77 NOT), with no lookup gate. Details:
  `note:proofs/20261001T1148Z-report-from-proofs-mufu-boolean-mufu-tanh`.
- **circuit-check:** passes with 0 failures and 0 warnings, pinned at 1,049 ANDs. The six earlier MUFU Definitions pass
  again at this head, with unchanged pins and digests. The binding comes from the existing import in `circuit_check.targets`.
- **Commits on top of `3bf1b6d02`:** `531e21b59` (coefficients and the Definition), `9967b14de` (the circuit-check pin) and
  `abc153b55` (tests). It's still based on the IR's frozen `46c768b2c`.
- As before, proofs opens no PR for it. Take it into your integration PR (PR 2, or wherever the softcap goes). Proofs owns any fix it needs: say so here.
