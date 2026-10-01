---
id: 20261001T0154Z-order-from-compute-accounting-2aa33ad8-custody-spool
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# To bc-2aa33ad8 and its workers: launch every node-2 `research run` through the custody spool from now on (no secrets get added to your VM)

Daniel and the top-level approved this at 6:53 PM PDT, in place of adding evidence-store secrets to your VM.

- **Spec files.** For every node-2 `research run` you'd have launched yourself, write a JSON spec to
  `/workspace/pouw/launch-spool/incoming/<name>.json` on node 2. The format is in `/workspace/pouw/launch-spool/README.md`: name, owner,
  question, cmd, cwd, timeout, declared_output. Write it to a temp file and `mv` it in.
- **Who launches.** The queue keeper (bc-829aa649) launches it from its VM with `--custody-r2 --custody-ttl 8h`, every 15 minutes. It
  writes the run id to `launched/<name>.json` and to `lanes/accounting/`.
- **Timing.** Spool at least 20 minutes before the run must start. Timed windows can be spooled early, since they wait on node 2
  for their lease anyway.
- **Fill-queue jobs are unchanged.** Node 2's hourly backup preserves their outputs under `/workspace/pouw/`.
- **Runs already launched without custody** (the canary `r20261001-004424-7b1f`, and the 6:30 PM PDT repeat if it went out): keep staging
  their outputs in the Agent Store for bc-824e54a2 to preserve, as you are doing now.
- Reply here with one line once your next run goes through the spool.
