---
cursor:
  subagentId: "bc-1a23b70c-8ce6-52de-9b80-c005acb94607"
---

lane: coordinator · kind: handoff (merge request) · from: pous (bc-1a23b70c, kernel tooling, for the pous project bc-b729c175) · to: research coordinator · cc: the sm_120 PoUW coordinator (bc-2aa33ad8), the harness owner (bc-0de2d624) · created: 2026-09-30T17:15Z · repo: danielreuter/verity

# Merge request: #491, the shared PoUW bench harness for sm_120

Daniel approved the kernel-tooling rollout at 16:17Z. Its first step (#583) stacks on this harness, and the kernel-engineering skill (#577, merge request 16:42Z) points every kernel lane at it. Today each timed run assembles its tree from several branches. With #491 on `main`, the lanes run the harness from `main`.

| PR | Branch @ head | Base | What |
|---|---|---|---|
| [#491](https://github.com/danielreuter/verity/pull/491) | `cursor/pouw-harness-sm120-d2f2` @ `73339a27` | `main`; merges cleanly onto `b1134766` (`git merge-tree`) | `benchmarks/pouw/harness/` (46 files, +18.8k): the arm interface, baselines (cuBLASLt autotuned, CUTLASS sm_120), interleaved timing with per-rep clocks, the dependent-chain decode, the SASS gate with pinned toolkits, the verify step |

- **Draft, and owned by the harness lane** (bc-0de2d624; opened by bc-2aa33ad8). This request doesn't change that. Please take readiness from its owner, or from bc-2aa33ad8 through the pous root, before you train it.
- **What it touches:** only `benchmarks/pouw/`. No `backends/flock/`, circuit, Lean or pinned-statement change, so no `lean-agreement`, `circuit-check` report or statement reviewer.
- **Tests:** `benchmarks/pouw/tests` passes at `73339a27` on my VM, 193 passed and 13 skipped (CPU, pytest-xdist). No `check` of `73339a27` is recorded that I can find.
- **The ask:** record `check` on `73339a27` (`tools/check/check.py --record --on MACHINE`, the CI pool) and add #491 to the next train. It waits on nothing.
- **What stacks on it:** [#583](https://github.com/danielreuter/verity/pull/583) (mine, draft).
  - It adds the attempt records (`kernel-attempt/v1`), γ from the Lean-pinned price twins, and poisoned dumps with a no-write control.
  - It fixes #491's two stale claims: the README's timed runs lacked `--timed`, and nothing in the harness poisoned outputs.
  - It lands after a one-day pilot, with a merge request of its own. It can go in the same train as #491 if its pilot finishes first.
- **#240** (the approach registry) already has a merge request: `lanes/coordinator/20260930T0345Z-merge-request-pous-approach-registry-240.md`, at `fe2260a7`, which is still its head. The Verity root's 09:30Z handoff lists it for a train, so I haven't refiled it. #577's "What's been tried" step needs its CLI on `main`.

Replies to `lanes/pous/`.
