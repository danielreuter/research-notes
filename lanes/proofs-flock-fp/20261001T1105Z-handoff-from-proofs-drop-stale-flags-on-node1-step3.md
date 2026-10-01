---
id: 20261001T1105Z-handoff-from-proofs-drop-stale-flags-on-node1-step3
campaign: overnight
lane: proofs-flock-fp
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# Node-1 step-3 points carry two stale flags: drop them in the roll-ups

to: proofs-flock-fp. From proofs. Follows `…1050Z-handoff-from-proofs-memory-requests-64-128`.

- **The flags:** your node-1 step-3 points carry `verifier-fold-unreviewed` and `lincheck-partial-unreviewed`. These are
  K=2048 E4M3, MXF4 and NVF4 (`r20261001-104549-e156`, `-104747-da44`, `-104819-3aad`) and K=4096 NVF4 and MXF4
  (`-104909-ea52`, `-104940-8f95`). The flags come from `gemm_hill.py` lines 320–321 in tree `proofs-flock-fp-s3m`
  (`535d20a`), which fires both whenever `CscCircuit` and `pub enum Lincheck` are present. That predates your grant fix.
  Both are granted (`…0910Z-handoff-from-proofs-fold-and-lincheck-granted-drop-both-flags`), so drop them from these points.
  Do the same for K=4096 E4M3, K=8192 and K=16384 when they land, exactly as you did for node 2's step-3 points.
- **Why it matters:** these become node 1's FP bests, and they beat node 2's step 3:

  | Cell | Node 1, step 3 | Node 2, step 3 |
  |---|---|---|
  | NVF4 K=2048 | 8.72e7 | 9.19e7 |
  | NVF4 K=4096 | 9.01e7 | 9.03e7 |
  | MXF4 K=2048 | 8.91e7 | 8.98e7 |
  | MXF4 K=4096 | 8.68e7 | 9.24e7 |
  | E4M3 K=2048 | 4.48e7 | 4.56e7 |

  Reply with the five points re-labelled (and the later ones as they land), or say why a flag stands.
- **No re-place:** the MXF4 and NVF4 K=2048 points ran at 200 GiB (ended rc 0 at 10:49Z), so I placed nothing. K=16384's
  two went in at 200 GiB too. Leave them; 128 GiB at K ≥ 8192 is for anything new.
- **Packed frame:** no yes from the research owner yet (`1790847605.189759`). I asked infra to delete your two pending
  pack stages (`fp-pack-stage-k2048-{nvf4,e4m3}`). Keep the held 11 held.
- **Cutoff:** nothing new after 11:55Z. Infra is asked to delete any `nd-proofs-*` still pending in `provers` then.

**Addendum, 11:10Z,** after reading `note:proofs/20261001T1105Z-handoff-from-proofs-flock-fp-step3n1-in-two-misses-fixed`:
the packed-frame line above is withdrawn. You had already deleted both pack stages, and the CPU build was allowed at 2:38 AM
PDT (no GPU points before the owner's yes). Your feeder's rule stands: pack stages go back one at a time, only after your GPU
points are out and none of proofs' waits, nothing after 11:55Z, and none whose wall ends past 12:10Z. The stale-flag
relabel above still applies.
