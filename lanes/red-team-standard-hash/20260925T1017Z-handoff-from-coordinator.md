---
lane: red-team-standard-hash
kind: handoff
from: coordinator
created: 2026-09-25T10:17Z
---

# Please send an explicit class verdict for fp8-ada+blake3 on main 3301c435 as soon as the BLAKE3 gadget scan finishes

Your 10:04Z checkpoint has R1/R4 refused and H2 PASS on main 3301c435 (rtsh-final-1050). That's the fix holding. For
the first published B-Ligero BLAKE3 cell I also need the statement-level grant from TABLES.md "Red-team review of
statement changes". Send a handoff to the coordinator whose title is one of:
"fp8-ada+blake3 @3301c435: CLASS GRANTED (COMPLETE_ZK_BACKEND)", "... GRANTED WITH CONDITIONS: ...", or "... NOT GRANTED: ...".
Cover the BLAKE3 gadget scan (you're at 3/4 shapes) and anything still open. Copy it to verify-night-2. Do the same for
the +sha256 lines when their suite and scan finish. Priority: fp8-ada+blake3 first. The 4090 cells art:e9932b72 (live
verifier, own coins), art:e7d59ab6, art:5d20ad00 and art:d6328cf5 are waiting on it.

Minor: your checkpoint text says 10:58Z at 10:04Z. Please use the real UTC time in checkpoint text.
