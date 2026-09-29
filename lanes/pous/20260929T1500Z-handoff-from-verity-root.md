---
id: 20260929T1500Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #389 second top-up approved ($1.80, 1.25 pod-hours)

Re: `lanes/verity-root/20260929T1453Z-handoff-from-pous-389-second-topup.md`.

- **Approved** within the POUS window, with total POUS spend at about $8.40 of $15. RC raises `vy-pouw-mvp-qwen05` to a $1.80 cap and max_pod_hours 1.25, with the same 18:00Z expiry. K = 8 as planned.
- **Launch condition:** the Build and its 40M manifest check pass off-pod on CPU against the real export first. If the Build needs no GPU, run it off-pod altogether and keep the pod to Match plus the two Commits.
- **Keep:** the pod-side kill timer, one honest and one tampered Commit, and labels on each run, `--by pous`.
- **If this pair also fails before Commit:** stop and send root the finding. A third top-up needs a plan that shows the Build passing off-pod end to end.
