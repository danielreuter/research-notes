---
lane: vllm-rf-b5vc
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T16:55Z
---
# main moved: 38a8d35d (b2vb ed8f6625, b5gmb 03e7b182, c2b 4d053f01 merged at about 16:40Z)

`origin/main` is now `38a8d35d`. It adds b2vb (one verdict, `properties/`, `check/commit_verdict.py` gone), b5gmb (the `check/match/global_match.py` split) and c2b up to `4d053f01` (Definitions to core `verity.ml`). Gate (b) base side is now **`38a8d35d`**; a base run at an older main no longer counts for a merge request.
**Bring main in by `git merge origin/main`** into your lane branch (no rebase, so no force-push needed), resolve, run lints, push. Merge commits in lane branches are fine.

## b5vc
`e1dd2a7e` merges cleanly with main (no shared files). Merge main before your first gate; gate (b) base is `38a8d35d`. The a5-t1 / a5-g1 handover from a5c comes later than planned (a5c must re-gate after its own main merge); a5c will post its ETA to you.