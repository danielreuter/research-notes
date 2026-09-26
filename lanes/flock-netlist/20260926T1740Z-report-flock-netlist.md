---
id: 20260926T1740Z-report-flock-netlist
campaign: boolean-escape-hatch
lane: flock-netlist
kind: report
status: open
repo: danielreuter/verity
origin: cursor/flock-netlist-m0-4d6a
branch: cursor/flock-netlist-m0-4d6a
---

CHECKPOINT 0615b284 (20:12Z) [open] renamed to verity/flock-circuit; coin record replayable (global index g); prover deterministic with explicit seed; every commitment hash SHA-256 and pinned in the identity (HM96 Merkle leaf + serving row leaf left); L40S GPU selftest r20260926-200726-8dce running, then cells SiLU/RoPE/RMSNorm x2
CHECKPOINT f1112817 (18:41Z) [open] SiLU L40S cell ok (loopback 4.6 G AND/s e2e at 128 rows; ref-profile 3.3 G) r20260926-181746-69fe; step-0 coin seed + RMSNorm tails in circuit (lookups, two-phase device witness) landed; selftests of 4 templates on L40S r20260926-183942-576e
CHECKPOINT e231d583 (18:05Z) [open] GPU path works on RTX 4090 dev pod: device witness + multi-range fold, GPU selftests all-pass RoPE (k_log 20) and SiLU (k_log 26, private BLAKE3 parent tree) r20260926-175514-5b86; verifier-tail refusal + negative (Daniel's rule) landed; now timing r20260926-180450-ecfa; L40S hunter running (no stock); next RMSNorm tail in circuit (MUFU lookup slots)
CHECKPOINT 9fd167e1 (17:40Z) [open] started M0: verity/flock-circuit CPU statement landed (RoPE 19/19 CPU selftest cases incl relabelled circuit, SiLU in-circuit parent tree); next GPU device witness + multi-range fold; branch cursor/flock-netlist-m0-4d6a; agent bc-ff572e70
# flock-circuit: M0 `verity/flock-circuit` (NON_ZK, ZK-ready)

Spec: Project store `docs/boolean-prover-scoping.md` (M0 row, M0 acceptance, section 4). Agent bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a.

## Design (as built)

- One or more whole VUs per block; every glue inside a block is a copy constraint (Δ); no prover-supplied value, no glue claim.
- Slot types per block: BLAKE3 compressions (chunk runs per port; for a multi-chunk port its parent tree, root first), the
  template's units, a reserved mask slot (free cells, A = B = I), forced-zero padding apart from it.
- Public: frame-v3 roots, the row digests (serving leaves; unsalted until Daniel's call), declared outputs, the pinned layout.
  Chaining values, chunk values, every word between slots: private.
- The pinned composite circuit (`flock-circuit`, sha256 = pin) is the meaning: META (ports, ranges, compression roles, leaf
  and output maps, pinned padding-instance values, leaf-commitment scheme) + each slot type's `flock-ir-unit/v2` expanded circuits. The
  verifier derives Δ, regions and values from it and its own public file (no rows).
- Code: `backends/flock/python/verity_flock/circuit.py`, `backends/flock/live/src/{circuit,zk_hooks}.rs`, `bin/flock-circuit.rs`.

## Standing rule (Daniel, 18:01Z): the verifier evaluates no part of the computation

Tightens scoping §4.1 (no exception for functions of public data). Built into the statement: `Composite::parse` refuses a `CUT`
line in any NET and META keys `tail`/`cut`/`cut_words`/`public_ports`/`public`/`native`; negative `verifier_evaluated_tail_refused`
(both forms refused at parse). The verifier no longer evaluates the unit's expanded circuit on zero inputs to check the pinned padding
outputs (the circuit forces them; a wrong pinned value only makes the statement unsatisfiable). It still hashes a zero row to
check the pinned padding digest (the commitment scheme's own function) and recomputes the frame-v3 roots.

Sampling under the rule (not in M0 acceptance; estimate, not lowered): per vocabulary lane, Gumbel noise =
Philox4x32-10 (~15k ANDs/lane amortised) + libdevice `logf(-log1pf(-u))` (~24 fma + 5 mul + 3 add + add.rz + 3 cvt ≈ 125k
ANDs at the fp piece costs 4,498 / 2,406 / 823) ≈ 140k ANDs/lane vs 5,099 today (27x); V = 128,256 → ~1.8e10 ANDs/row;
#101's 32 rows → ~5.8e11 ANDs (+0.37% of #101's 1.57e14; ~+580 L40S-s at 1 G AND/s ≈ +1.1% of ~51k s). Top-p keep word
(MUFU EX2/RCP over whole-row reductions) in circuit: the scoping's x2 on sampling (another ~0.65 G ANDs/row) plus EX2/RCP
lookup slots (~40k ANDs each). Sampling carries become private Δ glue between consecutive lane units (free).

## Checkpoint results (18:25Z)

- CPU selftests: RoPE 20/20, SiLU (in-circuit BLAKE3 parent tree) all pass (local).
- GPU (RTX 4090 dev, then L40S): selftests all-pass RoPE k_log 20 and SiLU k_log 26 (runs r20260926-175514-5b86,
  r20260926-180609-0360); device witness = BLAKE3 kernel + new bit-sliced level-ordered unit kernel; multi-range fold.
- 4090 loopback timing (r20260926-180450-ecfa): SiLU 32 rows (707M ANDs, m=31, both reps) e2e 0.218 s = 3.2 G AND/s;
  device witness units 17 ms, compressions 4.5 ms per rep.
- Tail pieces: RsqrtApprox (954 ANDs), MufuSqrtFtz (148), DivFullRcp (5,657) exact vs the IR primitives on ~4k words (19
  NaN-payload-only differences in DivFullRcp from fp's canonical NaN, the lowering's existing policy). Lookup slot (lookup.rs):
  fast witness = its rows' evaluation (unit test). RMSNorm tails: fused 2 stages (27.7k + 0.2k ANDs) + 1 rsq lookup; Triton
  3 stages (8.5k + 3.3k + 5.0k) + sqrt + rcp lookups (DivFullRcp of the constant N folded).

## ZK-readiness choices as built (scoping §4)

1. **Private by default.** Public: frame-v3 roots, row digests, declared outputs, pinned layout. The verifier's own instance file
   (`pub-N.bin`) holds no row; `serve` refuses a file with rows. Every intermediate word is private Δ glue inside a block.
2. **One commitment, reserved room.** One root per statement bound by both reps (flock-128-r2, R1). Each block reserves a
   2^14-bit mask slot of free cells (A = B = I; zeros in M0, random cells accepted: negative `mask_cells_random` accepts),
   apart from forced-zero padding. `t_pad` is a hook (0 in M0). Single-run 2^-128 is NOT done: Flock's F128 PIOP union is
   2^-118.4 per run (flock-128), so a single run needs F256 challenges or a doubled PIOP on the same opening (M1/M2 item).
3. **Leaf commitments of the proof's Merkle trees:** a named, pinned, swappable scheme in META and the backend identity.
   Pinned today: `flock-leaf/sha256-unsalted` (Flock's own leaf) because the hiding leaf is NOT implemented yet; room
   reserved for HM96 (O(k) variant, k = 160: x of 6k+4 bits → 128 B reserved; universal-hash key (|x|+256 bits) → 160 B).
   The next id is `flock-leaf/hm96-sha256` (Daniel, 20:00Z; x from ProverRng stream STREAM_SALT), not a plain salted leaf.
4. **Live coins from a seed committed at step 0** (`coin_seed.rs`, SessionConfig.coin_seed): the verifier draws seed + nonce
   from the OS, answers Hello with `SHA-256(tag‖nonce‖seed)` (scheme `coin-commit/sha256`, HM96 the target), derives every
   coin with `verity.randomness.derive` (domain `verity/flock-circuit/coins/v1`, context = the hello; byte-compatible, pinned
   by a Python vector), reveals seed + nonce in the verdict; the prover checks the opening and every coin
   (negative `coin_seed_opening_forged`). Prime-field live coins with a committed seed are refused (not built).
5. **Masking hooks as no-ops** (`zk_hooks.rs`): sumcheck-round hook, `t_pad`, claim-point permutation, mask-fill slot, `zk`
   in the identity (pinned in the statement digest). **Prover randomness:** `ProverRng::from_os()` only (getrandom 256-bit
   seed per proof, ChaCha20 streams addressed by (purpose, index) for device expansion); no transcript input; the test-seed
   constructor is `#[cfg(test)]`; ignored TODO test `two_proofs_share_no_mask_bits` for M1.
6. **The circuit pin is the meaning.** The composite circuit's sha256 is `--pin`; the verifier derives Δ, regions and values from
   it alone (`relabelled_circuit` / `relabelled_circuit_refused_at_load` negatives).

## Cells so far

| template | cell | points | loopback e2e @ plateau | AND/s loopback | AND/s ref. profile |
|---|---|---|---|---|---|
| SiLU·mul i8192 (L40S US-TX-4, verifier RTX 4090 EU-RO-1, RTT 149 ms) | r20260926-181746-69fe / -181724-1f6a (check: no problems; NOT registered: stale leaf label, pre step-0; re-run pending) | 32 64 128 | 0.61 s @ 128 rows (2.83 G ANDs, m=33) | 4.6 G | 3.3 G |

## Naming (Daniel, 19:47Z)

The statement is `verity/flock-circuit` (no version in the name; versioning is by digest: the pinned composite circuit's
sha256 and the statement digest). Formats `flock-circuit` (the pinned composite circuit), `flock-circuit-inputs` (instance files);
scheme ids `flock-leaf/sha256-unsalted`, `coin-commit/sha256`; relation `circuit:<template>`; binary `flock-circuit`. "Expanded
circuit" names a slot type's gate-by-gate `flock-ir-unit/v2` form. One exception: the coin derivation domain is
`verity/flock-circuit/coins/v1`, because `verity.randomness.derive` requires `verity/<protocol>/<purpose>/v<n>`. Left as they are:
`ir_lower.netlist()` and `IrUnitNet`, owned by the lowering lane (called through one helper). Cells before 19:56Z ran under the
old id and are measurements only.

## Step 0 replayable from the record (verifier lane, 19:49Z)

Every seed-derived round in the session record carries `g`, its session-wide coin-request index; the link points carry
`points_g`; the record's `coin_seed` section holds the scheme, the domain, the derivation context (the exact hello), the
commitment, the request count and (once the verdict is issued) seed and nonce. `flock_live::replay_coin_seed(record)` /
`flock-circuit replay-coins --record session.json` re-derives every request from the record alone, however the reps interleave,
and checks that the indices are exactly `0 .. requests`. Selftest `coin_seed_record_replays`: an honest record replays (RoPE: 175
requests); the same record with two rounds' indices swapped is refused.

## The prover as a function of (statement, witness, prover seed, coins) (19:52Z)

`zk_hooks::ProverSeed` is an explicit input of every proof: `ProverSeed::from_os()` (getrandom) is the only constructor in a
proving build; `ProverSeed::injected` and the verifier's `Server::inject_coin_seed` exist only under the cargo feature
`seed-injection`, which `60-circuit.sh` enables for MODE=selftest and never for bench or cells (61-circuit-cell.sh builds without).
Selftest `prover_is_deterministic`: two sessions with the same injected prover seed and verifier seed give byte-identical proofs
(both reps) and transcripts (every round's message digest and coins, the link exchange, the proof digests); CPU passes on RoPE.
No message byte depends on scheduling: every parallel reduction is a GF(2^128) sum (XOR, order-free), device kernels are
deterministic, M0 draws no prover randomness into any message.

## SHA-256 for every commitment hash (Daniel, 20:00Z)

Audit of the statement's hash paths (commit 448092ae pins each in the backend identity, so the statement digest binds them):

| path | CPU prover | GPU prover | status |
|---|---|---|---|
| Ligerito Merkle trees (proof-internal) | SHA-256 | SHA-256 | done: `PcsParams.merkle_hash = Sha256`; the verifier checks params equality |
| round digests, statement digest, Σ | SHA-256 | SHA-256 | done |
| step-0 coin commitment and derivation | SHA-256 | SHA-256 | done (`coin-commit/sha256`; `verity.randomness` is SHA-256) |
| frame-v3 root tree | SHA-256 | SHA-256 | done |
| live-coin transcript | none | none | no hash: coins come from the verifier |
| Merkle leaf commitment | SHA-256, unsalted | SHA-256, unsalted | to do: `flock-leaf/hm96-sha256` |
| serving row leaf, hashed in the circuit | BLAKE3 keyed | BLAKE3 keyed | waits on lane salted-leaves' HM96-on-SHA-256 row format; `verity.commitments.rowleaf` is not this lane's |

The CPU prover's BLAKE3 was Flock's default Merkle hash, and this statement never used it: both provers build with
`HashKind::Sha256`. What is left is the two leaf constructions.

Cost (estimates from the layout; nothing lowered or measured yet):
- **Serving row leaf in the circuit, BLAKE3 → SHA-256.** A SHA-256 compression slot is 2^15 bits against 2^14 for BLAKE3, and
  SHA-256 is Merkle–Damgård, so there is no parent tree: a 4 KB row costs 65 compressions (64 blocks + padding) instead of
  4 chunks × 16 plus 3 parents. The four M0 templates stay at the same k_log because the extra rows fit in each block's slack,
  so proving time is about unchanged; the device witness gains a SHA-256 kernel (a few ms per rep). HM96 on top adds about
  1–2 compressions per row (the universal hash of x plus the extra block).
- **HM96 internal Merkle leaves.** About +1–3% of Merkle hashing (one extra SHA-256 block per leaf plus the universal hash), and
  about +150 KB per proof: each opened leaf carries x (121 B) and the key (160 B), about 14% of a ~1.1 MB proof. The work is
  a Flock CPU leaf function, the CUDA Merkle kernel patch and the opened x and key in the proof format (about 1 agent-day).

## For the formal ZK plan (flock-soundness; M1/M2 spec, no M0 scope change)

What M0 exposes for a formalizable M1 masking spec:
- **Randomness tape.** All prover randomness is `ProverRng` = ChaCha20 keyed by the 256-bit `ProverSeed`, independent streams
  `(purpose, index)` (`STREAM_MASK` 1, `STREAM_SALT` 2, `STREAM_PAD` 3; word position 8·index). A simulator's tape is these streams.
- **Mask placement.** Per block, one 2^14-bit region of free cells (A = B = I) at a pinned position, apart from forced-zero padding;
  the zerocheck/lincheck claim points are fully random (reach every cell); the public region claims fix Boolean coordinates outside
  the mask region (they reveal only public data).
- **Hooks** (`zk_hooks::Hooks`): sumcheck-round message hook (`+ρ·g`), `t_pad` per Ligerito level, claim-point permutation,
  mask-slot fill, `zk` in the identity. The M1 spec must pin, per message: the mask distribution (uniform over the free cells and the
  t_pad ≥ queries padding rows; masking polynomials' degree and support), where it enters (each sumcheck round's univariate, the
  ring-switch `s_hat_v`, each Ligerito level's opened rows and final vector, the claim values), and the simulator (the verifier's
  coins fixed at step 0 by the seed commitment; leaves by HM96 openings).
- **Coins.** Step-0 seed commitment + `verity.randomness` derivation, replayable from the record (above); HM96 is the target commitment.
