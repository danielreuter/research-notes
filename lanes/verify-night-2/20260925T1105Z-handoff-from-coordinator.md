---
lane: verify-night-2
kind: handoff
from: coordinator
created: 2026-09-25T11:05Z
---

# Next: verify b-ligero-standard-hash's instance-equiv/v1 artifacts for the x4 sets when they arrive; then the +sha256 x4 cells

The 4090 +blake3 x1 plateau is now a cleared Table 2 cell (1.2e8x). The x4 cells you accepted (017a7069, 6b6d4484) are
blocked only by rule I: the renderer needs a verified `instance-equiv/v1` artifact per x4 instance ref. b-ligero-standard-hash
will register them; please verify them (`verified=accepted`) as soon as they arrive. The +sha256 x4 cells from
b-ligero-sha256 go after that, from main 767115db.
