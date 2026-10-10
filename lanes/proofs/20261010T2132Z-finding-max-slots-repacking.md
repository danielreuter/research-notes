---
id: proofs/20261010T2132Z-finding-max-slots-repacking
campaign: flock
lane: proofs
kind: finding
status: open
repo: danielreuter/verity
origin: proofs coordinator bc-8416bc72, on top's MAX_SLOTS ruling (Slack 1791666975) and ask (1791667323), at b795ecbde
---

# Raising `MAX_SLOTS` repacks parts that don't need it (2:32 PM PT, 10 Oct)

`rec_residuals.parts(spec(Shape(m, k_log, claims)), max_slots=X)` at b795ecbde. The input is the 33 distinct inner-session
triples of note:proofs/20261010T2112Z-finding-c3-claims-per-shape, which come from art:5200015a…. Each line gives the cap,
then (parts, outer statements = Ligerito levels + parts, the largest part's sha512x3 slots, residuals per part).

- At 172, 22 triples change:
  - all 14 at claims 8: still 2 parts, but first-fit moves residual 12 into part 0, which goes from 124–129 slots to 167–172;
  - 7 of the 8 at claims 12: 3 parts become 2;
  - Gumbel's (m35, k27, c16): refused, then 3 parts.
- Claims 6 and 10 don't change at 172 or 192. At 256, 6 of the 7 at claims 10 repack too.
- The outer statement count is never higher at 172 than at 160. It is 1 lower at the 7 repacked claims-12 triples.
- The F1 gate (m27, k24, c8), which isn't on the menu, goes from parts [0–9] (125 slots) and [10–12] (115) to [0–9, 12] (168)
  and [10, 11] (29). Both of its InnerRepCheck statements change.
- Alternative: first-fit at 160, with a residual that alone needs more taking a part of its own up to a second limit.
  Gumbel's shape then packs as at 172 ([0–10] 140 slots, [11–19] 115, [20] 172), and the other 32 triples pack as today.

```
83 rows 33 triples
m33 k23 c8 levels=6 160:(2, 8, 127, (10, 3)) | 172:(2, 8, 170, (11, 2)) | 192:(2, 8, 170, (11, 2)) | 256:(2, 8, 170, (11, 2))   <-- differs 6
m35 k25 c8 levels=7 160:(2, 9, 129, (10, 3)) | 172:(2, 9, 172, (11, 2)) | 192:(2, 9, 172, (11, 2)) | 256:(2, 9, 172, (11, 2))   <-- differs 4
m27 k23 c8 levels=4 160:(2, 6, 124, (10, 3)) | 172:(2, 6, 167, (11, 2)) | 192:(2, 6, 167, (11, 2)) | 256:(2, 6, 167, (11, 2))   <-- differs 4
m28 k22 c8 levels=5 160:(2, 7, 124, (10, 3)) | 172:(2, 7, 167, (11, 2)) | 192:(2, 7, 167, (11, 2)) | 256:(2, 7, 167, (11, 2))   <-- differs 4
m29 k27 c6 levels=5 160:(2, 7, 138, (9, 2)) | 172:(2, 7, 138, (9, 2)) | 192:(2, 7, 138, (9, 2)) | 256:(2, 7, 138, (9, 2))  1
m30 k22 c8 levels=5 160:(2, 7, 125, (10, 3)) | 172:(2, 7, 168, (11, 2)) | 192:(2, 7, 168, (11, 2)) | 256:(2, 7, 168, (11, 2))   <-- differs 7
m32 k26 c10 levels=6 160:(2, 8, 149, (12, 3)) | 172:(2, 8, 149, (12, 3)) | 192:(2, 8, 149, (12, 3)) | 256:(2, 8, 203, (13, 2))   <-- differs 4
m30 k26 c10 levels=5 160:(2, 7, 148, (12, 3)) | 172:(2, 7, 148, (12, 3)) | 192:(2, 7, 148, (12, 3)) | 256:(2, 7, 202, (13, 2))   <-- differs 6
m32 k26 c12 levels=6 160:(3, 9, 160, (13, 3, 1)) | 172:(2, 8, 171, (14, 3)) | 192:(2, 8, 171, (14, 3)) | 256:(2, 8, 235, (15, 2))   <-- differs 2
m30 k26 c8 levels=5 160:(2, 7, 127, (10, 3)) | 172:(2, 7, 170, (11, 2)) | 192:(2, 7, 170, (11, 2)) | 256:(2, 7, 170, (11, 2))   <-- differs 6
m35 k27 c16 levels=7 160:('refused',) | 172:(3, 10, 172, (11, 9, 1)) | 192:(3, 10, 172, (11, 9, 1)) | 256:(3, 10, 172, (11, 9, 1))   <-- differs 1
m28 k26 c10 levels=5 160:(2, 7, 147, (12, 3)) | 172:(2, 7, 147, (12, 3)) | 192:(2, 7, 147, (12, 3)) | 256:(2, 7, 201, (13, 2))   <-- differs 2
m35 k27 c10 levels=7 160:(3, 10, 140, (11, 3, 1)) | 172:(3, 10, 140, (11, 3, 1)) | 192:(3, 10, 140, (11, 3, 1)) | 256:(3, 10, 140, (11, 3, 1))  4
m28 k26 c6 levels=5 160:(2, 7, 137, (9, 2)) | 172:(2, 7, 137, (9, 2)) | 192:(2, 7, 137, (9, 2)) | 256:(2, 7, 137, (9, 2))  4
m34 k24 c8 levels=7 160:(2, 9, 128, (10, 3)) | 172:(2, 9, 171, (11, 2)) | 192:(2, 9, 171, (11, 2)) | 256:(2, 9, 171, (11, 2))   <-- differs 1
m34 k26 c8 levels=7 160:(2, 9, 129, (10, 3)) | 172:(2, 9, 172, (11, 2)) | 192:(2, 9, 172, (11, 2)) | 256:(2, 9, 172, (11, 2))   <-- differs 1
m31 k27 c8 levels=6 160:(2, 8, 128, (10, 3)) | 172:(2, 8, 171, (11, 2)) | 192:(2, 8, 171, (11, 2)) | 256:(2, 8, 171, (11, 2))   <-- differs 1
m35 k27 c12 levels=7 160:(3, 10, 140, (11, 5, 1)) | 172:(3, 10, 140, (11, 5, 1)) | 192:(3, 10, 140, (11, 5, 1)) | 256:(3, 10, 140, (11, 5, 1))  1
m26 k24 c6 levels=4 160:(2, 6, 135, (9, 2)) | 172:(2, 6, 135, (9, 2)) | 192:(2, 6, 135, (9, 2)) | 256:(2, 6, 135, (9, 2))  3
m32 k24 c12 levels=6 160:(3, 9, 159, (13, 3, 1)) | 172:(2, 8, 170, (14, 3)) | 192:(2, 8, 170, (14, 3)) | 256:(2, 8, 234, (15, 2))   <-- differs 2
m33 k25 c10 levels=6 160:(2, 8, 149, (12, 3)) | 172:(2, 8, 149, (12, 3)) | 192:(2, 8, 149, (12, 3)) | 256:(2, 8, 203, (13, 2))   <-- differs 2
m30 k26 c12 levels=5 160:(3, 8, 159, (13, 3, 1)) | 172:(2, 7, 170, (14, 3)) | 192:(2, 7, 170, (14, 3)) | 256:(2, 7, 234, (15, 2))   <-- differs 4
m34 k26 c10 levels=7 160:(3, 10, 150, (12, 2, 1)) | 172:(3, 10, 150, (12, 2, 1)) | 192:(3, 10, 150, (12, 2, 1)) | 256:(2, 9, 204, (13, 2))   <-- differs 2
m32 k22 c8 levels=6 160:(2, 8, 126, (10, 3)) | 172:(2, 8, 169, (11, 2)) | 192:(2, 8, 169, (11, 2)) | 256:(2, 8, 169, (11, 2))   <-- differs 1
m29 k25 c8 levels=5 160:(2, 7, 126, (10, 3)) | 172:(2, 7, 169, (11, 2)) | 192:(2, 7, 169, (11, 2)) | 256:(2, 7, 169, (11, 2))   <-- differs 1
m29 k25 c12 levels=5 160:(3, 8, 158, (13, 3, 1)) | 172:(2, 7, 169, (14, 3)) | 192:(2, 7, 169, (14, 3)) | 256:(2, 7, 233, (15, 2))   <-- differs 1
m33 k27 c10 levels=6 160:(2, 8, 150, (12, 3)) | 172:(2, 8, 150, (12, 3)) | 192:(2, 8, 150, (12, 3)) | 256:(2, 8, 204, (13, 2))   <-- differs 1
m30 k22 c12 levels=5 160:(3, 8, 157, (13, 3, 1)) | 172:(2, 7, 168, (14, 3)) | 192:(2, 7, 168, (14, 3)) | 256:(2, 7, 232, (15, 2))   <-- differs 1
m31 k23 c12 levels=6 160:(3, 9, 158, (13, 3, 1)) | 172:(2, 8, 169, (14, 3)) | 192:(2, 8, 169, (14, 3)) | 256:(2, 8, 233, (15, 2))   <-- differs 1
m31 k23 c8 levels=6 160:(2, 8, 126, (10, 3)) | 172:(2, 8, 169, (11, 2)) | 192:(2, 8, 169, (11, 2)) | 256:(2, 8, 169, (11, 2))   <-- differs 2
m30 k24 c12 levels=5 160:(3, 8, 158, (13, 3, 1)) | 172:(2, 7, 169, (14, 3)) | 192:(2, 7, 169, (14, 3)) | 256:(2, 7, 233, (15, 2))   <-- differs 1
m30 k24 c8 levels=5 160:(2, 7, 126, (10, 3)) | 172:(2, 7, 169, (11, 2)) | 192:(2, 7, 169, (11, 2)) | 256:(2, 7, 169, (11, 2))   <-- differs 1
m31 k25 c8 levels=6 160:(2, 8, 127, (10, 3)) | 172:(2, 8, 170, (11, 2)) | 192:(2, 8, 170, (11, 2)) | 256:(2, 8, 170, (11, 2))   <-- differs 1
triples whose parts differ across caps: 28
```
