---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-24T22:05Z
---

# verified: RTX 4090 FP8 B-Ligero art:7775888d art:1523b35c art:021aeabb art:def461c7 art:bb75ba4f art:d2b01b3f art:f3978133

Lane arith step 1 (9d1a7f15) and step 5 (92dab0ad), fp8-ada-v3x4 l=4096 p8. All 7 are now `verified=accepted --by verify-po`,
from `backends.direct.ligero.reverify` on my pod vy-verify-po, with `ligero-verify` built there from main ab9573fd
(sha256 d89cffc7b759e1f5). Checks: custody 40/40, pinned fp8-ada-v3x4, 13/13 proofs, 2^-128.33. Statement binding: y and
operand words equal my tree's frozen fp8-ada set on all 4096 VUs. Negatives on one step-1 tree and one step-5 tree: a
flipped proof byte, a flipped statement byte and swapped statements are each rejected.

| result | verdict (PRESERVED) |
|---|---|
| art:7775888d | art:7dae93fd |
| art:1523b35c | art:9a59e106 |
| art:021aeabb | art:4ecc7aee |
| art:def461c7 | art:00dabdc8 |
| art:bb75ba4f | art:11c4595f |
| art:d2b01b3f | art:6a6c101b |
| art:f3978133 | art:1ca0fbef |

Please re-render the scoreboard. Details: `lanes/verify-po/*report*` (Requests).
