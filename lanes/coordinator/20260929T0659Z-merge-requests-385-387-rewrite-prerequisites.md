---
lane: coordinator
kind: handoff
from: fixture-process (bc-dc2611ba)
to: research coordinator (bc-8ece7cde)
created: 2026-09-29T06:59Z
---

# Merge requests: #385 (HEAD scrub, ``) and #387 (commit maps, ``), the rewrite's steps 3d and 5; please record `check` on each

Both are on `main` `84560ab7`, touch only `tools/research`, `tests/test_repository.py` and `backends/sp1/tcdot` (nothing under
`backends/flock/`, so no `lean-agreement`), and neither changes a pin or a statement. Take them after #366 (`f4af1cf4`).

1. **[#385](https://github.com/danielreuter/verity/pull/385)**, `cursor/head-scrub-c4a4`, head ``: the tree names neither the R2
   account id, nor the bucket name, nor the personal email.
   - `store.pod.toml` takes the bucket and endpoint from the environment and pins the bucket by `bucket_sha256`. The cloud-VM
     fallback compares the digest.
   - **Behavior change:** a pod pointed at `store.pod.toml` now also needs `--env R2_BUCKET=... --env R2_ENDPOINT=...`. Custody
     runs are unaffected, since they stage their own store.toml.
   - `test_no_secret_like_literals` now fails on an R2 account endpoint.
   - The sp1 patches use the noreply address. Both fork arms reproduce `FORK_TREE` and `FORK_TREE_WIT` exactly.
   - Local `suites.py research repository verity-sp1 --fresh` passes.
2. **[#387](https://github.com/danielreuter/verity/pull/387)**, `cursor/commit-map-tooling-c4a4`, head ``: `research.commitmap`.
   - The gate reads a passing check of an old commit for its image only through an accepted `commit-map/v1` (label
     `commit_map=accepted` by `daniel`), and only when the tree is unchanged (the map's flag and the attempt's recorded tree).
     It refuses a REF that holds replaced commits.
   - Adds `research git old2new|remap|check|build`.
   - **Behavior today:** unchanged, since no map exists.
   - Local `suites.py research repository tools/check --fresh` passes.
   - The queue's grant and admission hooks are proposed to the merge-queue lane (`lanes/merge-queue/`). Please forward it to
     bc-605d7c89 if it doesn't watch that folder.
   - One-line conflict with #368 in `test_store_vocab.py`'s `VERIFICATION_KEYS`, for whichever lands second: keep both keys.

The rewrite's one remaining prerequisite is step 2, the secret scan of every ref's history. No pod spend of mine.
