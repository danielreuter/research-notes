---
cursor:
  subagentId: "bc-21aca6c8-631a-51fd-8553-ad0d0947ad11"
---

# Laptop parity pass 1 (03:15Z, 8:15 PM PT): findings and fix

Input: `internal/parity-20260925T0315Z.json`. Fix: [PR #12](https://github.com/danielreuter/verity/pull/12), branch
`cursor/parity-attempt-divergence-ad11`.

## 1. Nine divergent Sep 22 attempts

- **The R2 copy is canonical, and R2 was never rewritten.** I read R2 directly from a cloud VM:
  - each of the nine keys was written once, 17:55:42 to 18:02:15 UTC on Sep 22 (Last-Modified);
  - that's 24–31 minutes after the attempt builder landed (`66e4fd4f`, 17:31 UTC);
  - every artifact they name is on R2, including `telemetry.resources`.
- Six are pod runs on `vyv-accept` (host `1b087b2154a1`). Three are laptop runs (host `Daniels-MacBook-Pro.local`), each published at
  run end.
- **Nothing could have overwritten R2.** `S3Remote.put` raises `RemoteConflict` on different content, and `research` has no code
  path that rewrites a local attempt.
- **So the laptop's copies are later second publishes.** Something rebuilt them from the run directories with a builder that emits
  neither `load_end` nor `telemetry.resources`, which `research`'s builder has emitted since it first landed. Probably the pre-switchover
  veritor tooling, or a re-publish after the local file was lost and the run directories were evicted. It ran without R2 credentials,
  so it couldn't adopt the existing copy.
- **Why nobody noticed:** a push of such a copy is a `RemoteConflict`, and `preserved` only checked that the key existed.
- **To confirm on the laptop:** `stat -f '%Sm' ~/.research/store/attempts/r20260922-0531*.json`. A time well after Sep 22 18:00 UTC
  confirms a re-publish.
- **Recommendation:** one-time reconciliation with an audit log (`reconcile-attempts --all`, then `--apply`), plus the `preserved`
  content check so this can't recur silently, plus the wrapper loading credentials (runbook step 4).
  - Superseded local copies are kept verbatim under `attempts/.superseded/`.
  - Labels on artifacts only the local copy named stay valid; the log lists those artifacts.

## 2. The 43-line render difference

- **Cause: timing inside parity.** The labels were compared at one moment (11,519 on both sides), but the render view was built later
  from the live directories, and verify-po wrote 6 labels in between.
- **Fix:** freeze the compared records and render both sides over the same union. Count records written during the run and report
  them as concurrency.

## 3. "Not the real renderer"

- **What parity ran before:** `tables` only, with its own interpreter's `verity_numerical`, working directory and code.
- **What the daily render runs:** `tables` and `drilldown`, from the `steward.toml` source tree (on `PYTHONPATH` and as the working
  directory).
- **Fix:** #12 runs exactly that invocation and names the source commit.
- **New check:** it also renders the store under test directly, as the daily render does, and requires that output to match the
  snapshot view. That catches any view-versus-catalog difference.
- **Not the table code:** no bench code changed between #8's merge and `b84f11ea`, the commit of the 8:48 PM PT published tables.
- **Likely cause of the B-Ligero gap, unverified:** part of it is probably timing. Parity ran at 8:15 PM PT, and the arith red-team
  labels landed before the 8:48 render.
