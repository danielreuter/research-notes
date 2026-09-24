---
id: vllm-rf-f3/state
lane: vllm-rf-f3
kind: state
status: active
created: 2026-09-24T17:36Z
---
# vllm-rf-f3: undeclared inputs (D3, D4, D14, D15) (state)

- **Brief:** `~/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md`; plan `SYNTHESIS.md` §2 (D3, D4, D14, D15), §4 P7; coordinator note `20260924T1645Z-coordinator-checks-on-observe-survey.md`.
- **Worktree:** `/Users/danielreuter/projects/verity-wt/rf-f3`, branch `lane/vllm-rf-f3` from `72884c8a`.
- **Scope:**
  - D3: one declared `layout` parameter (Commit config / CLI flag, recorded in artifact), read once at process start, inconsistent values refused; roots unchanged where the two env vars agreed.
  - D4: `GATHER_FLUSH_LEAVES` / `PRE_FLUSH_LEAVES` into a torch-free module, delete the ImportError fallback in `acquire/plan.py`, test plan + digest identical with torch stubbed.
  - D14: seeds defaulting to 0 become required or derived from commitment; list every challenge derivation touched.
  - D15: env-driven Definition semantics (MufuTanh tables etc.) -> package data with pinned digest; list every env-dependent Definition. STOP and report if a fix would change a digest because the env path was actually used.
- **Acceptance:** gates (a), (b); torch-stub plan test; D3 GPU Commit row re-run with roots == regression record; no Program/manifest digest changes.

## Done
- 17:36Z worktree created.

## Running
- nothing yet

## Next
1. Read code at the defect sites; inventory env reads, seeds, env-dependent Definitions.
2. Implement D4, D3, D14, D15 as separate commits.
3. CPU pod: gates (a)/(b) (+ base measurement if a1 baseline.md absent).
4. GPU pod: one Commit row re-run for D3, compare roots with regression record.

## Open questions
- none yet

## Found, not fixed
- none yet
