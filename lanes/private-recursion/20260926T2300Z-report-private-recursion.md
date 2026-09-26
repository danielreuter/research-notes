---
id: 20260926T2300Z-report-private-recursion
campaign: circuit-privacy
lane: private-recursion
kind: report
status: open
repo: danielreuter/verity
origin: cursor/private-recursion-bad3
branch: cursor/private-recursion-bad3
---

CHECKPOINT 128e7f2c (23:59Z) [open] V[B] (4.52 G ANDs, fold 3.59 G) accepts honest RoPE art:bd9f7efb; agrees with recorded Lean/upstream verdicts on 28/28 (D-rs, D-fc refused at decode); own negatives running; draft PR #97
CHECKPOINT 461c99e2 (23:34Z) [open] building V[B] as a program of gadget tables; gadgets pinned (SHA-256 22,573 / SHA-512 57,947 / GF128 2,187 ANDs), hm96-sha512 matches PR #93 vectors, native lincheck with my fold passes on art:bd9f7efb honest; next: V[B] builder + coin tables + witness
CHECKPOINT 748c3cd6 (23:08Z) [open] started: read spec I.1-I.10, PR #83 statement, PR #85 PROTOCOL.md; RoPE unit has 158k nonzeros (spec bound 2^16); building V[B] on recorded fd02e847 sessions (art:bd9f7efb)
# private-recursion: the smallest private-circuit prototype (inner Flock session verified inside a hand-built V[B])

Spec: Project store `docs/circuit-privacy.md` Part I (I.2, I.3, I.9). Agent bc-be25385c-8dda-5970-9cf6-7c0ce338bad3.
