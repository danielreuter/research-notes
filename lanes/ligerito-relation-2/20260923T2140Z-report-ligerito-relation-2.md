---
lane: ligerito-relation-2
kind: report
created: 2026-09-23T21:40Z
status: superseded
branch: lane/ligerito-relation-2 (worktree ~/projects/verity-main-wt/ligerito-relation-2, from lane/ligerito-relation @ fbc3eef)
owns: backends/direct/ligerito/{prove.py, proof.py, run.py} (+ tests beside them)
pods: vy-ligerito-relation-2 52tgms6kjphi6k (RTX 4090 reference part, $0.74/h, created 21:44Z)
---

CHECKPOINT 0b40ae8a (05:54Z) [superseded] closed by coordinator 2026-09-25 05:55Z for the cloud switch-over: no sign of life >24 h; branch lane/ligerito-relation-2 pushed to origin; uncommitted work (if any) saved in evidence/uncommitted-0554Z*
CHECKPOINT none (22:25Z) [open] V1 fixed (cf9a63a); F12 labels (32d3d42); 4090 one-batch fit via streamed commit (abd8f5e). Gates 6/6 relations 0 failures @32d3d42 (4+90 each), fixtures on R2. fp8-ada 4096 one batch: 4090 0.566 s / 16.0 GiB, H100 0.398 s; H100 bf16-hopper 0.688 s, fp8-hopper 0.393 s. Next: live R + session, verify-rs-3 handoff
CHECKPOINT 9a3823a (22:00Z) [open] V1 fix committed cf9a63a (zero claims = Rust cover, cols from r_c; 5 must-reject forgeries); sumcheck-2 1fbbe86 merged 64d…; all-relation gates running on L40S; 4090 bootstrapping
# ligerito-relation-2 — V1 fix, one-batch 4096-VU numbers on LGSC0003, live coins, honest labels

CHECKPOINT fbc3eef (21:45Z) open — worktree created at fbc3eef, predecessor's V1 patch applied (uncommitted) + redteam_v1_test.py copied; 4090 pod up, bootstrapping. Predecessor branch unchanged since fbc3eef (no second writer).

## Log

* 21:38Z read relaunch §0/§2, Ligerito brief §9, predecessor report, handoffs (red-team-2 V1, verify-rs-2, sumcheck-2), sumcheck-2 FINAL.
* 21:41Z found an orphan pod of the dead predecessor: `vy-ligerito-relation-dev` lkdd6gndttgewf (L40S, $1.09/h, idle, running its
  fbc3eef gates at 21:13-21:16Z: fp8-ada / fp4-nvf4 / fp8-ada --zk 80 negatives 0 failures each; its tree = the saved patch, byte-identical).
  Nothing unrecorded on it. Will terminate it (not in any brief).
* Saved patch vs verify-rs-2's corrected rule: `zero_points` copies the first claim's point `(r_i || r_c)` and overwrites row bits
  `[b, n_i)` only, so the column coordinates ARE the zero-check's `r_c` (correct); its docstring wrongly says `rho_c`. The cover differs
  from Rust's `relation::virtual_zero_claims`: non-ZK covers all of `[m, R)` (4 blocks for fp8-ada), Rust covers each run of virtual rows
  (6 blocks), both modes. Aligning Python to Rust (one rule, both modes).
* 21:48Z laptop -> pod uploads crawl (4090 in NO: ~60 KB/s; L40S ~0.4 MB/s). Changed plan: kept the orphan L40S one more hour as the
  dev/gate box (it already has the fbc3eef tree + built CUDA extensions), shipped the 4090's tree pod-to-pod from the L40S (tar | ssh,
  seconds). L40S is now listed under pods; terminates when gates + fixtures are pushed.
* 21:55Z **V1 fix committed `cf9a63a`**. What changed vs the saved patch:
  - `aligned_cover` / `zero_blocks` / `zero_points` moved to `proof.py` (numpy only; the verifier and the laptop tests import them).
    Cover = Rust's rule: each maximal run of virtual rows `[a, b)` in `[m, R)` covered by the fewest aligned power-of-two blocks,
    both ZK and non-ZK. fp8-ada (m=3577, virtual rows = one run [3577, 3777)): 6 blocks, `[3577,3578) [3578,3580) [3580,3584)
    [3584,3712) [3712,3776) [3776,3777)` (read back from the dumped proofs' `params.zero_blocks`; the row ranges in this line
    were wrong until 22:30Z) — identical to `relation::virtual_zero_claims`. The free rows `[3777, 4096)` are not
    zero-claimed (no constraint or public row reads them).
  - Column coordinates of every zero claim = the zero-check's `r_c` (copied from claim 0's point `(r_i || r_c)`; only the row bits
    are rewritten). New laptop test `zero_claims_test.py` shows the swap counterexample: a witness nonzero at (row bit j, col bit k)
    and minus at the swapped pair cancels under `(rho || rho)` coordinates and is caught under `(rho || r_c)`.
  - Prover bug the patch had (found on the L40S, `AssertionError: prover-side claim mismatch` in PCS round 2): the non-ZK path re-zeroed
    `z[virt]` AFTER the sumcheck and before `pcs_open`, so the PCS's `M1` (a view of `z`) no longer matched the committed codeword on a
    forged run. Now `z`'s committed rows are fixed once, before the commit.
  - Must-reject V1 forgeries (`run.v1_forgeries`, used by the gate and by `redteam_v1_test.py`): the sumchecks run honestly on the
    prover's `z` while the committed w is nonzero on a virtual-row class (the verifier rebuilds those rows from the claimed statement,
    which differs): (a) end rows: claimed y +1 ulp, true witness; (b) `pub:*` rows: an operand exponent bit flipped in the statement;
    (c) start/link/end rows: statement `n_vus[0] - 1`; (d) `const` + every public row: last VU of sub-batch 0 zeroed in `z`, its y
    claimed +1; (e) `next:0` row +12345 in column 5 of the committed w. (a)-(d) must reject at "PCS" (the zero claims), (e) at
    "combined final" (next rows are pinned by the shift). With `zero_blocks` monkeypatched to `[]`, (a)-(d) VERIFY — the break
    reproduced — and (e) still fails the combined final.
  - `soundness()` adds the zero-claim term only when there are zero blocks (log2(0) otherwise).
