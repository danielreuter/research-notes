---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Proposal (deferred): resumable custody uploads

**Status:** deferred by the root on 2026-09-26, as a medium-sized change. What landed instead is the size warning:
`research.store.custody.SIZE_WARN_BYTES` (4 GiB) prints a warning before pushing a bigger run and records it as
`size_warning` in the run's `.custody` marker. Also landing is the key-lifetime guard: a `--timeout` longer than 6 h needs
an explicit `--custody-ttl`, capped at 24 h. Source: `docs/process-robustness.md`, item 2.

## Problem

`runner_publish` pushes a run's record with `push_run` and retries the whole push up to `PUSH_TRIES` times on a fresh
connection (PR #51). An object that drops mid-upload restarts from byte 0. On a large run (multi-GiB dumps) near the end of
its key's lifetime, the retries can exhaust the key. The run then stays on the pod as "custody NOT on the remote", and
repairing it needs a fresh key.

## Sketch

1. **Multipart uploads** for objects over a threshold (R2 and S3 both support them; about 64 MiB parts). Record the upload
   id and completed part ETags in `<custody dir>/upload-state.json`, next to the key, outside the run dir.
2. **Resume:** on retry, `ListParts` for the recorded upload id, skip the parts already done, and complete it. If the upload
   id is gone, start over.
3. **Repair path:** `research data custody RUN --publish` with a fresh key reads the same state file, so a repair resumes
   instead of restarting.
4. **Clean-up:** abort stale multipart uploads older than the key's lifetime. Also set a bucket lifecycle rule for
   incomplete multipart uploads.

## Size

About 150–250 lines in `remote_s3.py` and `custody.py`, plus tests against the `fs` vault with injected mid-part failures.
There's no format change to preserved records: the finished objects are identical.

## When to do it

When a run over the warning size appears, or the first time a custody failure is caused by an expired key on a big upload.
Until then, keep large outputs out of the run dir or give `--custody-ttl` room.
