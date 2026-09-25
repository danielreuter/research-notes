---
lane: vllm-rf-b4c
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T16:55Z
---
# main moved: 38a8d35d (b2vb ed8f6625, b5gmb 03e7b182, c2b 4d053f01 merged at about 16:40Z)

`origin/main` is now `38a8d35d`. It adds b2vb (one verdict, `properties/`, `check/commit_verdict.py` gone), b5gmb (the `check/match/global_match.py` split) and c2b up to `4d053f01` (Definitions to core `verity.ml`). Gate (b) base side is now **`38a8d35d`**; a base run at an older main no longer counts for a merge request.
**Bring main in by `git merge origin/main`** into your lane branch (no rebase, so no force-push needed), resolve, run lints, push. Merge commits in lane branches are fine.

## b4c
`5c05ff6d` merges **cleanly** with `38a8d35d`, but main (b2vb) also changed `verity_vllm/pipeline/commit.py` and `tests/lint/_imports.py`, which you change. So re-gate the merged tree, not `5c05ff6d`:
- Create `lane/vllm-rf-b4c` = `git merge origin/main` on `5c05ff6d`, push. Gate that head: lints, gate (b) head vs `38a8d35d` on b4b-cpu (same pod), #101 on b4b-g1.
- Tell `vllm-rf-b5vab` your new head in a handoff: it stacks on it and uses your head XML as its gate (b) base.