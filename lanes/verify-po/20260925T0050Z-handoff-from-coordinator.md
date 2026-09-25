---
lane: verify-po
kind: handoff
from: coordinator
created: 2026-09-25T00:50Z
---

# HOLD the verified=accepted label on A-GKR results with rewritten statements until red-team-lk passes (user decision 5:48 PM PT)

- agkr-fp8's 4090 cell art:45c5be4a (0.490 s, merged LK table, handoff 20260925T0045Z): verify it as requested and register the
  verification-verdict/v1, but do NOT write the `verified=accepted` label yet. The renderer would put it into Table 2 at once;
  the user wants it out until both you and red-team-lk pass. I will send "release" when red-team-lk passes.
- Same rule for any further A-GKR result from agkr-nvf4 or agkr-fp8 whose statement uses a rewrite red-team-lk is checking
  (merged/tagged LK, depth-1 flatten, BOOL_QUADRATIC, PAIRED queries): verdict yes, label held.
- Already-labelled cells stay as they are (the 5090 cell art:49757870 stays in Table 2, marked provisional by me).
- A-GKR results on unchanged statements, and B-Ligero / SP1 results: label as usual.
