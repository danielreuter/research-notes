---
lane: ligerito-verify-rs
kind: report
created: 2026-09-23T17:00Z
status: superseded
---

CHECKPOINT none (00:03Z) [superseded] by verify-rs-2 (coordinator)
CHECKPOINT ff9d4c3 (19:01Z) — B-POW2 (pcs-fast's shipping point, k' 6,4,4,3,3, rates 1,2,2,2,2, |S| 312,191,193,194,195) exercised end to
end with the in-crate prover at n = 26: proof 535 KB, 29 coins, 1085 opened rows, 891 final terms, verify 6 ms (5.4 GB / 140 s to PROVE on
the laptop — the Rust prover is a test oracle, not a product), 16/16 negatives rejected. RS query base changed to params.py's `(1 + ρ)/2`
(red-team: proven and tighter than my `(m + k + 1)/(2m)`, whose +1 cost 0.9 bits at m = 2^8 and pushed B-pow2 to 2^−127.95 → FALSE REJECT
under the new default target); now 2^−128.026 at n = 26 and n = 29, identical to params.py, pinned in `params::tests`. 48 tests green.
CHECKPOINT 0254f65 (18:55Z) — red-team F5(ii) closed: `--target-bits 128` is now the DEFAULT — `verify` rejects a proof whose own
(17) figure misses 2^−128 ("verifies, but its soundness 2^−9.00 misses the target"), `batch` fails on the union bound; `--target-bits 0`
waives (toys, conformance). The n=20 |S|=192 selftest proof passes at 2^−128.24. 48 tests green, `git status` clean.
CHECKPOINT 7e729ee (18:52Z) — REF.PY FIXTURES ACCEPTED BIT-FOR-BIT: new `refpcs.rs` verifies ligerito-design's SPEC dialect
(`backends/direct/ligerito/ref.py` @ lane/ligerito-design 760260d, format `ligerito-ref/v1`): mixed-radix digits with the TERNARY tall
digit (parameter-set-B shape `3 × 2^k`), tensor-claim statement (`eq` / Lagrange-3), natural-order RS rows, element-major BLAKE3 leaves,
3-coefficient sumcheck messages low digit first, per-claim `alpha` batching, and its BLAKE3-only `FSCoins` (chain + XOF; I added a
BLAKE3 XOF to `hash.rs`, checked against the `blake3` package). All 4 fixtures `python -m backends.direct.ligerito.ref` prints
(n8 L1, n10 L2, n12 L3, n10 L2 ×3-ternary; `fixtures/ref/fixtures.json`, byte-identical to the module's stdout) ACCEPT; 80 declarative
tampers (`fixtures/ref/negatives.json`: value, roots, rows, siblings ±, c0/c1/c2, sum-preserving c1/c2 swap, final vector, index set,
duplicate index, query count, row count, ext-in-base row, final shape, n_log2, non-canonical entry) get the SAME verdict as `ref.verify`
— 76 rejected by both, the 4 `x + p` non-canonical rows accepted by ref.py (it reduces mod p when hashing) and REJECTED here (documented
divergence, §6). Plus a set-B-shaped n16 L3 ×3 q64 fixture (`tall (12288, 768, 48)`, 234 KB): accept in 1.4 ms, soundness 2^−46.5 by
(17). 48 tests green. CLI: `ligerito-verify ref-fixtures --file F.json [--neg N.json]`; `batch --dir` also consumes `*.ref.json`
(+ `*.ref.neg.json`). Both PCS dialects (proto/pcs.py and ref.py) now verify from one binary — §10 asks pcs-fast/relation which one ships.
CHECKPOINT eb88ca8 (18:40Z) — SUMCHECK VERIFIER DONE: `relation.rs` implements ligerito-sumcheck's 18:20Z interface (LGSC0002 wire; Gruen
zero-check with the bivariate opening round; rows sumcheck with `coef = eq(r_k,·)ᵀ(A+γB+γ²C)` from the COO triples and `z̃` from the public
rows + `next_vals`; shift sumcheck with the cyclic-successor MLE; the 1 + n_links claims out). It ACCEPTS their fixture
(`ligerito-sumcheck/evidence/fixture_fp8ada_l64_S2.json.gz`, 0bc9d89: fp8-ada, l = 64, S = 2, n_i = n_k = 12, n_c = 7, 19 458 triples, 3 links)
two ways — replaying the recorded transcript with EVERY absorb byte-checked against the Python log, and with their `LocalCoins(b"fixture")`
re-implemented — and returns claims identical to the Python verifier's (4 points in F^19 + values). Negatives: every 7th proof byte flipped,
a public-row entry, a constraint coefficient, a virtual-row index, a different coin seed: all rejected. Verify 1.7 ms. Also (ea54996):
per-round RS rates after proto 7bc2fdd (header `rate_log2` list absorbed as a list; b4d7e12 scalar headers still verify bit-for-bit).
44 tests green; `git status` clean. CLI: `ligerito-verify sumcheck-fixture --fixture F.json [--seed fixture]`.
CHECKPOINT a43820c (18:00Z) — `batch --dir` now like ligero-verify's: every `*.proof` must verify, every `*.proof.neg` must be REJECTED,
`manifest.json` (`[{"proof","accepted","reason"}]` or `{"proofs":[...]}`) verdicts must agree with ours, `--target-bits B` checks the union of
the proofs' own soundness figures; `.z`/`.coins` sidecars resolved for `.neg` files too. Robustness sweep on the proto n=10 fixture: all
5867 single-byte flips (only the header's informational keys `splits`/`coins`, which are not absorbed by either verifier, are inert — see §4),
all 5867 truncations, random garbage, absurd header sizes: no panic, no false accept. 40 tests green. Disk: 8.6 GB free, my target dir 30 MB.
CHECKPOINT eb6ffa5 (17:52Z) — + `sumcheck.rs`: relation-side round verifier (plain deg-2 `(g0,g1,g2)` and Gruen deg-3 `(q0,q1,q∞)` with
the `eq(τ_t,·)` factor, `eq` helpers) tested against an in-crate zero-check prover (roundtrip, unsatisfied relation, tampered message /
τ / count rejected); 40 tests green. Read design 17:55Z (radix-3 tall dim: NOT supported yet, see §6), zk 17:55Z (RS padding + ȳ, §7).
CHECKPOINT 96a7a35 (17:48Z) — `backends/ligerito-verify/` (Rust, no deps, 3.4 kLoC) builds and `cargo test --release` is green: 36 passed / 0 failed.
It ACCEPTS the Python prototype's proofs bit-for-bit: 3 proofs written by `ligerito-proto` `proto/pcs.py::prove` (b4d7e12 + its uncommitted
working tree at 17:40Z; laptop CPU path, n = 10/12/16, 1/3/3 committed rounds) verify under Fiat–Shamir with the same coin count as Python
(5/14/18), and every byte flip we tried (~80 positions across header, v, roots, sumcheck messages, rows, siblings, y, plus each point
coordinate) is rejected. Two of those proofs (17 KB total) are pinned in `fixtures/proto/` and re-verified by the test suite. `ligero-verify`
still builds. 17:30Z HARD RULE acknowledged: no torch, no venv, nothing > 20 MB from this lane on the laptop (this crate is Rust-only; the
fixtures above were produced by the proto lane's interpreter BEFORE the stub landed, 17:40Z, and take 17 KB).
CHECKPOINT 0f64f4d (17:20Z) — scaffold: field (BabyBear + F_{p^6}), hash (blake3/blake2b/shake), Merkle multi-open, tensor claims,
transcript, params, PCS verifier, reference prover + negatives, LGRTOPV0 container, CLI `verify | batch | selftest`; 34 tests green.

# ligerito-verify-rs — independent Rust verifier for the Ligerito PCS (+ zero-check sumcheck, + LGTO batch)

Crate `backends/ligerito-verify/` (package `verity-ligerito-verify`, lib `ligerito_verify`, bin `ligerito-verify`). Zero dependencies;
the primitives are COPIED from `ligero-verify` (field, blake3/blake2b/shake) and extended, not linked — both crates build standalone
(`cd backends/<crate> && cargo build --release`; there is no workspace `Cargo.toml`).

## 1. What it verifies (matches `ligerito-proto` `proto/pcs.py` 17:45Z-frozen interface)

Statement `(z ∈ F_{p^6}^n, v ∈ F_{p^6})`, claim `f̃(z) = v` for a committed multilinear `f` of `N = 2^n` BabyBear coefficients.
Params `(n, k'_1..k'_L, |S_1|..|S_L|, rate_log2)` → `k_1 = n − k'_1`, `k_{i+1} = k_i − k'_{i+1}`; round i commits `2^{k_i} × 2^{k'_i}`
(round 1 base field, rounds ≥ 2 six coordinate planes), codeword length `2^{k_i + rate}`, evaluation domain `<ω>` (coefficient-basis RS,
position `s` holds `P(ω^{eta_index(s)})` with the proto's 4-step split `s = k'·n1 + k1 ↦ k' + n2·k1`, `(n1, n2)` from the proof header).

Verifier (paper §6 Alg. 2, one committed round = Ligero): per round `i`: absorb root_i; `k'_i` sumcheck messages `(g(0), g(1), g(2))`
each followed by `challenge("r", 1)`; `g(0)+g(1) == running`, `running ← g(r)` (deg-2 interpolation); then for `i ≥ 2`:
`indices("S", 2^{k_{i-1}+rate}, |S_{i-1}|)`, opened rows + siblings absorbed, BLAKE3 Merkle multi-path against root_{i−1}, each opened
row `s` becomes a geometric tensor term `⟨(η_s^x)_x, y_{i−1}⟩ = ⟨U_{i−1}[s,:], r̄_{i−1}⟩` (rows ≥ 2 are 6-plane, plane-major `(6, C)` words);
`challenge("alpha", 1+|S|)` batches the running claim with the new terms. Final: absorb `y_L` (`2^{k_L}` ext), `indices("S", ...)`,
Merkle check, `⟨U_L[s,:], r̄_L⟩ == P_y(η_s)` (RS re-encode of `y_L` at the opened positions), and the batched claim
`Σ_t coef_t · ⟨tensor_t, y_L⟩ == running` with all terms restricted to the last `k_L` variables. Report: coin count, opened rows, final
term count, `soundness_log2` (paper (17)/(18): per round the RS proximity term `((m + 2^{k_i} + 1)/2m)^{|S_i|}` ≈ `((1+ρ)/2)^{|S_i|}` — the
printed `(1−ρ)/2` base in (17) contradicts the paper's own numerics (|S| = 148 ↔ 2^−100 needs 5/8), so I use the sampling bound — plus
the field terms `(2k'_i + |S_{i−1}| + 1 + m_i k'_i)/p^6`).

Transcript (`transcript.rs`) = `FiatShamirCoins` byte-for-byte: state `blake2b_256("ligerito-proto/v1")`; `absorb(label, data)`:
`state ← blake2b_256(state ‖ label ‖ len_le64 ‖ data)`; `challenge(label, n)`: absorb(`"challenge"`, label) then
`shake256(state ‖ counter_le64)` → `8·6·n` bytes, each coordinate `= int64_le(8 bytes) mod p` (SIGNED read, see §4); `indices(label, d, c)`:
absorb(`"indices"`, label ‖ d_le64`), rejection-sample `c` distinct `u64 mod d` from `16c`-byte squeezes, re-squeezing if short.
Also `Live` (one 32-byte verifier coin per round trip, `shake256(coin ‖ sub_le64)`, from a `.coins` file: `u32 count ‖ 32 B each`) and
`Local(seed)` (diagnostic). Header absorbed first: `json.dumps({"n","kprime","queries","rate"})` with Python's default separators, then `z`.

## 2. Proof containers

* **proto** (what `proto/pcs.py::Proof.to_bytes()` writes): `u32 header_len ‖ header JSON ‖ v (24 B) ‖ per round: root (32) ‖ k'_i × 72 B
  sumcheck msgs ‖ final_y (2^{k_L} × 24) ‖ per round: rows (u32 words, round 1: |S|×C, later |S|×6C plane-major) ‖ u32 nsib ‖ 32·nsib`.
  The point `z` is NOT in the proof: the CLI reads it from the sidecar `X.z` next to `X.proof` (raw `n × 24` bytes = `_z_bytes`).
* **LGRTOPV0** (this crate's self-contained test container, includes params + z + v): used by `selftest --emit` and the unit tests.
  `verify` auto-detects (`{` at byte 4 ⇒ proto).
* **LGTO0001** (`ligerito-relation` `proof.py`): not published yet → `batch --dir` currently walks `*.proof` (+ `.z`, optional `.coins`)
  and prints one JSON line per file + a summary line; will switch to the LGTO reader when the format lands (§5).

## 3. CLI

~~~
ligerito-verify verify --proof X.proof [--coins X.coins] [--target-bits B=128]   # JSON line: accepted, reason, mode, bytes, seconds, report, params
ligerito-verify batch --dir DIR [--jobs N] [--target-bits B=128] [--json out.json]
    # every *.proof must verify, every *.proof.neg must be rejected (X.z / X.coins sidecars for both), DIR/manifest.json
    # verdicts ({"proof","accepted","reason"} entries) must agree, union soundness <= 2^-B; exit 0 iff all hold
ligerito-verify selftest [--n 12 --kprime 4,3,2 --queries 16,16,16 --rate-log2 2|2,4,4 --emit DIR]   # reference prover → LGRTOPV0 + proto + coins
ligerito-verify sumcheck-fixture --fixture F.json [--seed fixture]   # ligerito-sumcheck's fixture: LGSC0002 + layout + constraints + public rows
ligerito-verify ref-fixtures --file F.json [--neg N.json] [--reps R] [--json out]   # ref.py fixture list (+ tampers); exit 0 iff every verdict = ref.py's
~~~
`batch --dir` also picks up `DIR/*.ref.json` (ref.py fixture lists; `DIR/X.ref.neg.json` = tampers for `X.ref.json`) — every entry must
get ref.py's recorded verdict, and accepted ones contribute their (17) soundness to the union bound.
Verify time: proto n=16 (3 rounds, 32/32/16 queries, 33.8 KB) 0.9 ms; n=12 0.7 ms; n=10 0.3 ms (release, M-series laptop). At the
campaign's sizes (n = 29/30, |S| = 192, three rounds) the cost is dominated by `Σ_i |S_i| · 2^{k'_i}` row dot products + the last-round
RS re-encode at `|S_L|` points (`2^{k_L}` ext mults each); expect single-digit ms.

## 4. For ligerito-proto (transcript warts — freeze or fix, tell me which)

* **7bc2fdd per-round rates: implemented** (header `rate_log2` list ⇒ absorb `"rate": [r1, r2, ...]`; a scalar header ⇒ the old
  absorb) but NOT yet cross-checked against a 7bc2fdd proof — torch is a stub on the laptop now. Two asks, both seconds on your pod:
  (a) `PYTHONPATH=. python -c` the snippet below and drop the two files into `~/.research/notes/lanes/ligerito-proto/evidence/`;
  (b) run your `verify()` on MY proto-container proof `backends/ligerito-verify/fixtures/rust/n12_rates234.{proof,z}` (branch
  `lane/ligerito-verify-rs`, rates [2,3,4]) — it should say `accept`.
  ~~~
  import numpy as np, torch; from backends.direct.ligerito.proto.dims import Dims; from backends.direct.ligerito.proto.pcs import prove
  from backends.direct.ligerito.proto.ext import P, D; rng = np.random.default_rng(1); dims = Dims(12, [4,3,2], [16,16,16], [2,3,4])
  f = torch.as_tensor(rng.integers(0, P, size=1<<12, dtype=np.int64).astype(np.int32)); z = rng.integers(0, P, size=(12, D), dtype=np.int64)
  pf = prove(f, z, dims); open("n12_r234.proof","wb").write(pf.to_bytes()); open("n12_r234.z","wb").write(z.astype(np.uint32).tobytes())
  ~~~

* `_ext_from_stream` does `np.frombuffer(<u8).astype(np.int64) % P`: the 8 challenge bytes are read as a SIGNED int64 and reduced with a
  non-negative remainder — half the words are `2^64 − u` mod p, not `u mod p`. Uniform anyway, so harmless; I match it exactly
  (`i64::from_le_bytes(..).rem_euclid(p)`). If you change it to unsigned, say so and I flip one line (and the pinned fixtures).
* `indices` uses UNSIGNED `u64 % domain` (fine, matched).
* Header JSON uses default `json.dumps` separators (`", "` / `": "`), while `Proof.to_bytes` uses compact separators — matched both.
* The header's `splits` (the 4-step `(n1, n2)` per round, which fixes the codeword position ↔ domain point permutation) is read from the
  proof and NOT absorbed — by your verifier or mine. A prover could pick it after seeing `S` (a handful of factorisations → a few extra
  tries; negligible but a wart). Absorbing the full header bytes (or fixing the split canonically per size) closes it; I'd follow.
* `verify(proof, z, v)` takes `z` out of band; the CLI here needs a `.z` sidecar. If the relation lane's LGTO0001 embeds `z`, nothing
  changes for you.

## 5. For ligerito-relation

* Call `ligerito-verify verify --proof X.proof` with `X.z` beside it (raw `n × 6 × u32` LE, `_z_bytes(z)`), or `batch --dir` over a folder.
  Exit code 0 iff all accepted; one JSON line per proof (`accepted`, `reason`, `seconds`, `report.coins`, `report.soundness_log2`).
  Since 0254f65 the soundness target 2^−128 is ENFORCED by default (per proof in `verify`, union in `batch`); toy-size proofs need
  `--target-bits 0`. The figure is recomputed from the proof's own parameters (never trusted from the prover).
* Publish `proof.py`'s LGTO0001 layout (magic, header fields, how the sumcheck transcripts + PCS proof + z + v are framed) in your note and
  I add the reader the same hour; `batch --dir` will then verify the sumcheck → evaluation-claim chain and the PCS proof in one pass.
* Live coins: `--coins X.coins` (`u32 count ‖ 32 B per verifier round trip`) replays `LiveCoins` slots; without it Fiat–Shamir.
* Fixes: this section is watched until 23:00Z; write `## For ligerito-verify-rs` in your note with the failing proof path + expected result.

## 6. For ligerito-design (ref.py @ 760260d: ACCEPTED, see CHECKPOINT 7e729ee)

* `refpcs.rs` is a line-by-line Rust twin of `ref.verify` (same check order, same reason strings up to the stage prefix), fed by
  `proof_to_dict` JSON. The 4 `main()` fixtures verify bit-for-bit and 76/76 of my tampers that ref.py rejects are rejected here, in the
  same stage. Ternary digit, `lagrange3`, `rs_row_tensor` with `(1, ω^s, ω^{2s})`, `FSCoins` incl. the `need *= 2` re-squeeze: all matched.
* ONE divergence, deliberate: `row_bytes` does `% P` before hashing, so a row entry `x + p` in the JSON verifies like `x` (malleable
  encoding; the Merkle leaf is the same). Rust rejects any coordinate `>= p` anywhere in the proof. Suggest `proof_from_dict` assert
  canonical entries (`0 <= v < P`) so the two verifiers agree on every input.
* Soundness figure I report for a ref.py proof = the docstring's per-level `((1 + rate_i)/2)^{|S_i|} + (k'_i n_i + 2k'_i + |S_{i-1}| + 1)/|F|`
  summed (toy fixtures: 2^−4..2^−5; n16 ×3 q64: 2^−46.5). If `params.py` tightens this (list decoding / the contraction bucket), say
  which formula the Rust side should print.
* Fixture provenance for the record: generated on the laptop with the proto lane's interpreter (numpy + blake3 only, no torch) from
  `git show lane/ligerito-design:backends/direct/ligerito/ref.py` at 760260d; `fixtures/ref/fixtures.json` is `cmp`-identical to the
  module's stdout. If ref.py changes (labels, byte layouts, coin header), re-run `python -m backends.direct.ligerito.ref > fixtures.json`
  and tell me — the tamper file references fixtures by index and JSON path, so it survives regeneration.

## 7. For ligerito-zk (read §1.1–§1.2)

The per-column RS padding changes the verifier's row check to `⟨U_i[s,:], r̄_i⟩ = ⟨gen_s, y_i⟩ + ⟨gen'_s, ȳ_i⟩` with public
`ȳ_i ∈ F^{t_pad}` travelling with `root_{i+1}` (absorbed): that is one extra public vector per round and a shifted geometric term
`η_s^{2^{k_i} + j}` — ~40 lines here once `zk.py` fixes the bytes and the absorb label. The mask column / A-cells / G-block are
prover-side (the verifier sees a bigger `f̂` and one extra `W_g` block-term claim) — the block term (one-hot high part × sparse low
part) is a new `Kind` in `claims.rs`; tell me its exact framing when it exists. Not before the relation lane's LGTO0001 lands.

## 8. Timing (release, laptop, single thread)

`selftest --n 20 --kprime 6,4,4 --queries 192,192,192 --rate-log2 2`: proof 271 KB, 19 coins, soundness 2^−128.24 (paper (17) with
the sampling base), verify 2.5–3.3 ms (576 opened rows, 385 final terms); 16 negatives (tampered v / root / message / row / sibling /
final y / index set / z / truncated) rejected. `batch --dir` over honest + live (`.coins` sidecar) + proto containers: 3/3 in 4 ms.

## 9. For ligerito-sumcheck

* Your fixture verifies here bit-for-bit (see CHECKPOINT eb88ca8); `succ_mle` follows your CODE (`a = b + 1`: `(1 − b_t) a_t` at the flip,
  `b_u (1 − a_u)` carried) — the note's prose says `b = a + 1`; the code is right for `succ_mle(rho, r_c) = Σ_c eq(rho, c) eq(r_c, pred(c))`.
* Conventions I locked in from `verify()`: `zc/tau` is drawn BEFORE anything is absorbed (the caller's PCS commitment absorb precedes it);
  round-0 check is against claim 0 with the `E` factor outside; `r_var = reversed(draw order)`; `pub_names` = every `lay.virt` name not
  starting with `next:`; `next:{x}` indexes the links in `c_rows` order; `bits(c_x)` LSB first as base-field 0/1 ext coordinates.
* If the two-variable base round or any label changes, regenerate the fixture and I re-pin (one file, `fixtures/sumcheck/`).
* Real-size verifier cost is the public-row MLEs (192 × 2^18 base×ext): 10–20 ms here. Fine; no closed forms needed today.

## 10. For ligerito-pcs-fast / ligerito-relation — WHICH PCS DIALECT SHIPS?

Two Ligerito PCS dialects exist and this crate verifies both, but they are NOT wire-compatible and the relation lane's LGTO0001 must pick one:

| | `proto/pcs.py` (proto 7bc2fdd, now owned by pcs-fast) → `pcs.rs` | `ref.py` (design 760260d, the SPEC) → `refpcs.rs` |
|---|---|---|
| index | `x = row + 2^{k_i}·col`, binary only | mixed radix, digit 0 LOW, tall may be `3·2^k` (set B) |
| statement | `f̃(z) = v`, `z ∈ F^n` (eq tensor) | tensor claim `<f, w> = v`, `w = point_tensor(z)` (eq / Lagrange-3) |
| codeword rows | 4-step permuted (`splits` in header) | natural order `ω_n^{s r}` |
| ext leaf bytes | plane-major (6 planes × C words) | element-major (C × 6 words) |
| sumcheck msg | `(g(0), g(1), g(2))`, high variable first | `(c0, c1, c2)` coefficients, low digit first |
| batching | `alpha` per claim after `absorb(rows)` | same order; `challenge("batch", 1+|S|)` |
| coins | BLAKE2b chain + SHAKE256 (`transcript.py`), signed-int64 reduction | BLAKE3 chain + BLAKE3 XOF, unsigned |
| container | bytes: JSON header + body (`Proof.to_bytes`), `z` out of band | JSON (`proof_to_dict`), fixture carries z + commitment |

**pcs-fast's 18:40Z checkpoint answers (a): the GPU prover emits the proto dialect, byte-identical to proto 7bc2fdd, at the B-pow2 point
(k' 6,4,4,3,3, rates 1,2,2,2,2, |S| 312,191,193,194,195; radix-3 not implemented).** That is `pcs.rs` — exercised at that exact shape
(CHECKPOINT ff9d4c3): accept, 2^−128.026, 6 ms. Remaining ask to pcs-fast: drop ONE B-pow2 proof from the 4090 (n = 29, 0.646 MB, `.proof`
+ `.z`) into `~/.research/notes/lanes/ligerito-pcs-fast/evidence/` (< 1 MB, laptop-safe) and I confirm bit-for-bit within the hour; note
`batch --dir` over several proofs of the SAME target needs `--target-bits 128-log2(N)` or a per-proof run (the union rule is deliberate).
The ref.py dialect stays as the SPEC oracle (radix-3 set B proper). If pcs-fast later
implements set B by ADOPTING ref.py's index/tensor/message conventions (natural-order RS, coefficient messages, element-major leaves) and
keeps proto's `transcript.py` coins, that is `refpcs::verify` with a `RefCoins` adapter over `transcript::FiatShamir` — a 30-line change
here, and ref.py itself already runs on proto's coins (design's interop test). Tell me in your note (a) which dialect + coin scheme the
GPU prover emits, (b) the container for LGTO0001 (I read either JSON or a bytes framing), and post ONE proof + z + expected verdict; I
make `batch --dir` accept it the same hour. Until then both paths stay; nothing is removed.

## 11. For red-team-ligerito (your 18:30Z report, F2 / F5 / §0)

* F5(ii) fixed at 0254f65: `--target-bits 128` is the default in `verify` and `batch`; a proof with |S| = 1 is now rejected with an
  explicit reason. `n_proofs` binding (F5 i) is the relation lane's statement; once LGTO0001 carries it I add `--target-bits 128+log2 N`.
* F2 "the Rust verifier is pow2-only": no longer — `refpcs.rs` (7e729ee) verifies ref.py's radix-3 dialect (ternary low digit, set-B
  shapes) bit-for-bit, including a `tall = (12288, 768, 48)` fixture. proto's dialect (`pcs.rs`) stays pow2. Whichever dialect pcs-fast
  ships is covered; §10 above asks them to pick.
* Query base aligned to `(1 + ρ)/2` in both `pcs.rs` and `refpcs.rs` (ff9d4c3) after your proof that it is valid: my `+1` was worth 0.9 bits
  at the last level's m = 2^8 and would have false-rejected B-pow2 under the default target. Rust and params.py now print the same figure
  (B-pow2 2^−128.026). Your F5(iii) "size to 2^−129" is the relation lane's call; the verifier enforces whatever `--target-bits` says.
