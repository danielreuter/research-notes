---
lane: coordinator
kind: handoff
from: red-team-flock
created: 2026-09-26T01:20Z
---

# red-team-flock: art:167e64a8 (A100 bf16-ampere, keyed-BLAKE3 Flock) is labelled NON_ZK_PROOF. The flock-vllm-block/v1 review was already finished at 00:15Z, with art:56f792bd labelled.

- **art:167e64a8** is covered by the bf16 layout grant (23:20Z). AM1 is met: pin e97ecb9e, which the result records.
  - Its verifier commit e52eca82 is a6a6e548, the reviewed path, plus the stateless Ping; there's no other
    `backends/flock` change.
  - The verifier ran on vy-flock-backend-ver9, a separate pod from the prover's vy-flock-backend-a100c.
  - It is 1 proof at 4,096 VUs, 2^-195.44.
  - The plateau Σ (254070ca…) has 6/6 sessions in exchange mode with the gate on.
  - Labels written: `proof_class=NON_ZK_PROOF` and a `finding`.
- **flock-vllm-block/v1 (PR #41 @ ff1c1e3f):** already done. See `20260926T0015Z-handoff-from-red-team-flock.md`:
  GRANTED WITH CONDITIONS, with `proof_class=NON_ZK_PROOF` on art:56f792bd since 00:05Z. That covers the statement code,
  the verifier, the `VllmCircuit` fold, the CPU selftest (21/21 at 8 and 64 VUs) and the Rust vector tests (6/6),
  art:c30bb647. The only open item is hardening VL1 (recompute the a/b roots natively). verify-flock-pure's acceptance
  covers PB3.

## Also labelled: the next-publish re-runs from flock-backend's 00:03Z handoff
- **art:c3e83404** (H100 fp8-hopper, keyed-BLAKE3): verifier e52eca82 on vy-flock-backend-ver8, prover on h100d. 1 proof
  at 16,384, 2^-195.44. 6/6 sessions.
- **art:7afeecbe** (RTX 4090 fp8-ada): verifier e52eca82 on ver4090c, prover on 4090c. 1 proof at 4,096. 6/6 sessions.

Both are labelled `proof_class=NON_ZK_PROOF` plus a `finding`. The earlier registrations art:bb289d47, ed0047be,
37215309 and fb526e50 (from the 23:48Z handoff) are superseded, so I didn't label them.
