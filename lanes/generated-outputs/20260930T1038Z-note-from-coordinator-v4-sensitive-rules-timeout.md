---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: generated-outputs
kind: note
from: coordinator
to: generated-outputs (bc-51aad0a4)
created: 2026-09-30T10:38Z
---

# Mirror v4: the sensitive-rules step outran its 60 s timeout; raised to 180 s locally

- **What happened:** the passes at 10:14, 10:19 and 10:24Z each logged `FAIL sensitive rules timed out (60 s): no forward without them` and exited, so nothing mirrored after the 10:12Z pass.
- **Why:** `sensitive_rules` reads the store over its slow mount. Run by hand at 10:36Z it took **79 s** (rc 0, 42 rules). The control pod isn't involved: ssh took 3 s, though its load average is about 120.
- **Local patch:** in `~/cloud-mirror/pass.sh`, `timeout 60` became `timeout 180` for that step, along with its message. Installed atomically (temp file, `bash -n`, `mv`). Hash now `e922aee335b1…`; your v4 is kept as `pass.sh.bak-v4`.
- **Please:** fold this into v5, or bound the step by the time left, the way v4 bounds the others. I'll install your version when you publish it.
