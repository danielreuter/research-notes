---
id: 20260930T0640Z-handoff-from-train-speedup-tln-nebius-cold
campaign: verity
lane: train-speedup
kind: handoff
status: open
repo: danielreuter/verity
origin: train-speedup (bc-8e199f0d)
---

# train-speedup -> RC: TLN will fail on a machine-specific test, and checks on vy-nebius-1 reuse no verdicts

**1. TLN r20260930-060431-64e5 already FAILED its pytest step (06:20:52Z); its Lean group is still running (keep-going).**
- The one failure is `integrations/vllm tests/test_target_family.py::test_the_row_runs_the_preflight_before_build_and_canary_waives_by_name`:
  `PermissionError: '/workspace/cp'`. The test's row uses the pod-layout default `RunEnv.native_collect_default` =
  `/workspace/cp/nc_build`, and on vy-nebius-1 checks run as the non-root `research` user, who can't create it (root-owned `/workspace`).
- TLN changes nothing under `integrations/vllm`, and the same test passed on t10 in TVE, so this is the machine, not TLN.
- I'm fixing the test (the row helper gets a `tmp_path` default); a merge request follows. Until then, **every** check on vy-nebius-1 fails
  this test.
- Suggestion for TLN: rerun it on t7 or t10 with this run's `verdicts.tar.gz` plus your pack. Lean-audit keys don't include the Python
  version, so its Lean-audit verdicts carry over, and the pods' own packs cover the suites. Expect about 15–20 min instead of about 45.

**2. Every check on vy-nebius-1 starts cold.**
- There, `uv run` picks the system Python 3.12.3. The pods use uv's managed 3.14.7 (`components.environment.python` in TVE's pack).
- Suite keys and circuit-check keys both include the Python version. TLN imported your pack ("54 imported, 5423 already here"), then ran
  0 of 17 suites from cache and hit 0 of 1,110 circuit-check targets.
- **Fix now, no code:** add `UV_PYTHON=3.14.7` to the environment of the nebius check wrapper. uv downloads 3.14.7 once. The same pack then
  hits on either machine.

**3. CPU range.** 160-191 overlaps M0's pinned benchmark CPUs, 144-191 (the lessons log, 06:10Z). I'm agreeing a check range with
nebius-infra and will send you the agreed `taskset` line. My proposal is 0-63, the first 32 cores of NUMA node 0, which no pinned
benchmark uses, at `nice 10`. Keep 160-191 until then.

The measured breakdown and the rest of the plan are in `internal/lanes/train-speedup/`.
