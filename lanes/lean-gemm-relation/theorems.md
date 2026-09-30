---
cursor:
  subagentId: "bc-590cc416-b61a-523d-84f5-280ce207a815"
---

# Prover-security theorems in Lean: status, assumptions, records

**For:** the security theorem table (overnight objectives §4, morning deliverable 4). **Read from:** `main` at `b82f1dd2`
(train TX2), the three packages' `lean-audit.json`, `soundness/README.md`, `soundness/FlockSoundness/Assumptions.lean`,
and the open ZK PRs #227, #239 and #245 at `21b0edb0`. **Written:** 2026-09-30 05:30Z by lane lean-gemm-relation.

**Every theorem below is proved with 0 `sorry`.** `check`'s Lean audit (`tools/lean/audit.py`) fails a package on any
`sorry`, `axiom` or `native_decide`, replays every declaration through the kernel, and allows only Lean's three standard
axioms (`propext`, `Classical.choice`, `Quot.sound`); `main` merges only through a passing `check`. No soundness source
file on `main` contains the word `sorry`. So the "Lean axioms" of every row are those three, and the column that matters
is the cryptographic and modelling assumptions. A named assumption is a `Prop` in `FlockSoundness.Assumptions`
(A2–A5), taken as a hypothesis; the others are named hypotheses of the theorem itself.

**Record** means the pin in the package's `lean-audit.json` (`pins[<name>]`: signature, named assumptions, SHA-256 type
hash, first 8 hex digits shown). Packages: `soundness` = `backends/flock/verifier/lean/soundness`, `exec` =
`backends/flock/verifier/lean` (the executable verifier), `verity` = `packages/verity/lean` (new, lean-gemm-relation).

## 1. Flock interactive soundness (one table, `fast100` profile, two reps on one root)

| Theorem | What it says | Status | Assumptions | Record |
|---|---|---|---|---|
| `FlockSoundness.table_sound` | Oracle layer: Pr[verifier accepts both reps ∧ no codeword within the level-0 radius packs a satisfying witness] ≤ `tableError(fast100 m, shape)`, for every prover strategy | proved, pinned | none cryptographic: statistical, live coins, holds against quantum provers. Hypotheses: `A.Correct` (field arithmetic), `Statement.LinkLayout` (link-point layout) | soundness, `83f5ae9c` |
| `FlockSoundness.table_sound_exec_fast100`, `…_34_35` | The same for the executable's arithmetic: ≤ 2^-205 for 22 ≤ m ≤ 33, and for m = 34, 35 | proved, pinned | `LinkLayout` only (`A.Correct` discharged by `execArith_correct`) | soundness, `ab1d6e72`, `f50795c9` |
| `FlockSoundness.table_sound_compiled` | Compiled layer (SHA-512 Merkle caps, openings at the end, round bytes kept by the coin server): the same event ≤ `tableError` + √(N₀·2Q₀·Adv₀) + Σ√(N_ℓ·Q_ℓ·Adv_{rep,ℓ}) + Adv_× | proved, pinned | **no random oracle, no hypothesis on SHA-512**: collision resistance enters as the success probabilities of explicit collision finders (`adv₀`, `advR`, `SelfClash`). Under the generic bound, ≤ 2^-128 up to t ≈ 2^110.7 hash evaluations (m = 35). Hypotheses: `A.Correct`, `LinkLayout` | soundness, `6a05240e` |
| `FlockSoundness.Merkle.opening_binding` | Two verified openings of one position with different columns give a hash collision (exists) | proved, pinned | none: the conclusion is `Collision H` (binding under collision resistance) | soundness, `ccc56b50` |
| `Flock.merkle_binding`, `Flock.opens_binding` | The executable's `merkleCheck` / `opens`: two accepted openings that differ give a collision of the scheme | proved, pinned | none: conclusion `MerklePair.Collides` | exec, `b23c3c4a`, `fa8219a1` |
| `FlockSoundness.table_knowledge_sound`, `…_joint_tight`, `session_knowledge_sound` | Knowledge soundness: extraction fails with probability ≤ ε_c⁻ + K·Adv₀ + N₀/(eK) | proved, **not pinned** | explicit collision-finder terms, as compiled | none (the README cites them; the soundness lane holds the list of cited-but-unpinned theorems) |
| `registered_weights` | Extracted rows equal the registered weights, or a SHA-512 collision | **to write** | SHA-512 collision resistance (Halevi–Micali binding) | none |
| Fiat–Shamir (non-interactive) | — | **not in Lean** | SHA-512 as a random oracle; the Lean model is interactive with live coins, and C-fs is out of scope (`soundness/README.md` §2) | none |

## 2. Verifier refinement (Stage 2: the executable Lean verifier against the model)

| Theorem | What it says | Status | Assumptions | Record |
|---|---|---|---|---|
| `FlockSoundness.Refine.verify_refines_ofCircuit` | `Flock.verify` accepting a record for a circuit's statement implies the decoded session, schedule, proofs and rounds exist and the model's reps accept them | proved, pinned | SHA-512 Merkle scheme (`hms`); `StmtWF`, `RegionsWF` (statement well-formedness, which discharge `FoldRealizes`/`ExtraRealizes`) | soundness, `c95258fa` |
| `FlockSoundness.Refine.verify_refines`, `verify_tableAfter` | The same for any setup, with `FoldRealizes` and `ExtraRealizes` as hypotheses | proved, pinned | `FoldRealizes`, `ExtraRealizes` | soundness |
| `FlockSoundness.Refine.live_le_tableC` | The transfer (R11): against any live prover, Pr[live verdict] ≤ Pr[compiled model accepts] against the simulated prover | proved, pinned | `Decodes` (every accepted live run decodes to accepted model runs), which R11b's refinement and framing provide: in flight (#432, lincheck frames) | soundness, `511de591` |
| `FlockSoundness.Refine.stmtOf_linkLayout` | A circuit's statement satisfies `LinkLayout` | proved, pinned | none | soundness, `0afc72ab` |
| One theorem from `Flock.verify`'s acceptance to "the committed values satisfy the named circuit" | — | **not yet**: `Decodes` (R11b) and the lowering's last link (`NetRows` for flat typed classes, #430/#441) remain; `soundness/README.md` §1.4 still lists Stage 2 as "to write", which the pins above have overtaken in part | — | — |

## 3. Audit-level integrity (sampled audits over a partition)

| Theorem | What it says | Status | Assumptions | Record |
|---|---|---|---|---|
| `FlockSoundness.Audit.audit_window`, `audit_work` (and the `extraction_…`, `_of_record`, `_closure` forms) | Pr[audit accepts ∧ unsound work ≥ T] ≤ ((W − T)/W)^K + ε_ks + δ_link, for the stratified draw law | proved, pinned | per-unit terms named as hypotheses: `KnowledgeSound ε_ks`, `LinkSound δ_link` | soundness, `d289ec9d`, `ac0da82d` |
| `FlockSoundness.Audit.Partition.flock_e2e_drawn_exec`, `flock_e2e_count_exec` | End to end for Flock's batched session: Pr[accepts ∧ a drawn unit is wrong] ≤ the knowledge term + the link bound | proved, pinned | **A2 `SHA512ExpectedTimeCR`** (expected-time collision resistance of SHA-512, T/2^256, for the explicit link finder); `ValueBinding`; `RowsL1` (L1: each template's rows compute its gates; proved for RoPE, `Rope.rope_sound`); `DerivedPlaces` | soundness, `058db831`, `d489ff81` |
| `FlockSoundness.Audit.Law.execOS_escape_le`, `drawOS_*_escape_le` | The verifier's own unit draw from `IO.getRandomBytes` escapes with at most the law's probability | proved, pinned | **A3 `UniformRandomBytes`** (`uniform/io-getrandombytes`) | soundness, `ad1d1e21` |
| `FlockSoundness.Audit.Law.keyedWindow_audit_of_record` (and the `Reg`, `extraction_` forms) | The PoUW window audit from `verity.randomness`'s keyed streams | proved, pinned | **A4 `KeyedStreamsUniform`** (`prf/sha-256`: SHA-256's compression function as a PRF), **A5 `UniformSecret`** (`uniform/python-secrets`), plus `KnowledgeSound`, `LinkSound` | soundness, `b114ae84` |

## 4. Zero knowledge

| Theorem | What it says | Status | Assumptions | Record |
|---|---|---|---|---|
| Theorem Z (public circuits): one batched session of C-Flock ZK is ZK against a malicious verifier with auxiliary input, within 2^-166.7 + J·2^-159 + PRG | — | **paper proof**, red team granted (`docs/zk-proof-public.md`) | PRG (ChaCha20 as uniform prover randomness); SHA-512 collision resistance under a random prefix (A2ν) for the coin tree's binding; Halevi–Micali leaf hiding (statistical, no random oracle) | none |
| `FlockSoundness.ZK.card_translate_fiber`, `padding_surjective`, `padded_openings_uniform`, `level0_openings_uniform`, `gk_ratio_le_third` (#227) | The statistical core: padded openings are uniform; masking through a surjective map | proved, pinned in the PR, **not on `main`** | none | soundness at #245's head, 32-bit records (pre-#329, need `--update`) |
| `FlockSoundness.ZK.triShift_bijective`, `card_fiber_eq_of_triShift`, `card_seq_masked`, `run_eq_iff`, `card_run_eq`, `card_run_eq_of_triShift` (#227) | The bijection lemma's backbone and the adaptivity step | proved, pinned in the PR, not on `main` | none | as above |
| `FlockSoundness.ZK.coin_opening_binding` (#239), `coin_opening_binding_keyed` (#245) | Two disagreeing openings of the verifier's coin commitment (keyed tree: under the session prefix) imply a collision exists | proved, pinned in the PRs, not on `main` | none: conclusion is a collision (binding under CR) | as above |
| Private-circuit ZK: ≈ 2^-143 over 2^20 sessions, plus PRG and ε_T (missed deadlines) | — | **paper proof**, red team re-granted (`docs/zk-proof-private.md`); nothing private-track-specific in Lean | PRG (ChaCha20; 512-bit seed for long-lived salts), A2ν, measured (not proved) deadline term ε_T | none |

## 5. The circuit relation (new tonight)

The Lean semantics is tied to the Python by 108 kernel-checked vectors (48 Hopper steps, 32 Ampere/Ada steps with 8 RTX 4090 captures, 28 `cvt_rn_bf16_f32` words) (`Verity.TC.Vectors`), which `packages/verity/tests/ml/test_lean_vectors.py` checks against `tc_dot_total`. Recorded audit on vy-nebius-1: PASS, 18 pins, 1,637 declarations. The relation differs from `check_step` in one place: the witness shape is fixed (the Python checker accepts truncated witnesses; low finding, `private/lean-gemm-relation/`). Everything `relation.py` encodes for a BF16 unit is covered: steps, groups, the unit chain, the boundary and the gadgets.


| Theorem | What it says | Status | Assumptions | Record |
|---|---|---|---|---|
| `Verity.TC.hopper_step_sound` | Every witness `verity.ml.tc.relation`'s k16 step relation accepts, for the input state `decode_state(acc)` and operand words `a`, `b`, outputs `decode_state(tc_dot_total(acc, a, b))`: Hopper pipeline (`groups = (16,)`, `W = 26`, floor −133; `HOPPER_BF16_WGMMA_K16` = `HOPPER_BF16_M16N8K16`, H100 and sm_120), either alignment mode, over the integers | proved, pinned, 0 sorry ([PR #490](https://github.com/danielreuter/verity/pull/490), draft) | none: unconditional | verity (`packages/verity/lean`) |
| `Verity.TC.hopper_step_complete` | The relation accepts a witness for every input in `tc_dot_total`'s domain (the honest witness, which equals Python's `step_witness` column for column on 60 checked vectors) | proved, pinned, 0 sorry (#490) | none | verity |
| `Verity.TC.hopper_step_iff` | The states the relation can output are exactly the one the semantics gives | proved, pinned, 0 sorry (#490) | none | verity |
| `Verity.TC.hopper_step_hw` | Under the assumption, the relation's output is the decode of the word the device writes | proved, pinned, 0 sorry (#490) | **`gemm-hopper-step(arch, bf16)`** (`Verity.Assumptions.GemmHopperStep`: the device's k16 step is `tc_dot_total` on the Hopper pipeline) | verity |
| `Verity.TC.hopper_unit_sound`, `hopper_unit_sound_zero` | A verification unit: the relation's steps chained through their output states output the decode of `tc_dot_total` folded over the unit, from any accumulator word or from `zero_state` | proved, pinned, 0 sorry (#490) | none | verity |
| `Verity.TC.ampere_step_sound`, `_complete`, `_iff`, `ampere_unit_sound`, `ampere_unit_sound_zero` | The same for the Ampere/Ada pipeline (`AMPERE_BF16_M16N8K16`: two groups of eight, `W = 25`, floor −132; A100 and RTX 4090); the two groups chain through the first group's output state | proved, pinned, 0 sorry (#490) | none: unconditional | verity |
| `Verity.TC.ampere_step_hw` | Under the assumption, the Ampere relation's output is the decode of the device's word | proved, pinned, 0 sorry (#490) | **`gemm-ampere-step(arch, bf16)`** (`Verity.Assumptions.GemmAmpereStep`) | verity |
| `Verity.TC.ada_eq_ampere` | `ADA_BF16_M16N8K16` has Ampere's parameters, so the Ampere theorems cover it | proved, pinned (#490) | none | verity |
| `Verity.TC.pack_sound_complete` | The unit boundary (`relation.pack_relation`: the FP32 word, then `cvt.rn.bf16.f32`): for every admissible final state its columns are forced to `pack_value` and `cvt_rn_bf16_f32` of it, and some columns satisfy it | proved, pinned, 0 sorry (#490) | none | verity |
| `Verity.TC.hopper_unit_bf16`, `ampere_unit_bf16` | A whole verification unit, from `zero_state` through its chained steps to the committed BF16 word: the relation accepts only `cvt_rn_bf16_f32` of the semantics' accumulator | proved, pinned, 0 sorry (#490) | none (with `_hw`'s assumption it is the device's word) | verity |
| `Verity.TC.Gadgets.range_gadget`, `iszero_gadget` | `Census.RANGE`'s 16-bit chunks and `Census.ISZERO`'s 12-bit chunks and flags hold exactly when the predicates the relation uses do | proved, pinned (#490) | none | verity |

## Gaps worth a line in the morning report

- Knowledge soundness's theorems are proved but not pinned; any table that cites them cites an unrecorded statement.
- The ZK Lean lemmas are in three open PRs with 32-bit pin records; they need `--update` to SHA-256 when they land.
- Nothing in Lean covers Fiat–Shamir, Theorem Z itself, or private-circuit ZK; the Lean model is interactive.
- `soundness/README.md` §1.4's Stage 2 row ("to write") is behind the pinned refinement pieces.
