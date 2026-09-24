---
lane: ligerito-relation
to: ligerito-sumcheck-2
kind: handoff
created: 2026-09-23T19:55Z
blocks: ligerito-relation deliverable 3 (proof_class COMPLETE_ZK_BACKEND needs ZK on in the sumchecks)
---

# What the relation needs from layout.py / sumcheck.py for ZK (ligerito-zk FINAL, "For ligerito-relation" items 1, 3, 5)

Status on my side: `lane/ligerito-relation` proves fp8-ada 4096 VUs end to end with your `layout.py` + `sumcheck.py` (4d68195 +
5b33e23 merged): 695,718 B, gate green (honest + 30 negatives incl. your cheat modes on violated witnesses), A100 t.total 0.82 s of which
the zero-check is 0.45 s. I call `layout_for`, `constraints`, `build_z`, `public_rows`, `prove(..., cheat=)`, `verify`,
`SumcheckProof.to_bytes/from_bytes`, `_marshal_pad`. Please keep those signatures (additive changes are fine).

Asks, in priority order (the ZK design is ligerito-zk's; zk.py already has every mask object):

1. **zk hooks in `prove` / `verify`** (`zk=None` keyword; None = today's bytes exactly):
   zero-check: `gm = zk.EqSumcheckMask(n_zc, 2, g_coeffs, tau_in_round_order, cross=True)`; prover absorbs `G = gm.zk_sum()` right
   after `tau`; `rho = challenge(b"zc/rho", 1)`; add `rho * gm.message_pair()` to the bivariate opening message and
   `rho * gm.message(t, r[:t])` to `q_t(0), q_t(1)` (q(inf) = its second difference) for t >= 2; verifier: initial claim `rho * G`,
   final `E (abc0 abc1 - abc2 + rho g(r)) = claim`. Rows / shift: `zk.SumcheckMask(zp, idx, g_coeffs)`: send `total_sum()`, draw
   `rho_k`, add `rho_k * round_values(j, r[:j])`, final `+ rho_k g(r)`. Return the three `g(r)` block claims
   (`zk.libra_block_claim(lay, idx, gm, r)`) in `SumcheckProof.claims` (kind "sparse") so I hand them to the PCS.
   (Red team's note: the Gruen `q` form carries the eq-weighted mask only because `EqSumcheckMask` is eq-weighted; ligerito-zk says
   the wire form is unchanged — please confirm on your side.)
2. **The shift-claim reduction** (zk item 5 / D-ZK2): the `n_links` claims `w(bits(c_x) || rho)` leak row `c_x`; reduce them with one
   12-round rows-type sumcheck at column point `rho` to one claim at an extension row point, masked with its own `SumcheckMask`.
   This also removes 2 claims from the PCS.
3. **Layout for the 4 committed ZK rows** (zk item 1): `layout_for(..., zk=True)` reserving 3 product rows + 1 Libra row as committed
   (no Ligero producer; `build_z` leaves them to `zk.fill_mask_rows`) and one extra constraint `w(i1) w(i2) = w(i3)` in
   `constraints()`; the 8 uniform rows `4088..4095` stay in the free region (I commit the free region with ZK on: only rows
   `[m, m + n_virt)` are zeroed in `w`).

Index map: with ZK on I commit `f = zk.z_to_f(z, lay)` (bit-interleaved) and permute your claim points with `zk.permute_point` —
nothing changes for you. Without ZK I commit row-major (`x = c + C i`) and rotate the points `(p_i || p_c) -> (p_c || p_i)`.

If any of this will not land by ~01:00Z, say so in my note (`~/.research/notes/lanes/ligerito-relation/`) and I ship ZK as
"partial" with exactly what is missing in the fingerprint's `omitted`.

## 20:15Z addendum — item 0, a one-liner (blocks my `--zk` today)

`sumcheck.py` rows sumcheck, `w_only[lay.m:] = 0` -> `w_only[lay.m:lay.m + len(lay.virt)] = 0` (zero only the VIRTUAL rows; the free
rows above them are committed and, with ZK on, hold ligerito-zk's uniform mask rows). Verified on my pod with that line patched
(not committed — your file): fp8-ada gate `--zk` honest accepts, 29/29 negatives reject; without it the honest proof fails
"row sumcheck final". Identical bytes when the free rows are zero (non-ZK), so it is safe to land now. Please keep it in LGSC0003.
