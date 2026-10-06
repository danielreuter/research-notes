---
id: review-zk-gateway/20261006T1143Z-finding-review-zk-gateway-r7
campaign: proof-service
lane: review-zk-gateway
kind: finding
status: final
repo: danielreuter/verity
origin: [pr:1270@9cced347952bed837abddf28a31fee0518d946cc, pr:1343@b9d912d5af1ca19eda343292b9fae88a1c92be30]
---

# Red-team round 7: #1270 at `9cced3479` GRANT; #1343 at `b9d912d5a` NO-GRANT

The detail, probes and outputs are in the store's `private/red-team-reviews/1270/` (`r7-*`) and
`private/red-team-reviews/1343/` (`review-r7.md`, `r7-*`). No pod run: both reviews are Python and git only.

## #1270 (`cursor/zk-gateway-95d4`): GRANT at `9cced347952bed837abddf28a31fee0518d946cc`

This grant carries r5's grant of `74b2c0d3a` (`note:review-zk-gateway/20261006T0833Z-finding-review-zk-gateway-r5`) across
the rename and top's move. `research.queue.carry` returns False, as designed, so the head is reproduced and labelled again.
- **The rename is rename-only.** `fw-rename-check.py` (`art:cdc0093c…`), rerun: proofs' map applied to `74b2c0d3a` gives
  `2d694e170`'s tree exactly. 210 lines change, and no run is outside the map.
- **The restack reproduces.** `tools/move/restack.py 2d694e170 --move-commit afc9d352d --onto a7134c413`, with the posted
  committer and dates, is clean at every step and gives `09bc4bbc5`. The "ours" merge with `8e747893e` gives `9cced3479`.
- **The patch is unchanged modulo the two maps.** `9cced3479` over `8e747893e` against `74b2c0d3a` over `edf8f70ad`: 17
  files and 2,436 lines. 210 lines are proofs' map and 2 are the move's map; 0 are unexplained.
- **Non-blocking.** The move's map turned the credit "(review-zk-gateway's r4)" in `test_rec_live_firewall.py` into
  "(review-zk-firewall's r4)". PR 2 restores it.

## #1343 (`cursor/firewall-release-95d4`): NO-GRANT at `b9d912d5af1ca19eda343292b9fae88a1c92be30`

**Holds:**
- **The restack reproduces.** `8c993d681` gives `a6096748d`, clean, and the "ours" merge with `9cced3479` gives `b9d912d5a`.
  Its diff over #1270 is the same lines as rules 1–2 before the move: 4 files, 0 lines differ.
- **The tests pass.** 79 passed across the four files. The 14 release tests pass 30 runs in a row with thread exceptions as
  errors, and the no-wall-clock invariant passes.
- **The negative controls fail as the body says.** With `admit` ignoring a stop, 5 tests fail; with no slot, 2 do.
- **The real-binary run matches the body.** In `art:4c115cd6…`, L1's stop is a cut at serve, L2 is refused, and the record
  is `slot`, `wait`, `release`, `slot`, `release`.
- **The body states D8 (a)** (outside `FirewallComputes`).
- No circuit changed.

**Blocking:**
- **B1.** The first row's 11.19 bits assume that every statement before the stop was released and every one after it was
  never opened. The relay enforces only "nothing after a recorded stop". A V* statement never opened is no stop, the
  statements are admitted in any order, and a released one is served again. Without a fixed order, the row is about 18.0
  bits (log₂ 261663), plus the order. Fix: fix the statements and their order at `open`, and have `admit` refuse all but
  the next one, with tests. Or restate the row.
- **B2.** §10.5 lists the firewall's record as part of the auditor's view. That record keeps each stop's `why` (how it
  stopped, and the inner refusal's full text), every `refused` attempt and every `wait`. Fix: say the record stays with the
  developer, or keep only the one stop and its part.

Non-blocking (N1–N4: `Finish` after one proof, the slot during refusals, cross-stream order, the record's parsing) are in
`review-r7.md`.
