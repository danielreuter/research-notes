---
lane: verify-rs-2
to: ligerito-relation (cc red-team-ligerito-2, ligerito-sumcheck-2)
kind: handoff
created: 2026-09-23T21:15Z
branch: lane/verify-rs-2 @ e38a0c7 (pushed; worktree ~/projects/verity-main-wt/verify-rs-2, crate backends/ligerito-verify)
---

# verify-rs-2 → ligerito-relation: F10 landed (ref v2 transcript), LGSC0003 verified, V1 zero claims (use `r_c` columns, NOT ρ)

## 1. What landed (all on `lane/verify-rs-2`, `cargo test --release` 60/60 = 56 lib + 4 CLI)

| commit | what |
|---|---|
| 5611872 | **F10 + F11**: `ligerito-ref/v2` in `ref.py` (patch committed on this branch; design lane ended) and `refpcs.rs`: the statement is absorbed before the first coin; v1 refused; every field word must be a plain integer in `[0, p)` |
| c209c61 | **F5**: `--n-proofs N` (verify: each proof ≤ 2^-(B + log2 N); batch: exactly N accepted + union ≤ 2^-B; or `manifest.json` `"n_proofs"`) |
| 4bf4476 | **LGSC0003** (`src/lgsc3.rs`): sumcheck-2's fixture (1fbbe86, sha256 019869b0…) accepted with the recorded transcript (every absorb byte-checked) and with `LocalCoins(b"fixture")`, claims equal; its 6 negatives rejected in the same stage |
| 564fc65 | **V1 verifier side**: `relation::virtual_zero_claims(layout, &claims[0])`: the zero claims your PCS batch must open (§3) |

## 2. ref.py v2 transcript order (the F10 fix; `ref.py` docstring and `refpcs.rs` header carry the same text)

~~~text
FSCoins(seed = b"ligerito-ref/v2")
absorb("stmt/dims",  u32 L || L x (u32 tall, u32 wide_log2, u32 n_log2, u32 queries))
absorb("stmt/w",     u32 D || D x (u32 radix || radix x 6 u32))      # the tensor point, digit 0 first
absorb("stmt/value", 6 u32)                                          # the claimed <f, w>
then as v1: per level absorb(root_i); i >= 2: indices(S_{i-1}), absorb(rows || siblings), challenge(1 + |S|);
per column digit absorb(c0 c1 c2), challenge(1); after level L: absorb(v_L), indices(S_L), absorb(rows || siblings)
~~~

Your LGTO0001 already binds `lgto/params`, `lgto/stmt` (sha256), `lgto/vk` (sha256) before `root_1`, and the claim points
enter via `absorb("z")` after the zero-check. That is the property F10 was missing, so **keep that order** in `proof.py`.
F11 for LGTO0001: every u32 on your wire that is a field word must be `< p`. A lifted `x + p` must be rejected, not reduced.
Please confirm `proof.py`'s reader rejects it; `refpcs.rs` / `lgsc3::parse` / `relation::parse_lgsc` do.

## 3. V1 (red-team-2): the zero claims, and one correction to the proposed rule

Rule implemented in Rust (`relation::virtual_zero_claims`, test `virtual_rows_get_zero_claims`). For every aligned block
`{i : i >> b = pfx}` of an aligned cover of each run of virtual rows (fp8-ada: 3577 | 3578-79 | 3580-83 | 3584-3711 | 3712-75 |
3776, i.e. 6 claims), add to the PCS batch

~~~text
w~( r_i[..b] || bits(pfx, n_i - b) || r_c ) = 0          # row bits low->high, then columns (sumcheck order; rotate for the PCS)
~~~

where `(r_i || r_c)` is the point of the FIRST claim (`w(r_i, r_c)`, `values[0]`). Here `r_i` comes from the rows / combined
sumcheck and `r_c` from the zero-check. Both are drawn after `root_1` and independent of each other, so a non-zero `w|_B` passes
with probability at most `(b + n_c)/p^6`. The value 0 is public, so ZK is unaffected. `J` grows from 4 to 10 for fp8-ada.

**Do not take the columns from the combined sumcheck's ρ** (the handoff's `ρ_low[:b] ‖ bits(pfx) ‖ ρ_c` with `ρ_c = ρ[:n_c]`).
Row bit t and column bit t then share one coordinate, so two entries with those bits swapped cancel identically:
`x0(1-y0) - (1-x0)y0 = 0` on `x0 = y0`. Concretely, `+Δ at (row 3584, col 64)` and `-Δ at (row 3648, col 0)` is non-zero on
block 3584..3711, but its multilinear vanishes at every `(ρ[..7] ‖ bits(28) ‖ ρ[..7])`. Test
`zero_claim_columns_must_be_independent` checks this for any ρ, and checks that the `r_c` rule catches it.

This is exploitable whenever the compensating row is harmless. Examples: an unconstrained padding row when zeroing the whole
`[m, R)` region (the pub row at row_low `128 + j` with column bit 6 = 1, compensated at padding row_low `192 + j`), or a second
row the attacker also wants to forge.

The ZK index map is your call (blocks in the permuted index space). Please add the red team's `prove(..., mutate=)` negatives
(y16, one `pub:*`, one `next:x`) to every gate. On the Rust side the claims are ready; there is no LGTO0001 PCS path to open
them yet (§5).

## 4. CLI (release binary `backends/ligerito-verify/target/release/ligerito-verify`)

~~~text
ligerito-verify sumcheck-fixture --fixture F.json [--seed fixture]
    # LGSC0002 or LGSC0003 by magic; recorded transcript + LocalCoins(seed); claims must match; the fixture's "negatives"
    # rejected in Python's stage; prints "virtual_zero_claims": [...]. Exit 0 iff all of that holds.
ligerito-verify ref-fixtures --file F.json [--neg N.json]      # ref.py v2 fixtures, verdict-for-verdict (conformance only)
ligerito-verify batch --dir D [--target-bits B] [--n-proofs N] # *.proof must accept, *.proof.neg must reject (JSON = ref v2
                                                               # fixture lists), union <= 2^-B, exactly N accepted
ligerito-verify verify --proof X.proof [--target-bits B] [--n-proofs N]   # one proto-dialect PCS proof
~~~

`batch --dir backends/ligerito-verify/fixtures/forged --target-bits 0` exits 0: 52/52 forged rejected, 3/3 honest accepted.

## 5. Not done: LGTO0001 reader (your deliverable 2 stays blocked on it)

Needed pieces, as I see them:
- LGTS0001 / LGVK0001 parsers.
- Per-relation `public_vectors` decoders (fp8/bf16/fp4 operand decode, as ligero-verify's `public_pins_words`). This is the
  big one.
- proto PCS with J eq terms and your transcript (`pcs.rs` has the one-claim proto verifier).
- `lgsc3`/`relation` for the zero-check, plus the zero claims above.

I estimate 3-4 focused hours; it is not in tonight's scope for this lane. The pieces above are the reusable parts.
