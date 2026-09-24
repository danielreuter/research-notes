---
lane: vllm-retire-v1
repo: verity (~/projects/verity), worktree ~/projects/verity-wt/retire-v1
branch: lane/vllm-retire-v1 (off origin/lane/vllm-cleanup-2 = 815b837c), pushed to origin
---
# vllm-retire-v1: running state

Task: delete the v1 engine (required_manifest traversal/tables, required_values, ACQUIRE_CLASSES tables, ACQUIRE_ENGINE switch,
compiled_source v1 branch, sampled_replay v1 addressing, replay_partition v1 recompute, ENGINE=v1 paths) + prune census roots, cascade.

Baseline (staging 815b837c): 652 .py files, 209,413 lines under integrations/vllm; by-name allowlist 293.
Census: run with python3.13 (`/opt/homebrew/bin/python3.13 tests/dead_code_census.py`); python3.9 mis-parses commit_delta.py.
By-name lint: `/opt/homebrew/bin/python3.13 tests/test_no_by_name_rules.py` (pure AST, laptop-safe).

## Tip
- bda6f73a

## Done
- bda6f73a: ACQUIRE_ENGINE switch, v1_decision, gate v1 compare, plan class residuals, compiled_source v1 branch,
  commit_delta class-table extension, pod_match_v2.sh + match_compare.py (root dropped). Not yet run on a pod.

## Decisions / findings
- TP rank committers (tp/worker.py make_committer) have NO acquisition plan: they select by native_host's class tables.
  The plan has no rule for TP collective-site outputs, so switching TP to the plan is a design change needing a GPU TP Commit.
  => class tables + _select_modules KEPT (TP only); report as the one v1 survivor.
- verdict.py structural-leak notes name "native_host.ACQUIRE_CLASSES" / "required_manifest.members_for": left (verdict.json content).

## Next
- harness: ENGINE / BASELINE_ENGINE (resolver.py, manifest_digest.py), replay_partition v1 recompute
- sampled_replay v1 addressing (V1.members_for), then required_manifest.py + required_values.py + their tests
  (many tests build manifests with v1 build_manifest -> convert or delete)
- roots: drop GEN-lane runners (own commit, revertable); uncertain: canary.sh
- pod vyv-v2cpu3: ramlock /workspace/ramlock/retire-v1.json; staging + tip suites, harness T0+T1
