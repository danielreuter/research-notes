---
lane: vllm-rf-gc
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T16:55Z
---
# main moved: 38a8d35d (b2vb ed8f6625, b5gmb 03e7b182, c2b 4d053f01 merged at about 16:40Z)

`origin/main` is now `38a8d35d`. It adds b2vb (one verdict, `properties/`, `check/commit_verdict.py` gone), b5gmb (the `check/match/global_match.py` split) and c2b up to `4d053f01` (Definitions to core `verity.ml`). Gate (b) base side is now **`38a8d35d`**; a base run at an older main no longer counts for a merge request.
**Bring main in by `git merge origin/main`** into your lane branch (no rebase, so no force-push needed), resolve, run lints, push. Merge commits in lane branches are fine.

## gc
`301ce7dc` merges cleanly (no shared files), but main changed tests (b2vb, b5gmb, c2b), so the base set of failures moved. Your running base run at `8a3aa083` (r20260925-163221-f7ab) serves triage only.
- Merge main into your branch, then gate (b) base at `38a8d35d` and head, same gb-cpu pod, and re-triage against the new base. Stop the `8a3aa083` base run now if it has more than ~15 min left, to save pod time.