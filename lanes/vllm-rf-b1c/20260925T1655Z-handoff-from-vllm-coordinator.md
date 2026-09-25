---
lane: vllm-rf-b1c
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T16:55Z
---
# main moved: 38a8d35d (b2vb ed8f6625, b5gmb 03e7b182, c2b 4d053f01 merged at about 16:40Z)

`origin/main` is now `38a8d35d`. It adds b2vb (one verdict, `properties/`, `check/commit_verdict.py` gone), b5gmb (the `check/match/global_match.py` split) and c2b up to `4d053f01` (Definitions to core `verity.ml`). Gate (b) base side is now **`38a8d35d`**; a base run at an older main no longer counts for a merge request.
**Bring main in by `git merge origin/main`** into your lane branch (no rebase, so no force-push needed), resolve, run lints, push. Merge commits in lane branches are fine.

## b1c
`0e954bf0` **conflicts** with main in `properties/admission.py` (b2vb), `tests/check/test_commit_verdict_{hopper_no_evaluator_gap,replay_seed_of_record,selector_no_evaluator_gap}.py`, `tests/check/test_sampled_replay_query_population.py`, and allowlists p03/p10/p11. b2vb deleted `check/commit_verdict.py` (its rules are in `check/commit_rules.py`, `check/c2_rules.py`, `check/verdict.py`); your challenge-module routing of the commit_verdict seed recompute and the difftest hunks must land in the new homes.
- Merge main before your re-gate, then lints + gate (b) head vs `38a8d35d` on b5pat-cpu (same pod). #67 on g2 is unaffected (it runs your pre-merge tree; say so in READY.md).