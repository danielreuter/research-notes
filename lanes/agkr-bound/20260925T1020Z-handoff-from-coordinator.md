---
lane: agkr-bound
kind: handoff
from: coordinator
created: 2026-09-25T10:20Z
---

# Link CLEARED WITH CONDITIONS (red-team-link): you may build it; route (a) results stay in the drill-down until C1-C8 + Flock at 2^-128

Read `lanes/red-team-link/20260925T0957Z-report-red-team-link.md` §4 (C1-C8, 17 negatives). What changes for you:
- **Build allowed** now, to the checklist. No Table 2 cell from route (a) until every condition holds, including a Flock
  2^-128 profile. I'm funding a lane for that; today's Flock is about 2^-100.
- **Take the σ-in-clear variant** for A-GKR, as recommended. It drops u and the second commitment, which your single-tableau
  design can't host, and it's valid for your non-ZK class only. Say so in the Table 1 class line.
- **BabyBear, not Goldilocks:** your GPU cells run over BabyBear with a degree-6 extension. That caps a linked proof at 21,845
  BF16 VUs, and 2x16-bit limb range checks on u let a forgery through (moot under σ-in-clear, but check the cap).
- **The verifier derives both index maps itself and checks they're injective.** A digest in the statement isn't enough;
  it's the same pattern as B-Ligero's R1.
- **Must-have negatives:** an altered operand carrying its own bits (your scaffold accepts it today: gap_alt_operand), a
  forged middle block with honest chunk endpoints (needs chaining in the Flock proof), and a swapped VU.
- One challenge point over GF(2^256), not two over GF(2^128) folded into Flock's opening.
