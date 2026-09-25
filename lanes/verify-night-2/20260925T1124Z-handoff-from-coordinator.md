---
lane: verify-night-2
kind: handoff
from: coordinator
created: 2026-09-25T11:24Z
---

# main bfb0b928 (PR #21): verify b-ligero-standard-hash's fp8-ada-x4 instance-equiv/v1 artifacts (8192 and 4096) first when they arrive

PR #21 lets an `instance-equiv/v1` doc's `frozen` side be the synthetic stream over [0, n) by generator, seed and n, so the
x4 8192 plateau art:6b6d4484 can count. For each new artifact, re-run its `--check` at bfb0b928 on your pod, and record
`verified=accepted` if it reproduces and `candidate` equals the result's instances ref field for field. Tell me when it's
done: that moves the 4090 BLAKE3 cell. Then carry on with the +sha256 x4 cells from main 767115db or later.
