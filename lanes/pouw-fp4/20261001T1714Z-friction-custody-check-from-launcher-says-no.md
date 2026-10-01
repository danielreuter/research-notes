---
id: pouw-fp4/20261001T1714Z-friction-custody-check-from-launcher-says-no
lane: pouw-fp4
kind: friction
status: open
---

# `research data custody RUN` on the launching VM says NO custody for every `--on` run

`r20261001-134930-22d2` and `r20261001-071845-d95f` (both `--on vy-nebius-2 --custody-r2`) each report "NO custody on the
remote: 1 file(s) not in the run record ...: remote.json" from this VM. Both are PRESERVED (`research data preserved`), and the pod's
`.custody` says preserved (run record `art:9bf7b791`, 489 files, 16:50:00Z). `custody.verify` compares the local run dir with the
pod's record, and the launcher's `remote.json` is never in it, so the custody module's docstring ("`research data custody RUN`
answers the same everywhere") doesn't hold on the launcher. It cost about 10 minutes of doubting a custody claim I had already
posted. What I did instead: `research data preserved RUN`, plus reading the pod's `.custody`.

I didn't fix it, because skipping `remote.json` in `verify` would let the custody guard pass a launcher file that nobody preserved.
Two other fixes keep it fail-closed. The runner could ship `remote.json` with the run, or the error could say that the only
mismatch is a launcher-side record and name `research data preserved RUN`.
