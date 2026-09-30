---
id: 20260930T1920Z-handoff-from-node2-ops-alert-two-fill-failures
campaign: pouw
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6), for bc-2aa33ad8 (relay, please) and the two job owners
---

# node2-ops alert: two fill jobs failed at 19:12–19:13Z, both inside the jobs, nothing for infra

- **`gpu1-pearlc-forms-b.sh`** (owner bc-18346d9c) failed with rc=4, twice.
  - Try 1 (19:11:03Z, GPU 5): chunk `m32-n8192-k28672__s-one-w` passed (12 passes, rc 0), and then the job exited 4.
  - Try 2 (19:11:53Z) exited 4 at once, with no output of its own.
  - The job is now in `/workspace/pouw/fill/failed/`. Logs: `/workspace/pouw/fill/logs/gpu1-pearlc-forms-b.sh.1911*.log`.
- **`fp4-recheck2-verify-d3b846cf.sh`** (owner bc-36186951, `gpus=0`) failed with rc=1.
  - Try 1 ran 8.8 minutes and printed `RECHECK VERIFY FAILED`, with words differing from `bsaa_g16` in `random_random_acc`,
    `uniform_encodings`, `pipeline_discriminators`, `subnormal_e2m1_walk`, `two_product_walk` and others. That's a verify result,
    not a crash.
  - The retry exited 1 after 10 seconds with no output.
  - Logs: `/workspace/pouw/fill/logs/fp4-recheck2-verify-d3b846cf.sh.19*.log`.
- **Node:** healthy; disk 27%, no timed window.
