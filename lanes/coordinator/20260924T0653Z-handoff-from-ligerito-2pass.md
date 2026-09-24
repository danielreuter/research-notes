---
from: ligerito-2pass (superseded instance)
to: coordinator
created: 2026-09-24T06:53Z
---
# ligerito-2pass resumed at 06:51Z after its stall, found itself superseded by ligerito-2pass-2, and changed nothing

- This instance stalled from about 03:10Z to 06:51Z. When it came back, the lane was already superseded (your 03:42Z checkpoint). Its worktree had been removed, and `lane/ligerito-2pass` was at 0f6cc311 (ligerito-2pass-2's e0c7acd2 + 0f6cc311 on top of my 59eb8df8).
- Neither of my pods (v1z7ar00oxtsw7 4090, 3t6j7vf13tnp57 RTX 2000 Ada verifier, both EU-RO-1) shows in `pods list` at 06:52Z. I did not terminate them myself, so they were terminated by someone else.
- My three merges (3cd354dd relation-2@498f9014 clean, ac2094dc sumcheck-3@58e76e5d clean, 59eb8df8 verify-rs-3@a87edaa0: ref.py = theirs v2, test_ref.py = theirs + 11b908c8 interop test) are in the successor's tip, as is my red-team retarget (committed as e0c7acd2).
- FYI: at 06:53Z, ligerito-2pass-2's report is still `open`, and its last checkpoint is 04:07Z. That is past the 06:30Z FINAL, so it may have stalled too.
- No writes to its branch, worktree or pods; no new artifacts; no FINAL written for ligerito-2pass (it is superseded).
