---
lane: coordinator
kind: handoff
from: verify-night-3
created: 2026-09-25T14:46Z
---

# x4 instance-equiv/v1 art:d9b3724d (8192) and art:b6f2e1df (32768): verified=accepted (verdicts art:73aa7efe, art:7b44bcad)

- `instance_equiv --check` at lane/verify-night-3 a5d9b632 (= main 2c92b9e3, PR #21 in, + 5b28557b) on pod vy-verify-night-3
  (run r20260925-144140-d25e): both reproduce every field (producer tags lane/provenance dropped first), equal=True.
- candidate == the results' instances ref field for field: 8192 manifest 5ca6851d (art:6b6d4484, art:19be6afa); 32768 manifest
  fd076a29 (art:ecccca50).
- **Renderer gap:** `tables._equiv_content` at 2c92b9e3 still requires `frozen == FROZEN_INSTANCES[target]` ([0, 4096]) and
  flags both docs on that one point, so the x4 8192 plateau still won't count until the renderer admits a stream-frozen doc.
  Your call.
- Queue item 3 (H100 +blake3 table rows c8730574 / 7c6b4647 / 9c11326c / 7a3965da) was already verified=accepted by
  verify-night-2. 5090 NVFP4 art:70f275ac / art:6740eb22 stay fail-closed: reverify's `committed_trees` still has no fp4-nvf4
  at 2c92b9e3 (needs a main change, as verify-night-2 said at 1100Z).
