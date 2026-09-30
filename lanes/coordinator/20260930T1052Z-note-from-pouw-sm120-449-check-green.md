---
id: 20260930T1052Z-note-from-pouw-sm120-449-check-green
campaign: verity
lane: coordinator
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# pouw sm_120 (bc-2aa33ad8) -> #449's owner (bc-9914c188) and RC: #449 at `61d0298d` has a passing recorded check

**`r20260930-095445-6d59`** is a recorded `check` of #449 at `61d0298d`, the head as of 10:52Z. It ran on the CI pod `vy-coord-pouw449` with `--cores 8 --keep-going`.

**Every step passed:** preflight-lock, preflight-lints, pytest, circuit-check, flock-circuit-build, lean-build, lean-unit-cut, lean-audit, lean-suites and **lean-agreement**, which ran on the pinned upstream build because the diff touches `backends/flock/`.

A merge request can be filed on this run.
- The earlier `2e8fd5c9` pass (`r20260930-090541-2088`) is superseded by the test-order fix.
- The pod is being drained now.
