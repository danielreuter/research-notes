---
cursor:
  subagentId: "bc-0c4fbab5-c272-5c4c-8b3e-6e1684ae213e"
id: coordinator/20260930T1700Z-handoff-from-multipart-stall-merge-request
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: run-on-fixes worker (bc-0c4fbab5)
---

# Merge request: `cursor/multipart-stall-213e` (https://github.com/danielreuter/verity/pull/579), commit `a13199dbe`

Please train it, together with `cursor/run-on-fixes-213e` (#574) if that's convenient; the two branches don't share any files. It changes only
`tools/research`, so `lean-agreement` doesn't apply. `check` has not been recorded. Locally, the full `tools/research` suite passes.

This closes item 4 of note:coordinator/20260930T1615Z-handoff-from-verity-root-friction-run-on-late-failures, which is
note:20260930T1038Z-handoff-from-nebius-infra-steward-custody-multipart-stall. Previously, a part PUT's deadline was
`180 s + bytes / 8 KiB/s`, about 9 h for a 256 MiB part, with 4 tries. Now it's cut off when a 120 s window passes with under 1 MiB sent, or with no response after the body.
The failed part is retried and the parts already uploaded are kept; if every try fails, the upload is aborted and the publish fails instead of holding its slot.

Only `store/remote_s3.py` and its tests change. `custody.py` isn't touched, so there's no conflict with the run-outputs worker (bc-a98dbece,
`cursor/run-declared-outputs-4c35`, which changes `custody.py` and `telemetry/run.py`).
The fix hasn't been tried on the Nebius hosts yet; the next run on node 2 that has files over 64 MiB will show whether it works.
