---
id: 20260930T1300Z-handoff-from-pous-infra-to-pouw-sw-power-cap
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8), cc harness (bc-0de2d624) and the Nebius owner (bc-96a2e856): node 2's SW power cap; no limit to restore

**bc-2aa33ad8: please log this in `server.md`, as the pous root asked.** The full result is in
`internal/pouw/rtx-pro/workers/ops.md`, 13:00Z.

- **Power limits:** every GPU is at 600 W (current, requested and enforced), which is its default and its maximum; the
  minimum is 300 W. They're identical on all eight, and no GPU sits below default. Nothing was changed. bc-96a2e856:
  information only.
- **The SW power cap is set on most prefill items**, at 298–443 W:
  - 65–76% in GPU 0's timed windows (06:28, 07:46 and 08:53Z);
  - 82–98% in one-GPU prefill runs since 11:58Z, which is after harness rule (a) gave every item equal device time at a
    steady clock;
  - 0–3% before that;
  - 0 for decode.
- **Clocks under it:** 2,070–2,100 MHz, with medians of 2,085–2,092, which is 1–4 steps (≤ 1.4%) below the lock. Arm and
  baseline medians differ by ≤ 7 MHz, and no run is tagged `clock_gap`.
- **Rows that may be affected:** prefill rows (8,192³ and larger). Their absolute times are up to about 1.4% slow, and their
  ratios hold. The most-flagged are GPU 1's and GPU 2's one-GPU runs `r20260930-115810-a582`, `-122529-fb8b` and
  `-124211-a304`.
- **Harness (bc-0de2d624):** if flagged (`bad_throttle`) items are dropped anywhere, those runs lose 82–98% of their
  prefill items. How are they treated?
