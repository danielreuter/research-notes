---
lane: coordinator
kind: handoff
from: agkr-bound
created: 2026-09-25T11:40Z
---

# agkr-bound: the bit link's prime side is BUILT in A-GKR (sigma form, one GF(2^256) point), both verifiers. BF16 prove 1.20 -> 1.53 s, 11 of 11 negatives rejected by Python and Rust. Drill-down only (L).

lane/agkr-bound 78b1a62e: `gpu/link.py`, `verifier/src/link.rs`, PROTOCOL.md §17. Report section "The link built"
in `lanes/agkr-bound/20260925T0424Z-report-agkr-bound.md`. Evidence art:bd3d8b2c + art:fc687ece.

**Built to the 1020Z direction and red-team-link §4:**
- C1: one point in GF(2^256)^28.
- C2: the coins are their own slots, drawn after the Ligero root, the GKR messages and root_b.
- S1 sigma form: 256 sigma_t in the clear. This is NON_ZK_PROOF only; the Table 1 class line must say so.
- C5: both verifiers derive Lambda_F from the unit circuit and check it is a bijection.
- C6: n_cells <= p - 1 is enforced. That allows up to 40,960 BF16 VUs; the red team's figure is 40,959.
- C7: booleanity and recomposition are checked for every link bit.

**Stand-in binary side.** root_b is SHA-256 of a tag and commitment.txt. y is computed from x.bin / w.bin, which the
Rust verifier requires to hash to the public sha256/row/v1 digests.

**Cost.** A100 BF16 in-unit statement, 4,096 VUs, MALLOC tunables set:

| | before | after |
|---|---|---|
| median prove | 1.20 s | 1.53-1.54 s (link 0.33 s) |
| Python verify | 1.25 s | 1.56-1.58 s |
| Rust verify (13 threads) | 3.41 s | 4.68 s, plus 0.44 s derivation |

The proof grows by 6,144 B. The route (a) prime side is now measured at about 1.54 s per BF16 batch. That replaces my
1.44 / 1.65 s estimates; Flock is extra.

**Negatives rejected by both verifiers:**
- bit flip, non-boolean;
- alt_alt_bits (the scaffold used to accept it);
- sigma out of range, sigma + 2;
- root_b changed, z differs;
- vu_remap (sigma under a VU-swapped Lambda);
- a duplicated link column, a dropped booleanity assertion.

The forged middle block is not run: it needs the Flock chaining (C4).

**Decision still yours (red-team-link's).** Whether to fund C3 (Flock at 2^-128: a GF(2^256) interactive profile and
a Flock red team) and C4 (chain glue). Until both land, route (a) stays drill-down only.
