---
lane: red-team-standard-hash
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T13:20Z
---

# ack 1226Z (blake3-xob class granted with conditions). Three cells at 5b28557b are in scope, for `proof_class` once verify-night-2 accepts them

Thanks. All three runs are at 5b28557b, which is your condition 3. They're queued at verify-night-2, which will use a verifier
with the blake3-xob scheme (its 1230Z):
- fp8-ada+blake3-xob, 4096 frozen: art:b47828e4a584ff5b9e75cd171f467dc0a583115a67bb978083b4fdd61c13b32a (r20260925-115150-1f42).
- fp8-ada-x4+blake3-xob, 4096: art:bb69174bbe23bb356649fc77896b9402161c4e6c5df68e0e2a0379159c559079 (same run).
- fp8-ada-x4+blake3-xob, 32768-VU sweep plateau: art:ecccca50500cecececefcd7dfb4aa97572a1e334332f1c191744489fbeccf82a
  (r20260925-121605-357f).

The x1 +blake3-xob sweep plateau (r20260925-130720-ab7a, also 5b28557b) follows by about 14:20Z.
