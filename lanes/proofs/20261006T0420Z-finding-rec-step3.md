---
id: proofs/20261006T0420Z-finding-rec-step3
campaign: flock
lane: proofs
kind: finding
status: active
repo: danielreuter/verity
origin: bc-2a00fbff-762d-5c36-a641-1bbff50ddb4d (rec-reprice, for the proofs coordinator bc-8416bc72)
---

# Recursion rollout step 3: V* climbs plain SHA-512 leaves to tree tops the gateway commits under salts

Question (Daniel: live coins only; end to end means `VBridge` is proved, until then a prototype): once the inner session's
leaves are plain SHA-512 and the gateway commits every tree top under a salt, does V* still reject every forged top or salt
(and step 2's forgeries) in serve, upstream `replay --zk` and Lean `verify --zk`, and what does V* cost at K = 4096, m = 35
under a GPU lease per prove, against step 2 (note:proofs/20261005T1536Z-finding-rec-step2)?

## The format

zk-gateway's salted top (8c9a6631d `commit_top`, the bare node as hm96's inner digest) is not the commitment of any row, so
a level's `out` (a registered row, as in step 2) cannot read it; putting hm96 in `RecOpen` gives back 2 of the 4 saved
compressions. Step 3 builds against this format, written up for zk-gateway in
`/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/internal/proofs/zk-gateway-from-rec-step3.md`:
- each cap node is a registered row (its 32 LE u16 words, then 32 zeros), committed as
  `hm96 commit_string(default_key, sha512_row_digest(row, 16, ROLE_X), salt)` under its own fresh salt
  (= `Registered.commit`'s `b ‖ c`);
- level 0 once at Commit, its binding-round copy counted as `level0`;
- V* registers `rec-top-L<l>` under the gateway's salts, its root checked against the coin server's `b ‖ c`.

## The commits (`cursor/rec-step3-95d4`, on rec-step2 b6139d9b6)

- 0d9ababc9: plain SHA-512 leaves (META `leaf_scheme` `flock-leaf/sha512-unsalted`).
- e3a1ab023: the format above in `rec_live` and `rec_vstar`.
- 6ccb216a1: `rec_vstar.Top`.
- a86ecaa55: `RecOpen_v3{LANES,H}` (LANES/8 + 1 + 2H compressions), `rec_outer.TopValue`, the `top` and `top-salt` forgeries.
  circuit-check RecOpen_v3{LANES=8,H=1}: ok, 0 failures, 1 warning (redundant-gates/ir 16,538), q_call 764368u/1639292b,
  450.1 s (v2: 1289056u/3038280b, 2,338.4 s).
- 42678ddf6: InnerFold.lean `--plain-leaves`.
- 0d15464c1: 85-rec-reprice stages plain (`stage`) and hm96 (`stage-zk`).
- d23edf42d: merge of rec-step2 (the restack onto main 7b410fbf6).
- c8321f7a2: the GPU decoder reads an opening's salts only when the prover installed a salt context. It always read a
  count; a plain-leaf proof's stream misaligned into "capacity overflow" after 139 rounds (r20261006-013115-a310).
- 195fdddbc: `rec_vstar` refuses unless every declared rep has its stream and its proof. It had accepted that stopped
  session, and its two forged copies, with zero queries.
- 273017068: 85's inner step fails when the honest session's V* refuses (the prover reports a stop and exits 0).

## The runs (node 1, TAG=k4096s3, at 273017068)

| step | run | status |
|---|---|---|
| build | r20261006-015707-1c92 | passed: binary 5926ec47 (key 4b282b06e4d5089f), Lean be80e68d; plain inner circuit edf74947, hm96 bfce5c43 (step 2's), m = 35, k_log 24, 2,048 instances |
| inner | r20261006-021550-4e4b | passed: proxy prove 0.977 s, 856,466 bytes a rep, 278 rounds, 218 message rows, 12 salted tops (512 nodes); replay accepted; rec_vstar accepted, 1,118 openings, plain leaves; forged node and forged salt refused ("GATE-REFUSED: tree top: circuit/rep0 round 70's top 0 does not open its commitment"); M0 0.737 s; `--zk` 5.41 s prove, 7.48 s serve verify, replay --zk accepted |
| vstage | r20261006-022005-409a | passed: InnerFold --plain-leaves 1:59 at 3.0 GB, 6 extras; L0–L6 RecOpen_v3 (436/212/142/106/86/72/64 instances, 41/33/29/27/23/19/15 compressions, each 4 under v2) every opening climbed and summed; alg p0–p2 hold on both reps; forged top L6: instance (0, 0) not opened; forged top-salt L0: all opened, its `rec-top-L0` alone mismatches the entry; comb, message and sum as in step 2 |
| oprove | r20261006-024439-6203 | passed: 10 statements, each 4/4 sessions accepted by serve and by replay --zk; 13 forged sessions rejected in exactly their statements; L1 contended (serve verify 15–44 s); lease held 550 s over 23 proves, L0–L2 waited 3,474 s |
| lean | r20261006-040407-0310 | passed: every honest statement accepted, every forgery rejected in exactly its statement; `INNER_LEAN=1`: the plain inner session refused ("setup: leaf-commitment scheme flock-leaf/sha512-unsalted is not one this verifier implements") |
| oprove L1 alone | r20261006-041822-99db | passed: 0.699 s prove, 1.355 s serve verify, 4/4 and replay --zk accepted, lease 19 s, cores 18% busy |

## The answer

V* is sound on every forgery tried, on live coins.

| forgery | statement | serve and replay --zk | Lean verify --zk |
|---|---|---|---|
| top (L6, a node one bit off) | L6 | opening: RingSwitch(ClaimMismatch) | opening: ring-switch claim 8 mismatch |
| top-salt (L0, `root_B` under another salt) | L0 | opening: RingSwitch(ClaimMismatch) | opening: ring-switch claim 8 mismatch |
| comb | alg-p0 | zk inner: the batched constraint fails | the same |
| message | alg-p0 | opening: RingSwitch(ClaimMismatch) | opening: ring-switch claim 2 mismatch |
| sum | L0, L6, alg-p2 | zk inner: the batched constraint fails | the same |

Cost (medians of 3 after 1 warm):

| | prove | session | serve verify | bytes | Lean verify |
|---|---:|---:|---:|---:|---:|
| levels (step 2) | 4.682 s (4.748) | 7.869 s (7.118) | 8.949 s (6.980) | 13,775,756 (13,709,708) | 285.4 s (311.8) |
| algebra (step 2's circuits) | 3.482 s (3.151) | 7.235 s (6.553) | 12.957 s (11.468) | 5,904,284 | 152.4 s (137.4) |
| V* | 8.164 s (7.898) | 15.104 s (13.672) | 21.906 s (18.448) | 19,680,040 (19,613,992) | 437.8 s (449.2) |

- The 4 compressions saved per opening shrink each level's unit 8–20%. A level's m is k_log (23 at every level, in both
  steps) plus the log of its instance count, so m and the prover's work are unchanged at K = 4096; Lean's level verify is
  8.5% faster.
- Node 1 was busier than in step 2 (prover cores 35–63% busy before each prove, against 3–28%). The byte-identical
  algebra came out 10% slower, and the levels came out equal under that load.

What's left:
- A red-team grant and a `check --record` with lean-agreement (the coordinator's).
- `VBridge`: Lean refuses the plain-leaf inner session for want of a tag set (today's identity with
  `merkleLeaf := "flock-leaf/sha512-unsalted"`, `pinnedLeafScheme := some leafSchemePlain`, as InnerFold.lean
  `--plain-leaves` does). Its parser already takes unsalted leaves. It is a verifier change, not made.
- Reconciling with zk-gateway's `rec_live`, `rec_vstar` and 85 (different key layouts) when the branches meet.

Report: `/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/internal/rec-step3.md`.
