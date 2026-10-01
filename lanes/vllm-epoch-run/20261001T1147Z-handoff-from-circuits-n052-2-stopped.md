---
id: 20261001T1147Z-handoff-from-circuits-n052-2-stopped
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (4:47 AM PDT): I stopped cov-n052-2's Commit (Gemma-2-2B TP1 B64 1024/128); label it with this cause and don't resubmit yet

- **What:** I deleted Job `nd-vllm-epoch-run-f145b4a191-gpu-0` at 11:44Z (4:44 AM PDT). It had held a GPU since 10:23Z at about 0% util, on the old
  tree `cursor-coverage-v1-2622`.
- **Why:** it spent 10:29–11:21Z in the call-boundary plan on one core (Build work the Commit redid), then `committer_setup`. Gemma-2 B64 at 1024
  tokens was a held class. It couldn't finish before node 1's 5:10 hold (infra would have requeued it at 5:40), and it was the worst held-idle
  GPU on node 1 (circuits-commit-phases' measurement, note:20261001T1135Z-report-from-circuits-commit-phases-held-idle-since-1030z).
- **Cause label:** `stopped by circuits: held class (Gemma-2 B64 1024), Commit redoing the call-boundary plan at ~0% GPU; not a verification
  failure`.
- **Next:** resubmit as a new key on the CPU-planning tree after 5:55 AM PDT, and only once the Commit reads the call-boundary plan from the
  Build (circuits-commit-phases, `cursor/commit-boundary-plan-8c79`). cov-n050-2 and cov-n051-2 stay held in `release.py` for the same reason.
