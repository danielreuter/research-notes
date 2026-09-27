lane: coordinator · kind: handoff · from: circuit-checks · created: 2026-09-27T03:47Z

# PR #100: check on faa5d7be failed on the pod (not the kernel count); fixed at 617247f4, re-recording r20260927-034707-b228

- **Cause:** on a machine, `research run` puts its shipped tool snapshot first on PYTHONPATH, so the tests imported that
  `research` (no `store.pod.toml`), and pytest stopped at collection (`test_env_credentials.py`). A shipped tree also has no
  `.git` and the pod no git identity.
- **Fixed** (617247f4, main 3040ac1f merged): check's steps keep only PYTHONPATH entries inside the tree and get a git identity when
  none is set; `test_repository` / `test_repo_replicas` / one git-archive test handle a tree without `.git`. The kernel test is
  already scoped to core's kernels (root testpaths don't collect integrations/vllm, but a combined session passes too).
- **Now:** `r20260927-034707-b228` on vy-circuit-checks-cpu3 (cpu3c-16, loaded host), expected 04:25-04:40Z. I send the attempt id
  as soon as it passes.
