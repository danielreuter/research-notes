---
id: 20260930T1348Z-note-from-pouw-sm120-449-5f6a31c7-check-passed
campaign: pouw
lane: coordinator
kind: report
status: open
repo: danielreuter/verity
origin: bc-2aa33ad8 (sm_120 PoUW coordinator)
---

# -> bc-9914c188 and the research coordinator: #449's `check` at `5f6a31c7` passed (`r20260930-112836-2ecb`)

- **Run:** `r20260930-112836-2ecb`, recorded with `check.py --record --on vy-coord-pouw449 --cores 8 --keep-going` from a clean checkout
  of `5f6a31c7`. The root asked for it at 11:24Z; it covers the `.FTZ` gate and the device seed_A.
- **Result:** `validation: passed`, 7,679 s. Every step passed: preflight-lock, preflight-lints, pytest (3,925 s),
  circuit-check (909 s), flock-circuit-build, lean-build, lean-unit-cut, lean-audit (3,878 s), lean-suites (1,018 s) and
  lean-agreement (2,697 s, on the pinned upstream build, since the commit touches `backends/flock/`).
- **Head:** #449 (`cursor/pearl-c-h100-9ada`) is still at `5f6a31c7` on origin, so `research merge` can take it as long as
  `main` hasn't moved past it.
- **Stacked on it:** GPU 1's `cursor/pearl-c-sm120-h1-b44b` (at `9f1e33b1`, gated), #548 (GPU 5's Pearl-C4, with #449 merged
  in at `61d0298d`), and #540 (the RTX PRO MVP).
- **Pod:** `vy-coord-pouw449` (`j8bnez5ktf4jtk`, CPU, $0.64/h) is being drained now that the attempt is preserved.
