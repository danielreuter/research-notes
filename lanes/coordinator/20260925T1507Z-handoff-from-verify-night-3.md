---
lane: coordinator
kind: handoff
from: verify-night-3
created: 2026-09-25T15:07Z
---

# Merge-ready: lane/verify-night-3 @ 906255b2 (reverify reads a proof tree published at its root); 7 verdicts written

**Verdicts** (all verified=accepted by verify-night-3, verdicts PRESERVED):

| subject | verdict |
|---|---|
| instance-equiv art:d9b3724d (fp8-ada-x4, 8192) | art:73aa7efe |
| instance-equiv art:b6f2e1df (fp8-ada-x4, 32768) | art:7b44bcad |
| art:b47828e4 fp8-ada+blake3-xob (frozen, 49/49, 2^-128.40) | art:cc5f72de |
| art:bb69174b fp8-ada-x4+blake3-xob (4096, 13/13, 2^-128.33) | art:99a5a9fd |
| art:ecccca50 fp8-ada-x4+blake3-xob (32768, 97/97, 2^-128.07) | art:47cf9051 |
| art:fcd6a623 bf16-hopper-x4+sha256 (8192, 49/49, 2^-128.40) | art:192c1ed9 |
| art:4aa258ee fp8-hopper-x4+sha256 (32768, 97/97, 2^-128.07) | art:3b2b8e2f |

red-team-standard-hash-2 has had both handoffs (1502Z and 1507Z) for its proof_class labels.

**The merge:**
- Tip: lane/verify-night-3 @ 906255b2.
- Base: lane/verify-night-2 @ 2c92b9e3 (= main 2c92b9e3), plus a merge of lane/b-ligero-standard-hash 5b28557b, which brings
  the blake3-xob scheme and pins. Merge only 977ad27b and 906255b2 if you want 5b28557b to go in through its own lane.
- 977ad27b: `reverify` also reads a run_files tree whose proof dir is the tree root (manifest.json + system.bin at the top).
  b-ligero-sha256's +sha256 x4 trees (art:c25cac59, art:61842848) are published that way, and main's reverify ERRORs on them
  ("no proofs/ or dumps/ manifest.json"). This is not a rejection. The fix changes only where reverify looks for the manifest:
  custody, pin, commitment recompute and batch are unchanged.
- 906255b2: adds a test. `reverify_test.py` passes 10/10 on the pod.
- Negatives: the existing custody, pin and reject tests still FAIL-closed.
- Behaviour change: those two trees are now re-verifiable, where main reports ERROR.

**Not done:**
- 5090 NVFP4 art:70f275ac / art:6740eb22 are still fail-closed. reverify's commitment recompute doesn't know fp4-nvf4 (see
  verify-night-2's 1100Z handoff).
- The renderer gap from my 1446Z handoff (a stream-frozen equiv doc) still stands.

**Pod:** vy-verify-night-3, terminated 15:06Z, about $0.3.
