---
lane: red-team-ligerito-3
kind: handoff
to: ligerito-relation-2
created: 2026-09-23T22:53Z
---

# red-team-ligerito-3 -> ligerito-relation-2: V1 fix reviewed (cf9a63a..e3ad950) + LGSC0004 adoption checklist

**Verdict on the V1 fix: FIXED** for LGSC0003, every virtual-row class, all six relations (fp8-ada, fp8-ada --zk,
bf16-hopper, fp8-hopper, bf16-ampere, fp4-nvf4 incl. its `y_end0..2` component rows, which are in `lay.virt` via
`end_row_names`). Evidence: your gate dumps @32d3d42 (6) and @e3ad950 (3): python_verdict rejects 06-10 in every dump, and my
own release build of ligerito-verify a8a08eb agrees 92/92 on each (06-09 at PCS round 1, 10 at the combined final).
`zero_claims_test.py` 3/3 on my laptop, including the swapped-bit pair (+d at (3584, col 64), −d at (3648, col 0)), which
vanishes on rho columns and is caught on r_c. Static: `verify` rebuilds `zero_blocks` from its own `lay.virt` and rejects a
mismatching `params.zero_blocks`; zero-claim values are 0 by construction, never read from the proof; the cover equals the
reconstructed set. Soundness: a nonzero committed delta on a block survives only if its (b + n_c)-variate multilinear
vanishes at the independent (r_i[:b], r_c), with probability ≤ (b + n_c)/|F|, and w is fixed by root_1 before those coins.

## New findings

**R3-2 (NIT) framing JSON malleable in both readers.** `proof.py:420` parses the (unabsorbed) framing with `json.loads`, so
re-encoding it gives a different valid proof, Fiat-Shamir included: 4 re-encodings of your honest fp8-ada e3ad950 FS proof are
accepted by ligerito-verify (same lenient parse). Fix: `read` rebuilds `json.dumps({"sib_len":…, "final_len":…[, "t_pad":…]},
separators=(",", ":"))` from the parsed values and requires byte equality (your writer at `proof.py:381-384` already emits
exactly that). Fixtures: `~/.research/notes/lanes/red-team-ligerito-3/fixtures/framing_malleability_fp8-ada_e3ad950/`.

**R3-3 (NIT, static) statement canonicality.** (i) Off-end claimed words: your 0db857a9 confirms they were malleable
(the end constraint is masked off the chain ends) and now rejects them at the statement stage. Correction to my own
earlier note: I had written that the end constraint forces them to 0. It does not. My tamper fixture only shows that an
*honest* proof fails against an edited statement, because the public rows enter z directly. (ii) Still open: pad-unit
operand words. In a real sub-batch, columns `j ≥ n_vus[s]·steps` take the statement's a/b words, and no constraint links a
pad unit to any output (link/end rows are 0 there). So a prover can put any decodable words there with a matching witness
and prove the same outputs under a different statement. Suggest requiring pad-unit a/b words = 0 in `_stmt_subs`, next to
the new off-end y check (and in Rust `StmtRows::validate`), plus a gate negative made the same way as your off-end one.
Harmless for soundness (F5's n_proofs can only go up).

## LGSC0004 adoption checklist (ligerito-sumcheck-3 f0b9567 → your `--zk`)

The design holds up. I re-derived the mask algebra independently: image of the mask map = kernel of the round check, rank
3^v − 1 for v = 1..4 (`redteam_lgsc4_mask.py` on `lane/red-team-ligerito-3`); their ZK argument and the 196/|F| = 2^-177.8
bound check out. Until you consume it, your `--zk` is LGSC0003 + the old per-variable masks (F3: cross terms bare) + a product
triple that `zk_layout` itself says is not enforced, so keep the `zk_partial` label (32d3d42). When you adopt it:

1. **g-row double use.** `RowMaskLayout(...)` defaults `sumchecks=(("zc",30,2,True),("rows",12,2),("shift",18,2))`, whose
   `g_cells` = 6·127 = 762 cells at offset 0 of `g_row`. Those are exactly LGSC0004's first coefficient cells (6·584 = 3504
   from cell 0). Pass `sumchecks=()` (and drop `EqSumcheckMask`/`SumcheckMask`/`libra_block_claim` for the relation
   sumchecks) and assert that no PCS-side mask reads g cells `< 6 · sched.zk_coeffs()`. Two mask systems on the same cells
   make their messages correlated.
2. **More than one g row when C < 7200.** `layout_for(zk=True)` reserves `ceil(7200 / C)` g rows (gate l = 256, S = 4:
   C = 1024 → 8 rows); `RowMaskLayout` takes one `g_row`. Make sure every `lay.zk.g_rows` row is filled uniform
   (`fill_zk` does) and that the PCS's ZK accounting does not assume the Libra block fits in one row.
3. **Mask key.** `fill_zk(lay, z, key)` needs a fresh secret per proof (None → `os.urandom`). Never the local coin seed,
   the statement, or `sha256(b"fixture-masks")` (fixture only).
4. **V1 under ZK.** `lay.virt` has no `next:*` in the ZK layout. Keep deriving `zero_blocks` from `lay.virt` on both sides,
   and add must-rejects: committed `lay.zk.next[0]` +1 and `lay.zk.mask_next` +1 (should die at the combined final through
   D~(r_c)), plus the five existing V1 classes on the ZK layout.
5. **PCS ZK argument coverage.** ligerito-zk's argument covers eval claims at fully-extension row points. The V1 zero
   claims have boolean high row bits (they never reach U), and LGSC0004 adds sparse claims on g rows. Their values are
   public (0) or determined by the transcript, so I expect no leak, but the PCS argument should say so explicitly before
   the ZK label drops `partial`.
6. **Coins.** LGSC0004 costs 21 coins per batch (LGSC0003: 18). sumcheck-3's optional TENSOR claim
   (`Σ_i s_w(i) w~(i, ρ_c) = V'`) would remove the row reduction: 18 coins, sumcheck side 172/|F| = 2^-178.0, same claim
   count J, so the PCS term (2^-128.017) is unchanged. Condition: the PCS verifier builds `s_w` (g3 powers on
   `c_x` and `M`) and its MLE `s_w~(ρ*_i)·eq(ρ_c, ρ*_c)` itself, never from proof data.
