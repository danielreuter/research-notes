---
lane: coordinator
kind: handoff
from: red-team-flock
created: 2026-09-25T22:25Z
---

# red-team-flock: proof_class=NON_ZK_PROOF written on the pure-Flock cells art:6d1295ed (H100 bf16-hopper) and art:d1961ba4 (RTX 4090 fp8-ada), and on route (a) art:3d7cbea2. Each named verifier commit is code-identical to the reviewed path.

## Equivalence
- **H100 art:6d1295ed** (prover r20260925-220115-3522, verifier r20260925-220103-b7c0) names commit **a6a6e548**:
  - The verifier run's own recorded source is a6a6e548, with verifier binary sha256 2192a14d.
  - At a6a6e548 the Flock tree has zero diff from e5d54118 (`backends/flock/live`, both Flock patches, the CUDA
    sources and patch scripts).
  - e5d54118 equals the reviewed d3e96304/48045063 bf16 statement path, except for the Link-gate `commit.is_none()`
    edit, which is equivalent when points > 0, and the `points == 0` branch for the CPU statement.
  - The bf16 digest is unchanged by 48045063.
- **4090 art:d1961ba4** (prover r20260925-215031-5d4e, verifier r20260925-214955-238b) names commit **d93ce18b**:
  - The verifier run's source is d93ce18b, with verifier binary sha256 1350ddf2, the same binary as the art:949bcc35
    verifier.
  - The Flock tree has zero diff from e5d54118, so the path is equivalent to the reviewed 48045063 fp8 layout.
- **Both:**
  - lowering sha256 = PINS (da1bbe2c for bf16-hopper, e66262a0 for fp8-ada);
  - 6 of 6 timed sessions in each verifier run are accepted, exchange mode, gated, with Σ equal to the result's
    (4feab7cf… and 04f57c9d…);
  - one proof per batch point, so the reported union is 2^-195.44.
- **Note:** the result's `software.backend.binary_sha256` (dc0a66b4… and 305eeba4…) is the GPU prover binary. The
  verifier binary sha lives in the verifier run's `out/binary.sha256`.

## Route (a)
art:3d7cbea2 supersedes art:4b52879f (route-a-live's 2225Z request). It's the same runs (r20260925-201056-1018 /
-195835-65ab), NON_ZK_PROOF, bound 2^-130.19, live prime coins (3,006 rounds). The envelope changed only (protocol, sweep,
commit.seconds). Labelled under the 21:25Z grant.

art:77411c93 is route-a-live's later re-registration of the same runs. It adds `live.loopback_round_seconds`, and the
class and bound are unchanged (NON_ZK_PROOF, 2^-130.19, 3,006 live prime rounds). Also labelled `NON_ZK_PROOF`, at
22:22Z.

These class labels are independent of verify-flock-pure's `verified` replay labels.
