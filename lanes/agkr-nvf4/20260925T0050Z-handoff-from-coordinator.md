---
lane: agkr-nvf4
kind: handoff
from: coordinator
created: 2026-09-25T00:50Z
---

# Statement rewrites are under red-team (lane red-team-lk); new cells on them are held out of Table 2 until it passes

User decision (5:48 PM PT): results whose A-GKR statement uses a rewrite (merged/tagged LK, depth-1 flatten, BOOL_QUADRATIC,
PAIRED queries) enter Table 2 only after verify-po AND red-team-lk pass; verify-po holds the label until then. Keep registering and
handing them to verify-po as usual. Answer red-team-lk's questions quickly; if it finds a hole, stop building on that rewrite.
