---
cursor:
  subagentId: "bc-bae5e52c-4820-5cd5-bd6a-9eeb1a6856f0"
id: coordinator/20260930T1615Z-handoff-from-verity-root-friction-run-on-late-failures
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root (daily friction pass, worker bc-bae5e52c)
---

# verity-root -> RC, owner of `tools/research`: `research run --on` and custody fail late and silently on ssh machines (three today)

From root's daily friction pass (Project store `internal/friction/20260930-pass.md`). Three failures today have one shape: the
launcher accepts a run that the machine then rejects or misruns, `research fetch` doesn't show it, and the lane finds out by ssh.

1. **`--timeout` with units** (note:lean-gemm-relation/20260930T0629Z-friction-run-timeout-units, `r20260930-062341-5775`):
   `--timeout 40m` launched, the machine's harness exited "invalid float value: '40m'", and `fetch`/`inspect` said
   `submitted rc=None`. `_harness_timeout` (`cli.py`) and `lease_extend_s` (`remote.py`) also return `None` on `40m`, so
   neither the custody-key guard nor the lease extension sees that timeout. Fix: parse `--timeout` once at launch with
   `credentials.parse_ttl`'s grammar and ship seconds, or refuse it before launching.
2. **A launcher that exited still shows as submitted** (same run): `fetch` reports a machine-side launcher exit, with
   `launcher.log`'s last line.
3. **Relative-path command without `--cwd source`** (note:lean-value-binding/20260930T0826Z-friction-run-cwd-custody-upload,
   `r20260930-080414-bae0`): it ran in the run dir, custody uploaded 9.5 GiB of undeclared files for 54 min, SIGKILL, no
   attempt. Fix: print the resolved cwd at launch; refusing `--source` without `--cwd` is your call (the documented recipes all
   pass `--cwd source`). Whether custody may skip undeclared files over a size cap is with Daniel (ruling request in the pass);
   leave that part until he answers.
4. **Multipart stall** (the nebius-infra steward's 10:38Z handoff to you, still open): a read timeout on part uploads and retry
   with resume, so a stalled publish ends instead of holding a slot for over an hour.

Also yours, about three lines: `notes.py` `push_branch`'s "REFUSED <l>: no local branch lane/<l>" names the fix when the
worktree is on another branch: `research notes bind <l> --branch <current> --worktree <dir> --pod none`
(note:flock-v2-design/20260930T1250Z-friction-final-check-unbound-branch; `checkpoint final --require-pushed` failed the same way).

None of these is in an open PR; #496 (`infra/nebius`) and #448 touch `cli.py`/`remote.py`. If you'd rather a worker take them,
say so in your next checkpoint and root assigns one. Whether a lane may fix a `tools/research` bug itself, with you reviewing, is
also with Daniel (same pass).
