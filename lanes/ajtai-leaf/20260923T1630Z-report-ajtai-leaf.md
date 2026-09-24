---
lane: ajtai-leaf
kind: report
created: 2026-09-23T16:30Z
status: superseded
---

CHECKPOINT none (00:03Z) [superseded] by ajtai-leaf-2 (coordinator)
CHECKPOINT d40399f (19:00Z) — REBASED ONTO lane/leaf-iface 720820d (§9 18:10Z): `lane/ajtai-leaf` is now leaf-iface + my commits
(old head kept as `lane/ajtai-leaf-pre-rebase` a3b4e49, never to merge). Took leaf-iface's `base/registry/hashchain/hashauth/relchain/
serialize/run` + Rust `leaf.rs/auth.rs/format.rs/verify.rs/relation.rs`; ported Ajtai as `registry.register_family("ajtai", resolve)`
(`ajtai-n<N>`, N a power of two in [8, 512]; `name = "ajtai"`, `tag = "ajtai-n64"`; `carry_elems = digest_elems = n`), gadget reads the
compose's committed bit rows off the word expressions (`sum 2^j b_j`: beta = 1, nothing re-decomposed) and refuses `steps > n`;
`chain_witness` returns the n `acc_out` hint rows as the contract's third item. Same census as before (fp8-ada+ajtai-n64 4858 rows,
131 links; bf16-hopper+ajtai-n128 4669 rows, 259 links). **Red-team F5 done for everyone:** `LeafScheme.privacy_note` (optional attr;
Poseidon2/dummy set, default text for schemes without it), `relchain` fingerprint `leaf.privacy_note` + the ZK hashed note now name the
scheme's hash and ITS caveat (Ajtai: "linear, unsalted (r0): binding-only, leaks equality and linear relations between rows"); Ajtai
`assumption` = the red-team line (k-tree 2^289 / 2^571, lattice floor 2^283 / 2^557). **F6 done:** Rust `leaf.rs::ajtai` re-derives B
from SHAKE-256("verity/ajtai-babybear/B/v1" || LE32(i)) with the crate's own Keccak, checks it against the pinned `B_SHA256` (both
verifiers pin it; `params_sha256` absorbs it), and `check_system_key` scans EVERY `+ajtai-n<N>` statement's system file for the 2n key
rows (coefficients `p - B[x][i]` in bit-row order, both roles) — runs pinned or `--allow-any-system` (a B = 0 system is refused before a
proof byte is read). Rust unit tests 27/27 (incl. B derivation == Python's digests). Prover fixes since 18:08Z: `chain.extra_coefs`
(the extra-family coefficients were quadratic in n_extra: 2 x 22k kernels in the n128 tests graph; now one power per k + a batched
product, bit-identical) and `protocol` chain-test encoding in 64-row chunks (n128 OOMed at 24 GB); committer `native` on numpy is now
one vectorised pass (was 24.8 s / 8.7 s Poseidon2 -> 0.64 s). Bench r20260923-183129-78b2 (pre-rebase code, same gadget):
fp8-ada+ajtai-n64 **t.total 1.055 s** (Poseidon2 0.648, bare 0.214) with the Rust batch accepting 13/13 pinned; bf16-hopper+ajtai-n128
5.79 s (Poseidon2 1.21, bare 0.28) — its `split.hints` 3.4 s was my old per-sub-batch state recomputation; leaf-iface's `row_chain`
precomputes at commit (Poseidon2's path), being re-measured. Pod stage-4 run r20260923-185031-aee0 in flight: cargo test, leaf +
conformance (`VERITY_LEAF_CONFORMANCE=ajtai-n64,ajtai-n128`) pytest, fixtures for both relations (-> `leaf.rs::PINS`), both gates.
CHECKPOINT 40e3a11 (18:08Z) — POD GATES GREEN (vy-ajtai-leaf, RTX 4090 reference part, run r20260923-180117-1446): `fp8-ada+ajtai-n64`
gate-vu 2048 VUs batch 16384 cuda: 7 honest sub-batches accepted, **92 negatives all rejected, 0 failures** (incl. the brief's three: digest of
a different row → column challenge mismatch, both unclaimed and with the rank claimed; one bit flipped with the state recomputed → linear;
s = 2 → linear; a non-binary bit vector of the same word value → quadratic (booleanity); acc_out tampered / link broken / nonzero start →
linear). `bf16-hopper+ajtai-n128` gate-vu 512 VUs: 4 honest, 92 negatives, 0 failures. Honest prover per sub-batch at l = 16384 (gate,
no pipeline): fp8-ada+ajtai-n64 341 VUs **0.22 s**; bf16-hopper+ajtai-n128 170 VUs 0.56–0.59 s. Pod pytest (torch): leaf + hashchain +
relations + chain + tests/test_ligero_auth.py **54 passed** (run 2abd). One fix on the pod: `leaf_negatives` wrote int64 into the int32
device witness (40e3a11). Bench run r20260923-180727-6439 in flight: fp8-ada {ajtai-n64, +hash, bare} and bf16-hopper {ajtai-n128, +hash,
bare}, `--zk --mode interactive --batch 16384 --total-vus 4096 --reps 3 --pipeline 4`, rep-1 dumps verified by the Rust `batch` (pinned).
CHECKPOINT 3389c39 (17:45Z) — Rust verifier checks `fp8-ada+ajtai-n64` (pinned system 8330e2d1…, fixture `fixtures/fp8-ada-ajtai-n64/`,
`cargo test --release` 49/49 incl. 3 new Ajtai tests: accept + pin, 13 statement / 4 proof negatives, system mismatches). Adopted
ajtai-design FINAL: `b_i` = SHAKE-256("verity/ajtai-babybear/B/v1" || LE32(i)) per BIT index (their `derive_ring_element`, regression
vector in my tests), n a power of two (n = 96 refused), schema `ajtai-babybear-n<N>-b1-r0/row/v1` (`r0` = unsalted, `salt_bits`
exposed, non-zero refused). Chain-test growth MEASURED (laptop Rust, 20 VUs l=1024, 4 threads): Ajtai 0.26 s vs Poseidon2 0.12 s
per sub-batch — chain 0.091 vs 0.006 s (131 links: `2·131+1` coefficient rows × D=6 NTTs, and 128 dense 258-term forms × t × D),
ntt 0.090 vs 0.016 s; merkle/quadratic smaller (4858 vs 6210 rows). Pod `vy-ajtai-leaf` qam33gj60dv60g created 17:44Z, bootstrap
r20260923-174310-30ac running. Laptop disk is 3.2 GB free (< the 4 GB rule): nothing > 100 MB is written here from now on.
CHECKPOINT ede23de (17:55Z) — Python side complete and green on the laptop: `fp8-ada+ajtai-n64` proves + verifies on the CPU,
committer digest == in-circuit digest, v5 statement round trip, all negatives rejected (`leaf/ajtai_test.py` 9/9; existing
`hashchain_test.py` + `relations_test.py` 35/35 — Poseidon2 path byte-for-byte unchanged). Next: Rust verifier, then pod.
**For ajtai-design (please relay):** your 16:50Z gadget `Y_i = c_i + Σ_j A[i][256c + j]·bit_j` uses a DIFFERENT A block per
column `c` — not expressible in the Ligero chain (one constraint system, applied at every column; nothing in a column knows `c`).
I implement the ring version (§1 below): state transition `acc' = X·acc + B·s_col` in `F_p[X]/(X^n+1)`, `B` = the top-left
`(n, 256)` block of YOUR seeded A (same tag, same per-row XOF, LE u32, reject ≥ p — so any `n` is prefix-consistent).  The
digest is `h = Σ_i b_i(X)·g_i(X)` = Ring-SIS(n, q = p, 256 ring elements, ternary γ of degree < steps); the SIS lattice has
dimension `256·n ≥ 12288` so your SIS estimates carry over under the usual Ring-SIS ≈ SIS heuristic — please confirm, and
note the extra requirement **n ≥ steps** (48 for fp8, 96 for bf16: a wrapped polynomial makes `s_a − s_b` a coefficient and
(1,1) collides with (0,0)); `compose` refuses `n < steps`.  Naming per your note: `ajtai-babybear-n<N>-b1/v1`, leaf = n × LE u32.
CHECKPOINT none (17:10Z) — brief + code read; worktree `~/projects/verity-main-wt/ajtai-leaf` on `lane/ajtai-leaf` @ e0cf2cd. Design decided (§1); coding `leaf/ajtai.py`. No pod yet.

# Lane ajtai-leaf — `leaf/ajtai.py`: an Ajtai / Ring-SIS row digest behind the §2 LeafScheme contract

## 1. Design (why it is NOT the naive `h = A·s` per column)

The Ligero chain compiles ONE constraint system that is applied at EVERY column (unit).  A linear digest carried
column to column as `acc_out = acc_in + A_blk · s_j` therefore uses the SAME block `A_blk` at every column, so
`h = A_blk · Σ_j s_j` — swapping two columns' bits is a collision.  Position-dependence via public per-column scalars
(`acc_out = acc_in + A_blk (π_j ⊙ s_j)`) is broken too: per coordinate `Σ_j π_j[b] δ_j[b] = 0` is a 48-term modular
knapsack (2^16 work), then `A_blk · 0 = 0`.  What works with per-column identical LINEAR constraints is a public
linear state transition `acc_out = M·acc_in + B·s_j`, giving `h = Σ_j M^{steps-1-j} B s_j`.  With `M` = multiplication
by X in `R = F_p[X]/(X^n + 1)` (a negacyclic shift: n nonzeros) and `B = [b_0 … b_{255}]` 256 seeded ring elements
(one per bit position of a column), `h = Σ_i b_i(X) · g_i(X)` where `g_i(X) = Σ_j X^{steps-1-j} s_{j,i}` collects bit
position i across the VU's columns (degree < steps ≤ n).  That is exactly **Ring-SIS / SWIFFT** (Lyubashevsky–Micciancio–
Peikert–Rosen 2008: `h = Σ a_i x_i` over `Z_q[X]/(X^n+1)` with binary x_i): a collision is 256 ternary polynomials
`γ_i` of degree < steps, not all zero, with `Σ b_i γ_i = 0` in R_p — Ring-SIS(n, q = p, m = 256 ring elements, β_∞ = 1,
‖γ‖_2 ≤ √(256·steps) = 111 for fp8-ada).  p = 15·2^27 + 1 splits X^256 + 1 completely (2^27 | p − 1): NTT-friendly, same
situation as SWIFFT's Z_257[X]/(X^64+1).

Provisional parameters until `ajtai-design` posts: **n = 256, β = 1 (bits), f = X^256 + 1, B seeded by SHAKE-256**
(`verity/ajtai-leaf/v1|p|n|m|f`, u32 LE words masked to 31 bits, rejection-sampled < p).  n is a parameter of the leaf
(`ajtai-n<N>`); the relation string carries it (`fp8-ada+ajtai-n256`).

Gadget per unit (both operands): the operand bits are the private-operand bit rows step 1 of `hashchain.compose` already
committed (`hash.a[i].b<j>`, `hash.b[i].b<j>` — NOT re-decomposed); n linked `acc_in` hint rows (chain start = 0, so no IV),
n `acc_out` hint rows with the Linear constraint `acc_out[x] − acc_in[x−1] (−acc_in[n−1] for x = 0) − Σ_i B[x,i] s_i = 0`
(a field identity by construction, appended without the integer audit like the sponge's quadratics), the chain link
`acc_in[j+1] = acc_out[j]`; the digest pins `hash.d[0..2n)` tied by `is_end · (acc_out − d) = 0` (Poseidon2's structure).
Rows/unit added = 704 (private operands) + 6n + 1; chain links = 3 + 2n.  Why explicit acc_out rows and not a dense link
expression: `chain_coefs` materialises one (D, l) coefficient tensor per link TERM (dense Y = 2n·257 terms = 100 GB),
and the chain test costs one NTT per involved row either way (2n acc_in + 2n acc_out vs 2n acc_in + 512 bits).

## 2. Status / log
* 17:10Z start of coding.
* 17:55Z ede23de: `leaf/{base,registry,ajtai}.py`; `hashchain.compose(rel, leaf)` (`_compose_leaf`, `_leaf_hints`; `HashedRelation.leaf /
  n_digest / relation_name`); `hashauth.LeafParams` (schema, params digest, lanes, native, leaf_bytes — Poseidon2 = the default, bytes
  unchanged); `serialize` reads the digest width / schema / params off the relation string (`fp8-ada+ajtai-n64`), `_runner` resolves the
  suffix; `run.py --leaf ajtai[-nN]`; `relchain.leaf_negatives`.  Census fp8-ada+ajtai-n64: rows 3769 + 704 + 256 + 129 = **4858/unit**
  (Poseidon2: 6210; bare: 3769), 131 linked rows (Poseidon2 19), 128 Linear rows (each 1 + 1 + 256 terms).  Laptop CPU, 2 VUs at l=256:
  prove 0.36 s, verify 0.09 s (Poseidon2 on the same laptop: ~0.8 s / 0.47 s — the S-boxes).  Negatives: digest of another row → column
  challenge mismatch (statement changed); one bit flipped with the state recomputed → linear (the word row) fails; s = 2 → linear; a
  non-binary bit vector of the SAME word value (2·1 + 0·2) → quadratic (booleanity) fails; acc_out tampered → linear.
