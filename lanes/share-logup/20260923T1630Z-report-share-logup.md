---
lane: share-logup
kind: report
created: 2026-09-23T16:30Z
status: superseded
---

CHECKPOINT none (00:03Z) [superseded] by share-logup-2 (coordinator)
CHECKPOINT fc49219 (18:50Z) Rust verifier verifies the pair (`ligero-verify verify|batch --system-h`; 13/13 tile64 pairs ACCEPT on the pod, batch 2^-128.18, pinned fp8-ada G/H digests both modes, python agreement 13/13); gates fp8-ada+shared tile64: interactive AND Fiat-Shamir 49 honest sub-batches / 98 negatives / 0 failures each; bench (4090, 4096 VUs, 13 sub-batches, l=16384, interactive) prover 0.41 s + hints 0.14 s = 0.55 s vs included-hash 0.52 + 0.10 = 0.62 s vs bare --pipeline 4 0.16 s; FS 0.47-0.70 s + 0.13 s. F7 booked (fingerprint_collision x n_op(l/steps) with the 3/2^32 coin bias: 2^-157.2 IA / 2^-138.9 FS per proof), F8 = option (b): leak stated in zk_statement (ZK_SHARED_NOTE), v2 costed in PROTOCOL.md 8e. Fixed a 3x slowdown: H's layout flipped between 70 and 71 units per sub-batch and the ragged last one dropped to l=256, so the tests graph was re-captured each time (0.3-0.5 s); H's l now floors at l_G / 4. Pod pytest 47 passed (chain, hashchain, relations, batch_bound, auth); laptop cargo test 16 passed. NEXT: rebase onto lane/leaf-iface 720820d, bf16-hopper if time, FINAL.
CHECKPOINT 8cfa7fb (17:40Z) Python G+H end to end on the CPU (4-VU 2x2 tile + 2-VU worst case, both modes; 6 negatives rejected); gate/bench wiring + pod runs next; Rust after.  Earlier: CHECKPOINT none (16:55Z) worktree ~/projects/verity-main-wt/share-logup on lane/share-logup from main e0cf2cd; pod vy-share-logup (kx69zewzhawgy1, RTX 4090 24564 MiB reference part, EPYC 7K62 host, $0.74/h) created 16:47Z (two REST 500s first: "no instances available"), bootstrap started 16:52Z (`/workspace/bootstrap.log`); design settled (below), coding.

# share-logup — hash each operand row once per tile, every VU proves equality by a post-commitment fingerprint

## 0. Census of the two mechanisms (decision: fingerprint chain)

Both mechanisms need the row hashed *somewhere* in-circuit exactly once and every VU bound to that row without re-hashing;
they differ only in the binding.

* **LogUp multiset.**  The VU's 32 words per column and the row unit's words are two multisets of (position, value) pairs;
  the argument is sum 1/(alpha - (pos + beta value)) over both sides with a verifier coin (alpha, beta) drawn AFTER the
  commitment, one inverse row per word per column (1536 inverse rows per VU per operand + the running-sum rows) plus the
  same rows on the hash side.  Every inverse is a product row; the cost is >= 2 x 32 rows per column per operand on the
  GEMM side alone (~130 rows/unit) and the coin is post-commitment either way.
* **Fingerprint chain.**  F_o(rho) = sum_{s,i} rho^{16 s + i} lane_o[s][i] over the VU's 48 columns x 16 lanes (the same
  16-bit lanes the sponge absorbs), rho a post-commitment verifier coin.  The constraint is LINEAR in the committed
  rows with rho-dependent coefficients, so it costs NO witness rows: it rides the chain test (Ligero's general linear
  test already draws one coefficient per constraint per column) with the lane rows as the only addition (16 rows per
  operand per unit; the lanes are needed anyway to pack the bits).  F leaves the prover as one message after the coin
  (8 coordinates x 2 operands per VU) and the hash-side proof takes the same rho and F as public inputs.
  Collision: two different rows agree on F(rho) with probability <= 767 / p per coordinate (degree < 768 polynomial in
  rho, Schwartz-Zippel); 8 coordinates -> (767/p)^8 ~ 2^-171.

The fingerprint chain wins by ~130 rows/unit and by needing no new product rows; both need the same new coin (rho after
the root) -- which the transcript already has a slot for (challenge 1 is derived from the root / the step-0 coin r1).

## 1. Design (paired proofs per sub-batch)

Per sub-batch i (341 VUs at l = 16384) TWO Ligero proofs share one session:

* **G_i** (`hashchain.compose_shared`): the GEMM relation with PRIVATE operands (bit rows + decode constraints as
  `compose` step 1), 16 lane rows per operand per unit (`lane = sum 2^(8q+b) bit`), NO sponges, NO digest pins.  After the
  root, challenge 1 expands (as today) r | rho_lin | rho_quad | rc AND 8 more elements rho_0..rho_7 (coin-only in the
  interactive mode, root-bound in Fiat-Shamir: 8c holds).  The prover then sends F (n_vus x 2 x 8 u32; absorbed into
  challenge 2 in FS mode) and the chain test gets 16 more constraints per VU at its end column:
  sum_{s,i} rho_x^(16 s + i) lane_o[48 v + s][i] = F[v][o][x], each with its own uniform coefficient (the end column's
  unused link/start families + monomials, exactly the `chain.py` extras rule).
* **H_i** (`hashchain.row_hash_system`): one Poseidon2 sponge per unit hashing ONE row (x row or W column, role a public
  pin selecting the IV) over 48 columns: bit rows, lane rows, 852 S-box rows, 8 linked capacity rows, digest pins at the
  end (8 lanes), and the SAME fingerprint constraint with rho and F from H's STATEMENT.  H_i hashes the ~70 distinct
  rows sub-batch i touches (5.3 x rows + 64 W columns at the 64x64 tile), l = 4096.
* **Cross-check (pair):** rho(H_i statement) == rho derived in G_i; for every VU v of G_i, F_G[v][x] == F_H[unit of x row
  x_index[v]] and F_G[v][W] == F_H[unit of W column w_index[v]]; H_i's digests are leaf/v2h leaves at those ranks under the
  a / b roots (hashauth multiproofs, as today); G_i's y words under the y root (as today).

Cost model (fp8-ada, rows per unit): base 3769; + private operands 704 (11 / byte); + lanes 32 = ~4505 for G (+19.5 % vs
bare, vs 6210 = +65 % for included-hash today); H: 256 + 16 + 852 + 8 + 9 + 3 = ~1145 rows x 4096 columns per sub-batch
= 5 % of G's cells.  The Poseidon2 work per tile drops from 4096 x 2 permutations x 48 to ~70 x 13 x 48 (5x; 64x would
need a tile-wide session -- one rho for all 13 sub-batches -- which breaks per-sub-batch pipelining; deferred).

## 2. Log

(appended below)

* 17:40Z  8cfa7fb.  chain.py: `sys.chain["fp"]` = {lanes, coords, mode coin|public}; `chain_coefs(..., fp=FpArgs(rho, F))` adds
  n_op x C constraints per VU at its END column with monomial coefficients `extra_coef(rc, 2 n_extra_links + o C + x)` (degree <= 4 at
  an end column; G: e = 0..15, H: e = 10..17), the lane-row coefficient at column steps v + s being sum_x u_{v,o,x} rho_x^(16 s + i) (one
  (D, n_op, C, n_slots, steps, 16) product, ~134 MB at l = 16384, D = 6).  protocol.py: challenge 1 expands C more elements
  (coordinate 0's tail = rho; 8c intact: a function of the coins alone), `Proof.fp` (n_vus, n_op, C) is a prover message absorbed into
  challenge 2 (FS) / sent after coin 1 (interactive), `statement_digest(..., fp=)` binds rho, F in the public mode, `verify(..., out=)`
  hands the verifier's rho to the pair check; `soundness(..., fp=(coords, steps))` books `fingerprint_collision` = ((16 steps - 1)/p)^C.
  FS mode needs C = 10 (the 2^60 factor: (767/p)^8 x 2^60 = 2^-110.6 > target), interactive C = 8 (2^-170.6): `FP_COORDS` / `FP_COORDS_FS`,
  the runner picks by mode.  hashchain.py: `compose_shared` (G: 4506 rows/unit fp8-ada = base 3769 + private 704 + lanes 32 + 1 pin;
  vs 6210 hashed, +19.6 % over bare) and `row_hash_system` (H: 1142 rows/unit = 10 pins + 256 bits + 16 lanes + 852 S-box + 8 caps;
  IV(role) = IV_x + role (IV_w - IV_x), role a public pin so one system hashes x rows and W columns; `Poseidon2Witness(role_row, ivd)`
  kernel).  relchain.py: `SharedHashedRunner` (AUTH `included-hash-shared`): per sub-batch prove G -> (rho, F) -> H on units =
  distinct x ranks then distinct W ranks of the auth block (`hashchain.shared_units`), both configs sized for 2 n_proofs; verify = G,
  VUs of one unit agree on F, H on (table, units, rho, F_H), table roles/ends vs units, `verify_hash_auth` on the per-VU expansion of
  H's digests.  CPU smoke (fp8-ada, 4 VUs on a 2x2 tile, l = 256 both sides): prove 0.6 s, verify 0.09 s; rejected: H digest lane
  flipped, G's F flipped, computed on a flipped row alone on its unit ("H: chain constraints failed"), shared row flipped (the prover
  refuses: two VUs disagree on F), H hashing another row.  Batch bound (interactive, 1 sub-batch = 2 proofs) 2^-128.08 accepted.
  Laptop torch runs were <= 20 s each on the pre-existing ~/projects/verity/.venv (no installs; 17:30Z rule read: all further torch
  work on the pod).  Disk 4.1 GB free.
