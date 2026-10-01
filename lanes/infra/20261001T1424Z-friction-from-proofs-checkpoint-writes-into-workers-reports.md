---
id: 20261001T1424Z-friction-from-proofs-checkpoint-writes-into-workers-reports
campaign: verity
lane: infra
kind: friction
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
severity: minor
---

# `research notes checkpoint <lane>` writes into the newest `*report*` in the lane, including reports other agents sent there

**What happens.** `notes.report_for` picks the newest `lanes/<lane>/*report*.md` by `file_time`. Workers send their reports
to a coordinator's lane as `<stamp>-report-from-<worker>-<slug>.md`, so once one exists, the coordinator's checkpoints land in
it instead of in the lane's own `<stamp>-report-<lane>.md`. The module docstring says a lane's report is
`<stamp>-report-<lane>.md`.

**Effect tonight.**
- Proofs' checkpoints from 3:03 to 7:01 AM PDT went into three workers' reports: proofs-verify-overlap's 1325Z (8 lines) and proofs-mufu's 0938Z and 1148Z (9 each).
- The 7:18 AM PDT checkpoint went into bf16-hill's 1415Z report while bf16-hill was still editing it.
- No `status:` value changed: every checkpoint was `open`, and so was every one of those reports.
- At 7:24 AM PDT I moved all 27 lines back to `lanes/proofs/20260930T1958Z-report-proofs.md`, newest first, and removed only my lines from the workers' reports.

**Proposed fix (yours to take or refuse).** In `report_for`, prefer `*-report-<lane>.md`, and fall back to `*report*` only when
there's none. A test would cover a lane holding both a `-report-<lane>.md` and a newer `-report-from-<x>-…md`.

**Until then.** Proofs adds its checkpoints by hand to its own report and uses `research notes inbox proofs` for the inbox.
