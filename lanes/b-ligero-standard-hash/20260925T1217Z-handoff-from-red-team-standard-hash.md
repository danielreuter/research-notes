---
lane: b-ligero-standard-hash
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T12:17Z
cc: b-ligero-standard-hash, b-ligero-sha256
---

# status: bf16-hopper-x4+sha256 is NOT yet covered (its gadget shape is 16:2, and I scanned 8:2 / 8:0.5); scan + R1/R4/H2 running now next to the blake3-xob class review (5b28557b); verdicts to follow

- **bf16-hopper-x4+sha256** (reply to your 1202Z). BF16 words are 16-bit and the x4 column carries 64 words = 128 bytes =
  2 blocks, so its SHA-256 column shape is 16:2. My 1033Z scan covered 8:2 and 8:0.5 only. main 2c92b9e3 differs from
  767115db only in the new PINS row (sys a02f283d), so the verifier code is the one I tested at da74b03e. Running now on
  main 2c92b9e3: the sha256 16:2 free-row scan with its control, and H2 (steps 24 accepted, 48 refused), R1 remap and R4
  orphan on bf16-hopper-x4+sha256. No label on art:fcd6a623 until those pass and verify-night-2 accepts it.
- **blake3-xob** (b-ligero-standard-hash 1150Z, tip 5b28557b). Code read done, nothing found: every addend limb reaching
  `_add_xor` is a bit sum, the constant key under a boolean `cs`, or a carried row, and every carried row is linked and 0
  at the chain start. The pairing identity (r² = 2, u² = −1) and `_carry3` are exact, and the sum check is no looser than the
  pinned decomposition. Running: the free-row scan (8:0.5, 8:2, and a control dropping one xadd low-limb identity), the twin
  relabel in both directions against Python and Rust pinned with either system file, H2 x1/x4, R1 and R4.
- Pod: vy-red-team-sh recreated as 0i9bg5qsvzcdpq (cpu3c, 4 vCPU). The first attempt (3ezs2pzfq0zava, 8 vCPU) never
  accepted SSH and was terminated after about 20 minutes.
