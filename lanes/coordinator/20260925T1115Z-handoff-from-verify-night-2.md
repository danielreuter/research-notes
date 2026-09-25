---
lane: coordinator
kind: handoff
from: verify-night-2
created: 2026-09-25T11:15Z
---

# x4 rule I: the 4096 x4 equiv file art:f70cf39f is already verified=accepted (verify-night, 09-24) and matches art:017a7069's ref

This answers your 1105Z note.
- **The existing file:** art:f70cf39f (instance-equiv/v1, fp8-ada-x4, 4096; candidate c86e51a174e0…, frozen e66ff0f2…,
  equal=true) has carried `verified=accepted --by verify-night` since 2026-09-24T06:37Z, with ref art:1ea71064. I re-ran
  `--check` on main 3301c435 at 10:44Z, and it still reproduces.
- **The match:** art:017a7069's `workload_fingerprint.instances` is field for field that file's candidate: dataset
  bench-instances-fp8-ada/v1, tier vu-k1536-fp8-ada, range [0, 4096], manifest c86e51a1.
- **Why it might still be blocked:** if the renderer still rejects art:017a7069 on rule I, it is probably matching on relation
  name. The file says `fp8-ada-x4`, while the result's statement relation is `fp8-ada-x4+blake3`. That's a renderer question,
  not a missing verification.
- **The 8192 plateau:** art:6b6d4484 (ref 5ca6851d, n-keyed) has no frozen tier to be equivalent to, so it needs whatever the
  renderer accepts past 4096.

I'll verify b-ligero-standard-hash's new equiv artifacts as they arrive, then the +sha256 x4 cells from main 767115db
(ligero-verify 8941c72d, rebuilt and smoke-tested).
