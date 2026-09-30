---
id: lean-gemm-relation/20260930T0629Z-friction-run-timeout-units
lane: lean-gemm-relation
kind: friction
status: open
---

# `research run --on` accepts `--timeout 40m`, the machine's harness rejects it, and the run sits in "submitted"

Run `r20260930-062341-5775` on vy-nebius-1 (the ssh-provider CLI from branch `cursor/nebius-server-da07`): the launcher
returned "launched", but the machine's `research run --attempt-dir` exited with "argument --timeout: invalid float value:
'40m'" in `launcher.log`. `research fetch` and `inspect` kept reporting `submitted rc=None` with no hint, and it took an
ssh into the run directory to find it (about 10 minutes). Relaunched with `--timeout 2400` as `r20260930-062851-727b`.
The fix: parse durations (`40m`, `6h`, as `--custody-ttl` does) or reject them before launching, and have `fetch` report
a launcher that exited.
