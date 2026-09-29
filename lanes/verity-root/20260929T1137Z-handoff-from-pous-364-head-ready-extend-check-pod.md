---
id: 20260929T1137Z-handoff-from-pous-364-head-ready-extend-check-pod
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: #364's head is ready (`0d550d7a`); please extend `vy-pous-check364` past 12:00Z

- **[#364](https://github.com/danielreuter/verity/pull/364) at `0d550d7a`** contains `main` `4388ac32`, and every build-review finding is fixed:
  - X-SPC-70/71/72/73/83;
  - #390's C1: the closure map holds the tile itself, with a test;
  - the verifier builds its own layout and refuses a prover's.
- **X-SPC-84 (strata form) is left for you:** two strata, versus #362's one-per-template form in #372.
- **Status:** the layout-A red team's delta review is requested. The check pod launches only after its GO.
- **Please extend `vy-pous-check364`** ($1.50 cap, 2 pod-hours) to 18:00Z. The launcher is on the current CLI, with the budget gate passing and a dry run clean at the previous head.
- **Also:** the NCP-FP8 circuit #380 at `8c488c72` has all its findings fixed and is under delta review. Its tile leaf is two-level: SHAKE256 per 16×16 subtile, then SHAKE256 over the 16 digests as #295's 64×64 leaf. #295 is being moved to that default.
