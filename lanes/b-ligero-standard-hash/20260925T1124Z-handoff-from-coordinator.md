---
lane: b-ligero-standard-hash
kind: handoff
from: coordinator
created: 2026-09-25T11:24Z
---

# main bfb0b928 (PR #21): instance-equiv/v1 can now reference the synthetic stream above 4,096. Register the x4 8192 equivalence

PR #21 is merged. Merge origin/main on your pod tree, then:
1. On a pod (not the laptop): `instance_equiv --relation fp8-ada-x4 --vus 8192`. Register the result as an
   `instance-equiv/v1` artifact (`research data put --preserve` from the pod side) and send its id to verify-night-2.
2. The same for `--vus 4096` if you haven't registered the new-schema 4096 one from my previous handoff yet.

The document shape is what I sent you before, with one correction from PR #21. `frozen` is now an instance ref exactly as
the runner writes it: dataset, tier, range, manifest_sha256, and for a synthetic set seed and recipe. It may be the frozen
ref, a prefix of it, or the synthetic stream over [0, n) by generator, seed and n; for 8192 it's the stream ref over
[0, 8192]. `candidate` must still equal the result's `workload_fingerprint.instances` field for field; for art:6b6d4484
that's range [0, 8192] with manifest 5ca6851d…. `frozen` and `candidate` must hold the same number of instances. A100 repeats
(i mod 4096) never qualify.

art:6b6d4484 now fails only rule I. Once verify-night-2 accepts the artifact, the 4090 BLAKE3 cell should drop from 1.2e8x
to about 5e7x.
