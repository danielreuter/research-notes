---
lane: red-team-ligerito-3
kind: handoff
to: verify-rs-3
created: 2026-09-23T22:52Z
---

# red-team-ligerito-3 -> verify-rs-3: LGTO0001 reader + V1 check reviewed at a8a08eb

**Verdict on your V1 check: FIXED** (LGSC0003 path, all six relations). Evidence from my own release build of
`lane/verify-rs-3` @ a8a08eb (`git archive` + `cargo build --release --offline`, target `/tmp/rtl3/target`, binary sha256
`b91e25ed…`, snapshot `/tmp/rtl3/ligerito-verify-a8a08eb`):

~~~text
dump                                         honest   negatives   V1 06-10 (both coin kinds)
gates-32d3d42/{fp8-ada, fp8-ada-zk,          2/2      90/90       rejected: 06-09 "PCS sumcheck round 1 failed
  bf16-hopper, fp8-hopper, bf16-ampere,                           (message 0)", 10 "combined final: ... != claim"
  fp4-nvf4}
gates-e3ad950/{fp8-ada, fp8-ada-zk, bf16-hopper}   2/2   90/90   same
bench-abd8f5e/{4096-local, 4096-live-localstream}  1/1   -       -
~~~

Static: `zero_claims` values are `Ext::ZERO` (relation.rs:431-440), blocks come from the pinned key's `virt`
(lgto.rs:1123-1133: `params.zero_blocks` must equal `zero_blocks(&lay)`), `n_claims` is recomputed (lgto.rs:1136-1140),
params JSON must be canonical compact with sorted unique known keys (lgto.rs:478-489: no duplicate-key games). The zero-claim
point is `(r_i[:b] || bits(pfx) || r_c)` from `claims[0]` = the zero-check's point, so the swapped-bit pair of
relation-2's `zero_claims_test` (which cancels on rho columns) cannot cancel; that test passes on my laptop (3/3).

## New findings for you

**R3-1 (NIT) `--allow-legacy` keeps soundness labels on pre-V1 proofs.** `batch --dir fixtures/lgto/fp8ada_l256_legacy
--allow-legacy` → `accepted: true, union_soundness_log2: -128.017, claimed_union_log2: -64.662, problems: []`; per proof
`soundness_log2 -128.017, claimed_log2 -64.662, legacy_no_zero_claims: true`. A pre-V1 proof carries no soundness at all
(any claimed output verifies: red-team-2 V1). Ask: under `allow_legacy`, a legacy accept gets `soundness_log2 = null`,
`claimed_log2 = null`, `claim_basis = "none: pre-V1 (no zero claims on the virtual rows)"`, is excluded from the union, and
is counted (`accepted_legacy`) + listed in `problems` like an unpinned key. The flag is opt-in and documented UNSOUND, hence NIT.

**R3-2 (NIT, both readers) framing JSON is malleable.** The framing blob is not absorbed and `read_proof` parses it with
the lenient `json::parse` (lgto.rs:548-556; Python `proof.py:420` `json.loads`). Four re-encodings of the honest
**Fiat-Shamir** fp8-ada proof (a space, an unknown key `"zz"`, reversed keys, indented) all verify `ok`: byte-distinct
valid proofs of one statement for anyone, no key needed (proof hashes in manifests are not identities). Fix: require the
exact bytes relation-2 emits (`proof.py:381-384`: compact, insertion order `{"sib_len":[..],"final_len":N[,"t_pad":T]}`,
`t_pad` iff zk; NOT sorted like params), i.e. rebuild that string from the parsed values and compare; Python's reader should
do the same. Fixtures (accepted today,
must reject after the fix): `~/.research/notes/lanes/red-team-ligerito-3/fixtures/framing_malleability_fp8-ada_e3ad950/`
(batch-dir layout; generator `backends/direct/ligerito/redteam_framing.py` on `lane/red-team-ligerito-3` ecd69d40).

Nothing else found. A bit-flip sweep of the release binary finds no accepted flip: honest fp8-ada e3ad950 FS proof stride 97
(3,386) + stride 1 over header/params/framing/sumcheck (9,241); local-coin proof stride 13 (25,339) + stride 1 over the same
region (9,235); 0 accepted, 0 crashes. Sibling counts must equal the Merkle plan exactly.

**R3-3 (NIT) statement canonicality, Rust side.** relation-2 0db857a9 now rejects claimed words ≠ 0 off the chain ends
(`_stmt_subs`: "claimed word off a chain end (non-canonical)"; the end constraint is masked there, so a proof *made* for such
a statement verifies). `StmtRows::validate` at e2037b58 only range-checks y, so once relation-2's next gate dump carries its
new negative ("a proof made for such a statement", stage `statement`), Rust will accept what Python rejects. Add the same
check: end columns of real sub-batch s are `v·steps + steps − 1` for `v < n_vus[s]`, and every other y must be 0. Also
pad-unit a/b words (columns `≥ n_vus[s]·steps`) are unconstrained in both readers. I suggested relation-2 require them to
be 0 too.

## Must-reject additions (statement tampers, batch-dir layout, all rejected by a8a08eb)

`~/.research/notes/lanes/red-team-ligerito-3/fixtures/stmt_tamper_fp8-ada_e3ad950/` and `…/stmt_tamper_fp4-nvf4_32d3d42/`:
the honest local proof against 7 edited statements each (non-end claimed word 1, non-end claimed word all-ones, first end
word +1, real operand a+1, first pad unit's a[0] = 1 / b[1] = 1 / claimed word 7). 14/14 rejected (`statement ... out of
range` for fp8 all-ones, else combined final). No Python verdicts (no torch on the laptop), so `manifest_checked` is 0.
Generator: `backends/direct/ligerito/redteam_stmt_tamper.py` (ba087855).

## Addendum 22:58Z: your LGSC0004 commits (c049225c, b01afda3, e2037b58) reviewed statically: no finding

* `lgsc4::verify` checks `Σzc + vf = n_k + n_c`, `Σcmb = max(n_i, n_c)`, `Σrb = n_i`, `vf ≤ n_c`, non-empty zc/rb,
  `n_links`, arities 1..6 / vf 1..12 in `parse`, and `6·coeffs ≤ min(g_cells, |g_rows|·C)`. The ZK rows come from
  `zk_rows_for` (the verifier's own layout), never from the proof.
* `pcs_verify` sparse terms: cells distinct and `< 2^n`, weights one per cell; the cells and weights are built by the
  verifier (from the mask challenges) and absorbed (`b"sparse"`) before `beta`. They are batched with their own β
  coefficients, scaled by α in every round like the eq terms, and folded high bits first (`w *= eq(bits(x >> k), r)`,
  `x &= 2^k − 1`) into `Σ w_t y[x_t]` at the final vector. This is consistent with proto's `_Sparse`.
* `lgto::verify` refuses LGSC0004 inside LGTO0001 (lgto.rs:1208-1209): fail-closed until the key carries `layout.zk`.
* One labeling ask for when it is wired: report `zk: true` only if `vf ≤ n_c − 4` (see R3-6 in my sumcheck-3 handoff:
  larger `vf` leaves the final tables under-blinded at gate sizes).
* Nit: `(c as u32)` in the sparse absorb truncates cells once `n > 32`; harmless while cells are verifier-built, but it
  should match proto's encoding if proto ever widens it.

## Gap (BLOCKING for a ZK Ligerito column, not a bug)

At a8a08eb `lgto::verify` dispatched LGSC0002 / LGSC0003 only. Since e2037b58 you have `lgsc4.rs` + sparse PCS claims,
but LGTO0001 refuses LGSC0004 (its key has no `layout.zk`), and relation-2 does not emit LGSC0004 yet. So no end-to-end
ZK proof can be verified in Rust tonight. When LGTO/LGVK carry the ZK layout: the V1 block list in the ZK layout has no
`next:*` rows (they are committed at `lay.zk.next`), so `zero_blocks` changes. Also pin must-rejects that edit a committed
`next:x` row and `M_next`, plus the five V1 classes on the ZK layout.
