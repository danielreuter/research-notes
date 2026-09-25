---
lane: vllm-rf-c4irc
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T16:55Z
---
# main moved: 38a8d35d (b2vb ed8f6625, b5gmb 03e7b182, c2b 4d053f01 merged at about 16:40Z)

`origin/main` is now `38a8d35d`. It adds b2vb (one verdict, `properties/`, `check/commit_verdict.py` gone), b5gmb (the `check/match/global_match.py` split) and c2b up to `4d053f01` (Definitions to core `verity.ml`). Gate (b) base side is now **`38a8d35d`**; a base run at an older main no longer counts for a merge request.
**Bring main in by `git merge origin/main`** into your lane branch (no rebase, so no force-push needed), resolve, run lints, push. Merge commits in lane branches are fine.

## c4irc
`lane/vllm-rf-c4irc` (`26964de2`) and `lane/vllm-rf-c4ir` (`793f14af`) conflict with main in `tests/lint/allowlists/p10_size.json` only (b5gmb and c1 changed the ratchet). Code overlap is limited to `README.md`, `tests/lint/_imports.py` and `tests/program/padded_commit_tiny.py`.
- Finish gate (a) at `793f14af` as you are doing (tests 131..158 + custody); that evidence carries to the merged head for the analysis code.
- Then merge main into `lane/vllm-rf-c4irc`, resolve p10 from the merged files' real sizes, and re-gate on reg: lints + gate (b) head vs `38a8d35d` (same pod). The merge request will name `lane/vllm-rf-c4irc` at that head.
- After that, reg is **not** handed to b5vab automatically: tell the coordinator when reg is free, and the coordinator routes it.