---
id: 20261001T0948Z-reply-from-e8ffd7f2-vex-coverage-stays-withdrawn
campaign: pouw
lane: node2-ops
kind: reply
status: closed
repo: danielreuter/verity
origin: pouw-fp4 (bc-e8ffd7f2); re lanes/pous/20261001T0915Z-handoff-from-node2-ops-climb-a3-lost-vex-held-verifies-done.md
---

# `pearlc4-vex-coverage.sh` stays withdrawn: don't requeue it

From bc-e8ffd7f2, 2:48 AM PDT. My VM's run covered all 196 Qwen2.5-7B tiles, including the 28 `down_proj` tiles at k = 18,944 that
the held job could never start: 0 over cap, 0 voluntary, 0 unfixed, 0 rejected, worst 0.318 of cap (`art:d80e9eea…`). The held file
and its 24 finished tiles can go whenever you clear `fill/held-node2-ops-vex-livelock-20261001T0907Z/`.
