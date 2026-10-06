---
id: outer-shape/20261006T0841Z-finding-outer-shape-cap
campaign: proof-service
lane: outer-shape
kind: finding
status: open
repo: danielreuter/verity
origin: bc-8416bc72 (proofs)
---

# Outer proofs of one fixed shape: the inner statement padded to a public cap

PR #1315 (`cursor/outer-shape-95d4`, head `e3f7a643a`, base rec-step3's #1284). The PR body is
`internal/proofs/outer-shape-pr.md` in the proofs coordinator's store.

## Question

Can every outer proof of a deployment have one shape, whatever the inner statement's size? And does it still verify under
serve, upstream `replay --zk` and Lean `verify --zk`, with rec-step3's forgeries rejected and a forgery in a filler slot
rejected too?

## Answer

Yes, by padding the inner statement to a public cap. V*'s statements are a function of the inner table's shape, (m, k_log,
claims), alone. A deployment fixes the cap: instances, claims, k_log and vus_per_block, all public items. Every inner
statement is padded to the cap's instance count with filler instances, so V* over any session has the cap's statements.
`rec_vstage --cap` refuses a session of another shape before anything is staged. A filler's input rows are zero and its
output is the class lowering's own (`outs[real:] = got[real:]` in `stage`). Staging's satisfaction check covers it; unlike a
real instance's output, it isn't compared with the reference evaluator's.

The padding hides the outer proof's shape and cost, not R. The inner statement's public file, `pub-N.bin`, still shows R: its
header's `shared_rows` (p1 has R + 1 rows, p0 2 where unpadded has 1) and its refs (every filler's p1 ref is row R, the real
ones rows 0 to R − 1). Serve, `replay`, Lean and V*'s verifier values (`v`) all read that file.

At K = 4096 the cap is `instances=2048,claims=8,k_log=24,vus_per_block=1` (m = 35). An inner statement of 1,024 real
instances padded to 2,048 has V*'s statements identical to rec-step3's over an unpadded 2,048: the same templates, instance
counts and circuit SHA-512s, and the same 19,680,040 proof bytes.

I didn't pad V*'s own statements: their counts are already fixed per m, and across m the templates, level count and algebra
differ. I didn't add a combining step either: it costs roughly ten times the outer prove, and it is fixed only if V* is.
VBridge's statement and the pinned Lean guarantees are unchanged, because the padded statement implies the unpadded one.

## Numbers (node 1, medians of 3 after 1 warm, one GPU lease per prove; sums over V*'s ten statements)

| | prove | session | serve verify | bytes | Lean verify |
|---|---|---|---|---|---|
| V* at the cap (padded 1,024 to 2,048) | 7.894 s | 14.389 s | 20.009 s | 19,680,040 | 389.4 s |
| rec-step3 (unpadded 2,048) | 8.164 s | 15.104 s | 21.906 s | 19,680,040 | 437.8 s |

The circuits and bytes are the same, so the gap is node load: 1-minute load average 48–134 at each step's start, and the
prover's cores 11–45% busy before each prove (L1 100%). Lean verify is the session's verify time from Lean's stderr, as
rec-step3 reports it. The padded inner (ZK off, against the proxy) proves in 0.86 s; rec-step3's took 0.977 s. Today's
`--zk` on the padded statement takes 4.90 s prove and 7.66 s serve verify.

## What the cap costs a statement below it (R = 1,024 unpadded, at its own m = 34)

V* over the unpadded 1,024-instance session has 7 levels (each RecOpen template's H one smaller) and an algebra of 4 parts,
11 statements. Every verifier accepts all 11: serve 4 of 4 sessions each, upstream `replay --zk`, Lean.

| R = 1,024 | statements | prove | session | serve verify | bytes | Lean verify |
|---|---|---|---|---|---|---|
| V* at the cap (m = 35), padded | 10 | 7.894 s | 14.389 s | 20.009 s | 19,680,040 | 389.4 s |
| V* at its own m = 34 | 11 | 10.214 s | 30.471 s | 50.602 s | 21,610,780 | 789.7 s |
| levels at m = 34 | 7 | 4.670 s | 7.377 s | 8.110 s | 13,663,116 | 570.3 s |
| algebra at m = 34 | 4 | 5.543 s | 23.094 s | 42.492 s | 7,947,664 | 219.4 s |

The inner (ZK off, against the proxy): padded 0.860 s prove, 856,466 bytes a rep, peak 20.65 GB; unpadded 0.523 s, 820,402
bytes, 12.98 GB. So at R = 1,024 the cap costs the inner prover (0.34 s, 7.7 GB), not V*: the outer proof under the cap is
one statement and 1,930,740 bytes smaller. Node 1 was busier for the unpadded run (load 71–309, prover cores 31–100% busy
before each prove), so its session, serve and Lean times aren't like for like; the counts and bytes are. 12 GPU leases, 353 s.

## Forgeries (provers with FC_ZK_SELF_CHECK=skip; serve, replay --zk and Lean agree on every session)

- top → L6, top-salt → L0, comb → alg-p0, message → alg-p0, sum → L0, L6 and alg-p2: exactly rec-step3's statements.
- filler (new): filler slot 1,024's output row has one bit off. The M0 prover gives a session without stopping, and V*'s
  hashing reference (`rec_vstar`) accepts it, because its openings are the prover's own. V*'s algebra does not hold: parts 0
  and 1 are false in both reps, part 2 true. Serve, replay --zk and Lean reject alg-p0 and alg-p1 ("zk inner: the batched
  constraint fails") and accept alg-p2. So V* refuses the session.

## Evidence

- `r20261006-071140-5b44`, the build (run record art:6a5cb3f9124fe4419d2612a0790ce9972f9bf8f8e0c85e7943791774dfa0d277):
  the stage record shows 1,024 real and 1,024 fillers, k_log 24, vus_per_block 1.
- `r20261006-072405-f1ba`, the padded chain (run record art:9a29e3c3cfa1b4d8a8cab7c2e4d73638789c48bae8ce093098526647c0242a35):
  inner, staging with the five forgeries, outer proves, Lean.
- `r20261006-073154-8c34`, the filler forgery (run record art:8da350a8ffde73da3a28ed3886a0f33f638ede7b7a81c8000038d4a3a7217cad).
- `r20261006-084418-1684`, the unpadded 1,024-instance chain at m = 34 (run record
  art:375c5efdd17fdd31a375b1c44e0e0f322906a9a7e2461caa12adaf8500e67b33).
- rec-step3's reference: oprove art:1157c1c5e86c21f802bf2dae5018e9389910aa8a41d015e3f9661268355701b2, L1 rerun
  art:de6a699580e6c1b1c31b23750ec84cfc0927438f77fc5bdc40fe0201527fde1b, and lean
  art:bb95919c70f13489c9605a85153d6843e531692a08cc90264f1d587c4fd3c518. The same aggregation reproduces its totals.

## Open

- Hiding R: needs a layout for the fillers' rows whose public file (table sizes, refs) is the same for every R, with V*'s
  verifier values computed from it.
- Nothing on the verifier's side checks the cap; only `rec_vstage --cap` (the firewall's side) does. A verifier holding the
  cap would compare each outer statement's template, instance count and SHA-512 with `rec_shape.outer(cap)`'s (digests
  rebuilt) before serve or Lean.
- Wired (template-instance) statements aren't padded; `stage(pad=...)` refuses them.
- The cap is opt-in (`--cap`/`REC_CAP`, `--real`/`FLOCK_REAL`). `rec_shape.check` doesn't read the inner instance count, so
  an unpadded 1,025–2,047 passes it. Only one R is measured at the cap. Small-R timing variation (fillers share one committed
  row per port) belongs to P2, the firewall's stop bound.
- `85-rec-reprice.sh STEP=inner` with `WARM=0 RUNS=1` looks for `inner/s0`, but `rec_live --sessions 1` writes `inner/`.
  The filler job worked around this with `INNER=`. The fix goes to zk-gateway's next round, since #1270 edits that file.
