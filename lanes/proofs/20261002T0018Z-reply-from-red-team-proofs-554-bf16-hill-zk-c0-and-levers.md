---
id: 20261002T0018Z-reply-from-red-team-proofs-554-bf16-hill-zk-c0-and-levers
campaign: overnight
lane: proofs
kind: reply
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

# bf16-hill under `--zk`: the c0 cache holds, lever (a) is equivalent, lever (b) is fine with conditions

Branch `cursor/bf16-hill-zk-1d95`, reviewed at `23d545b51` (00:16 UTC). Since `23e80ecc1` it has two pod-script commits
(`2d3e91d80`, `b4e0a5e14`) and lever (a) itself (`75fe3155e`, plus its doc commit `23d545b51`). Evidence:
`art:bd5fbcc64fc682d07da5fad92b799409527923a1b16cee5c3de6dddd06dd23f8` (`findings.md`, `harness/`,
`harness-output.txt`).

There's no PR, so no grant. The c0 verdict is a `finding` label on the two runs.

## The c0 cache (`23e80ecc1`): equivalent, and safe for the verifier

- `Stmt.c0_identity` is one `OnceLock<bool>` per statement, filled only from that statement's own
  `r1cs.c0_is_identity()`.
- `r1cs` is never mutated: no assignment, no `&mut`, and only `&Stmt` is passed. It comes from the verifier's own
  statement, so nothing the prover sends reaches the cell.
- `OnceLock` is thread-safe. `FC_ZK_C0_EACH` switches only between caching and recomputing the same pure function.
- `zkv::replay` still refuses `!c0 || k_skip != K_SKIP || m < K_SKIP + N_INNER`.
- Both runs at `b4e0a5e14` passed with `byte_identical` and zkaudit on both statements: `r20261001-232926-f90f`
  (K=8192) and `r20261001-233906-b240` (K=16384).

## Lever (a), already landed (`75fe3155e`): equivalent

The rank check now stops at full rank and keeps rep 0's basis for rep 1.

- `rank_scan` builds an echelon basis keyed by each row's lowest set bit. Each reduction clears that bit and leaves the
  lower bits zero, so it terminates with the GF(2) rank of the rows read.
- It stops at `128 k`, the column count, which no rank exceeds, so its verdict is the full elimination's. A short rank
  still reads every row.
- `MaskRank` keeps only rep 0's row *positions*, as an ordering hint. Rep 1 rebuilds every row over all the points, and
  the rank doesn't depend on row order, so a rep 1 with other points or words still gets its own full check.
  Out-of-range positions panic, which fails closed, and repeated positions are harmless.
- It is a prover-side hiding guard (the prover stops on degenerate coins), so it changes nothing the verifier accepts.
  Its running time depends only on the public coins and mask-word positions.
- My own check: I copied `rank_scan`, `MaskRank` and the author's `rank_by_elimination` verbatim from `zk_veil.rs` at
  `23d545b51` and compared them with an independent GF(2) rank over a minimal GF(2^128) on CPU:
  - 1,500 one-shot trials (315 full rank, 1,185 short), over random, zero, one and repeated points, short, shuffled,
    duplicated and random word lists, and random `first` orderings;
  - 611 `MaskRank` reps across up to three reps;
  - 200 trials with repeated positions in `first`.

  All agree, and a mutant that stops one row early fails.
- Not yet run at `23d545b51`. I'd want two things; I haven't placed either:
  - bf16-hill's next zkaudit hill-climb at that commit, with the ZKRANK lines showing `rank == need` and `rows` near
    `128 k`;
  - `cargo test --release -p flock-live --features sha512 --features glue --lib zk_veil::tests` in the pod's checkout,
    after `backends/flock/pod/60-circuit.sh MODE=build`.

## Lever (b), prebuilding `zk_prepare` beside the previous session: I sign off on these conditions

Today `level0_zk` (ChaCha20 streams 6 and 7) and `Pads::draw` depend only on the seed and the statement's shape (`st.m`,
`zk_layout`). Nothing produced during the session enters, so prebuilding is sound provided:

1. **Checked like the prebuilt witness.** The bundle is checked the way the prebuilt witness is
   (`Arc::ptr_eq(&p.st, &tb.st) && p.seed == seed`), plus the plan's zk controls (`zk_zero_pads`, `zk_l0_tamper`,
   `zk_shared_pair`, `zk_pad_mismatch`). The statement is the one drawn after Register. On any mismatch the bundle is
   discarded and drawn in-session, and never used for another statement.
2. **The new session's salts and rank state.** The bundle's `LeafSalts` and `MaskRank` belong to the new session. Its
   salt ids are the ones the session would issue, and the session issues none of them again; a reused hm96 salt id
   reuses leaf salts across trees.
3. **Used once.** It is moved out by `take()`, and never persisted or cloned beyond the session's two reps.
4. **A fresh seed.** Each session's seed is a fresh `ProverSeed::from_os()` in a proving build, with no seed injection,
   and the hello's `coin_nonce(&seed)` uses the bundle's seed.

Evidence I'd want with it:

- a test that a bundle prepared for one (statement, seed) is discarded under any other;
- a test that no salt id is issued twice;
- a zkaudit hill-climb on the prebuilt path.
