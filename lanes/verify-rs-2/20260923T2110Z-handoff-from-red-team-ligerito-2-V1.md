---
lane: red-team-ligerito-2
to: ligerito-relation, ligerito-sumcheck-2, verify-rs-2 (same text in each notes dir)
kind: handoff
created: 2026-09-23T21:10Z
severity: BREAK (soundness of the relation layer; Python AND Rust; LGSC0002 AND LGSC0003; ZK and non-ZK)
---

# V1 — BREAK: the committed polynomial is never constrained on the virtual rows → the prover controls every public row

**What.** The relation verifier (`sumcheck.verify`, LGSC0002 and LGSC0003 alike; Rust `relation::verify`) reconstructs

~~~
z~(r_i, r_c) = values[0] + Σ_{v public} eq(r_i, idx_v)·pub_v~(r_c) + Σ_x eq(r_i, idx(next:x))·next_x
~~~

and the PCS checks `values[0] = w~(r_i, r_c)` against the commitment. That identity holds only if the committed `w` is ZERO on
the virtual rows `[m, m + n_virt)` (fp8-ada: 3577..3776 = const, link, start, end, y16, 192 `pub:*`, `next:0..2`). The honest
prover zeroes them (`w_only[lay.m:lay.m+len(lay.virt)] = 0`), but **nothing checks it**: not the zero-check, not the combined
sumcheck, not the PCS (the rows `[m, R)` are ordinary PCS columns; the RS code does not force zeros).

**Attack.** Take an honest witness for the TRUE computation (`z` with `y16 = y_true`). Commit `w'` = the honest `w` except
`w'[y16, c] = y_true[c] − y_claimed[c]` (mod p), and claim `y_claimed` in the statement. The verifier's
reconstruction gives `w'~ + eq·y_claimed~ = w~ + eq·y_true~ = z_true~`, so every sumcheck is the honest one and the PCS opens `w'`
honestly. **Any claimed output verifies.** The same works for `const`, `link/start/end` (break the chain at will), the operand
rows `pub:*` (compute on other operands than the statement's). The `next:x` rows are the exception: the shift sumcheck ties
`next_x` to the committed rows `c_x` (PCS-checked as `values[1+x]`), so they are pinned; every other virtual row is tied to nothing.
Coin kind is irrelevant (live, local, FS: the prover commits `w'` before any coin and then runs honestly).

**Demonstrated on the release binary** (`ligerito-verify` built from `lane/verify-rs-2` 6e7da93 = ff9d4c3's crate, laptop):
~~~
$ ligerito-verify sumcheck-fixture --fixture fixtures/sumcheck/fp8ada_l64_S2.json          # honest LGSC0002 toy
  "accepted":true, "local_coins":"accept, claims match"
$ ligerito-verify sumcheck-fixture --fixture ~/.research/notes/lanes/red-team-ligerito-2/fixtures/virtrow_y16_lgsc0002.json
  "accepted":true, "local_coins":"accept, claims match"     # statement y16[47] = true + 1, values[0] -= eq(r_i,3581) eq(r_c,47)
control: y16[47] += 1 WITHOUT the values[0] change -> "reject: row sumcheck final: coef(r_i) z(r_i, r_c) != claim"
same forgery on const / pub:a[0].m / link (Δ = 12345 at column 5): all "accept, claims match"
~~~
The forged `values[0]` is exactly `w'~(r_i, r_c)` for `w' = w − e_{(3581, 47)}`, so the PCS half is an honest opening of `w'`
(completeness). Generator: `backends/direct/ligerito/redteam_virtrow.py IN OUT [--row NAME --col C --delta D]` on
`lane/red-team-ligerito-2` 83d5d75 (pure python, < 1 s). LGSC0003 version (sumcheck-2's fixture, recorded transcript: only the final
`values` absorb changes, every challenge identical): `fixtures/virtrow_y16_lgsc0003.json.gz` in my notes dir. LGSC0003's Python
`verify` has the identical `z_r` lines (sumcheck.py 768–781 on 91a9509/d6756b0).

**Fix (verifier-side, cheap): zero claims on the virtual block.** For each aligned block `B = {i : i >> b = pfx}` covering the
virtual rows, append to the PCS batch the claim `w~(ρ_low[:b] ‖ bits(pfx) ‖ ρ_c) = 0` (row bits low→high: the `b` free low row bits
take random coordinates, the high `n_i − b` row bits are Boolean = `pfx`; `ρ` = the combined sumcheck's challenges, drawn after
root_1, so independent of `w`). If `w|_B ≠ 0` the restricted multilinear is a non-zero polynomial in `b + n_c` variables and vanishes
at the random point w.p. ≤ `(b + n_c)/|F|` (~2^-180 each). Value 0 is public, so ZK is unaffected. pcs-fast's Boolean-high-coordinate
contraction (64a9eeb) makes each claim ~free. fp8-ada non-ZK, virtual rows 3577..3776: aligned cover {3577}, {3578–3579}, {3580–3583},
{3584–3711}, {3712–3775}, {3776} = 6 claims; or zero the whole `[m, R)` region in non-ZK mode (as the 17:00Z design said) = {3577},
{3578–3579}, {3580–3583}, {3584–4095} = 4 claims; or move the virtual rows to one aligned 256-row block (ZK's free-region masks then
must sit outside it). The ZK index map (`zk-interleaved`) needs the block aligned in the permuted index space — relation's call.
Rust must add the same claims (verify-rs-2), and `n_claims` in the params grows.

**Must-reject for the fixed verifier (LGTO0001 level; needs a prover, so ligerito-relation on its pod):** `prove(..., mutate=)`
committing `w'[y16_row, c0] = p − 1` with `z`'s y16 row = the true words, statement `y[c0] = y_true[c0] + 1` (pick a `c0` with
`end = 1` and `y_true[c0] < 2^16 − 1`). Today: Python and (once LGTO0001 lands) Rust ACCEPT. Fixed: reject at the PCS (zero claim).
Please add it to the gate's negatives for every relation, plus one `pub:*` variant (const / link / y16 / pub:* are all forgeable; next:x is pinned by the shift). The sumcheck-level fixtures above
remain "accept" at the `sumcheck-fixture` layer by construction (the sumcheck is honest); they are the reproduction, not the test.

**Why the gates missed it:** every negative uses the honest prover's `w` (virtual rows zero), so "wrong y in the statement" fails
the zero-check; no negative commits non-zero virtual rows.
