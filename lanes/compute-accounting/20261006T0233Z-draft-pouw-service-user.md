---
id: 20261006T0233Z-draft-pouw-service-user
campaign: pouw
lane: compute-accounting
kind: draft
status: draft
repo: verity
origin: pouw-service
---

# PoUW as a user of the proof service

Read at `origin/main` `c305471c5` (Oct 6 01:58Z). `benchmarks/pouw/hidden_zk/` isn't on main; it was read at
`origin/cursor/pouw-zk4096-e3fa` `9aac7c4a3` (#1034). The service design read is proofs'
`internal/recursive-zk-system-architecture.md` (5 Oct, 4:55 PM PDT), and PoUW's current state is
`note:20261005T2318Z-draft-consolidation`. Paths are relative to the repository root. PoUW's Python lives under
`verity/protocols/accounting/work/pouw/`, written `pouw/` below. Anything marked *(unverified)* or *(estimate)* was
not checked or measured.

## The short version

- **Most of PoUW's infrastructure is already the service's in another form.** PoUW keeps its own copies of the
  commitments, salt and draw coins, three draw implementations, the openings' transport, the replay verifier and the
  audit record. The service replaces all of them.
- **What PoUW keeps is the four things it states:**
  - the row schemas;
  - the work-weighted policy and its work table;
  - the `pc8` hidden tile check as a Program;
  - the credit rule and the γ theorems.

  The noise derivations stay too, because they are part of the check.
- **The composition point already exists in Lean.** `pearlCHiddenSm120v1LoopCast8p72Rev1Cap1000_8192`
  (`verity/Security/Proofs/Pouw/PearlC/HiddenGamma.lean`) gives the served γ (0.36949% at 8192³). It is conditional on
  `TileProofSoundAll` at some `ηzk` (`Specs/Pouw/Assumptions/PearlC/HiddenTile.lean`). The service discharges that
  obligation with `RecursiveSound`'s error, once `VBridge` is proved.
- **One design conflict decides the rest.** Pearl-C's per-call noise seed is
  `seed_A = H(salt ‖ root_A ‖ root_B ‖ index)` (`pouw/schemes/pearl_c.py` `unit_seed_a`). So forming waits for A's
  commitment root inside every call, in decode's critical path. Under the service, that root is a salted hm96 root
  computed by the developer's gateway, which the GPUs must never see the salts of. A gateway round trip per call doesn't
  fit decode. Publishing an unsalted root instead leaks A to a dictionary attack. Either the noise moves to the epoch's
  coins (Daniel's precommitted-circuit variant), or `seed_A` moves into gates as in `ncp-v2`. Question 1 at the end.
- **The served scale doesn't fit as configured.** The work law's K = 27,713 draws per window, at ε = 0.1% and
  δ = 2⁻⁴⁰. With each drawn decode tile's closure of about 130–290 units, that is millions of proved units per window.
  `hidden_zk`'s measured Lean verify is 4,777–5,841 s for one 16-instance row session. Recursion fits only if a window's
  units are proved in a handful of large sessions, and if the audit window is decoupled from the 15-minute coin epoch.

## (a) What PoUW owns today, and what the service replaces it with

### Commitments and hashing

| What | Where | Under the service |
|---|---|---|
| Hash formats h0, h1, h2, h3: tree hash, BLAKE3 message and leaf labels, `seed_a` mode | `pouw/serving.py` `HashFormat`, `HASH_FORMATS`, `hash_format`, `SchemeId`'s hashing suffix | **Replaced** by the service's one commit format (hm96-sha512). The scheme name loses its `-h*` suffix. |
| Row and tile trees: framed SHA-256 by default, `frame-b3` or `frame-b3s` by `commitment_hash` | `pouw/audit.py` `commitment_hash`, `rows_domain`, `weight_binding`, `activation_binding`, `commit_rows`, `weights_root`, `transcript_domain`; core `verity/primitives/commitments/merkle.py`'s BLAKE3 modes (only PoUW and `experimental/.../multiproof.py` use `blake3-s256`) | **Replaced** by `commit`, with frame-v3-sha512 trees over hm96 leaves. The domain bindings become the service's served and registered domains. |
| The tile leaf: h0 TurboSHAKE128 per row and 32-column chunk, then over those digests; -h1/-h2 keyed BLAKE3 | `pouw/schemes/pearl_c.py` `message_digest`, `leaf`, `digest_keys`; in gates, `pouw/circuit/leaves.py` `PearlTileDigest`, `tile_digest` on `circuit/hashes.py` `KeccakP1600R12` | **Stays: protocol semantics.** It is the lottery's ticket and the hiding tile's compressed output (281 Keccak-p per 64 × 64 tile). The BLAKE3 variants go. If the lottery is dropped on served work (question 2), the tile unit could instead output C̃ and U as committed rows. That trades 32 KiB of commitment per tile against 281 permutations in gates. |
| Row schemas and layouts: `SCHEMAS`, `ROW_WORDS`, `ROW_SCHEMA`, `words_*`, `ok_of` | `pouw/circuit/leaves.py` | **Stays: protocol semantics.** This is "what is committed": each row's words and its role. |
| Row digest, commit string and tree leaf; the statement's META rows | `pouw/circuit/leaves.py` `row_digest`, `commit`, `tree_leaf`, `statement_rows` | **Replaced.** `commit` produces b ‖ c and the leaves. The service builds META from the Program's ports. |
| `ncp-v2`'s in-circuit A tree: D_s, an RFC 6962 SHA-512 tree D_A, key K | `pouw/circuit/ncp2.py` (`NcpDigest`, `NcpNode`, `NcpKey`), `circuit/reference.py` `row_digest`, `strip_digest`, `node`, `root`, `key` | **Stays: protocol semantics**, because K is Fiat-Shamir inside the check. An option would read the service's per-call root as an anchored input instead, dropping two templates. That moves digests, and A's commitment would then precede K, which is the property the in-circuit tree gives today. |
| GPU hashing kernels: h0, h1 and h2 trees and leaves, message digests, A's tree, seed_A | `benchmarks/pouw/pearl_c/hash.cuh` (366 lines), `hash_h2.cuh` (205), `hash_sm120.cuh` (321); `benchmarks/pouw/pearl_c_sm120/h2_rows_stats.cuh` (43); `benchmarks/pouw/pouw_hash/` (2,483, superseded); the hashing steps of `pearl_c_sm120/run.py`'s pipeline (`pad_a`, `node_keys_a`, `hash_rows_a`, `tree_a`, `seed_a`, `hash_msg`, `hash_leaf`; category map in `pearl_c_vllm/profile_decode.py`) | **Replaced**, apart from the TurboSHAKE tile leaf if it stays. The GPU half of `commit` becomes a service kernel: unsalted SHA-512 row-seg digests, which the gateway salts. |
| vLLM's on-device commitment: `_Keys`, the weight-side tree (`weight_roots`), per-call A trees, the pass's tile tree | `integrations/vllm/verity_vllm/protocol_options/pouw_pearl_c_device.py` (798 lines; about 250 of them commitment, *estimate*) | **Replaced** by `commit` calls from the executor. |
| `ncp-v2` serving's own SHA-256 leaves: `unit_leaf`, `units_root`, `calls_root`, `WeightRecord`, `inputs_digest` | `integrations/vllm/verity_vllm/protocol_options/pouw_circuit.py` (470 lines), built on `audit.commit_rows` and `protocol.tagged` | **Replaced** by `commit`. Today's leaves aren't hiding (SHA-256 over values). |

### Randomness

| What | Where | Under the service |
|---|---|---|
| The epoch salt: `derive(beacon, "verity/pouw/salt/v1", {weights})`, the beacon a drand quicknet round checked by BLS | `pouw/audit.py` `Epoch.start`, `Epoch.unverified`; core `verity/primitives/crypto/beacon.py` (111 lines) and `bls12_381.py` (391). PoUW is the only importer of `beacon` outside `crypto/` (grep) | **Source replaced, use stays.** The salt becomes the service's epoch coins, issued after the epoch's commitment: the workload declaration and `weights_root`. That is Daniel's precommitted circuit. The salt as the noise's seed is protocol semantics. |
| The per-matmul noise: seed_A, seed_B, Pearl's line rule, the F bases, G, E′ | `pouw/schemes/pearl_c.py` `unit_seed_a`, `_labelled`, `_basis`, `gram`; `pearl_kw.sample_line`; `circuit/anchors.py` `TileAnchors`, `Derivation`, `public_ports`; `pc8.DERIVATIONS`, `SEEDS` | **Stays: protocol semantics.** The check reads it, as public input regions. What changes is the *input* to seed_A (question 1). The service only carries the regions file (C-Flock's `--public-inputs`). |
| `ncp-v2`'s noise: E₁ and F₁ from SHAKE256 of K or the salt | `pouw/circuit/ncp2.py`, `reference.py` `e1_row`, `f1_col` | **Stays: protocol semantics** (in gates). |
| The audit's draw coins: `derive(source, "verity/pouw/audit/v1", {transcript, salt})` | `pouw/audit.py` `Sampled.select` | **Replaced** by the service's live coins, drawn after the registration receipt. |
| Pearl-C's draw beacon: `Beacon`, `derive(beacon, "verity/pouw/pearl-c-draw/v1", {round, transcript, records, …})` | `pouw/schemes/pearl_c_work.py` `Beacon`, `draw` | **Replaced** by the service's draw coins. |
| The window's fresh source and its record (root's C1 and C2) | `pouw/circuit/anchors.py` `_fresh_source`, `Ledger.open`, `Ledger.record`, `replay_key`; `circuit/plan.py` `DRAW_DOMAIN` | **Replaced.** These are exactly the verifier gateway's job: coins after the receipt, used once, then recorded. |
| The replay's draw source: `os.urandom(32)` after the transcript; Pearl-C4's Fiat-Shamir beacon shortcut | `benchmarks/pouw/pearl_c_vllm/verify_run.py`; `benchmarks/pouw/pearl_c4/replay.py` | **Replaced**, along with the replay itself. |

### Draws (unit selection)

| What | Where | Under the service |
|---|---|---|
| t independent work-weighted draws with replacement; integer tickets ∝ a tile's share of W_ref | `pouw/audit.py` `tickets`, `Sampled` (Lean `WorkWeightedSampling`) | **Replaced** by `sampled_proofs`' `work:K` law (`one_stage/draw.py`; the Lean `flock-verify draw`). |
| Pearl-C's credited-cell tickets and the tile weight | `pouw/schemes/pearl_c_work.py` `cell_wref`, `DrawWref`, `draw_wref`, `ticket_cell`, `tile_weight`, `tickets`, `work` | **The weights stay; the sampler goes.** The weights are protocol semantics and become PoUW's work table. The service's law weighs per template, and credited cells vary per tile, so see requirement R7. |
| Exclusion tiles: one tile per excluded row | `pearl_c_work.exclusion_tiles` | **Stays: protocol semantics**, as a deterministic selection the service must accept beside its draw (R8). |
| The lottery: digest ≤ target·cells·k | `pouw/audit.py` `Lottery` | **Stays: protocol semantics** (Pearl's mining rule), but see question 2. |
| The closure-draw machinery: `CountLaw`, `WorkLaw`, `record_k`, `window_laws`, `check_work_strata`, `draw`, `Plan`, `law_object`, `openings`, `profile`, `unsound_work_bound` | `pouw/circuit/plan.py` (398 lines); `circuit/__init__.py` `Traced.draw`, `check_openings`, `check_link` | **Sampler, law and record replaced** (about 250 lines, *estimate*). Kept as PoUW's statement of the policy: `layout`, `tile_layout`, `template_strata`, the closure map (`Plan.proved_b`, `proved_y`), the work table's values and floors, and K or (ε, δ). |
| The window ledger's refusal of a repeated call index (A11 `UniqueCallIndices`) | `pouw/circuit/anchors.py` `Ledger.admit`, `Receipt` | **Replaced** by the service's registration and receipt (R1–R7 in `one_stage/registration.py`). PoUW states "a call index is unique" as a rule the registration checks. |

### Transports

| What | Where | Under the service |
|---|---|---|
| The retained pass: A's BF16 rows and tree levels per call, B's rows and levels per weight, the leaves, the tile tree; poisoning; the manifest | `pouw_pearl_c_device.py` `_Pass`, `begin`, `poison`, `end`, `_write_retained` (manifest `verity-vllm/pouw-pearl-c-run/v1`); `pouw/serving.py` `MANIFEST_SCHEMA`, `MANIFEST_SCHEMAS_READ` | **Replaced.** Under ZK no row leaves the developer. Only hashes go to the verifier gateway, and witnesses go to the prover workers. Poisoning stays as a kernel gate. |
| Openings: `TileOpening`, `Prover.open`, the device-layout paths | `pouw/audit.py`; `benchmarks/pouw/pearl_c_vllm/verify_run.py` `opening`, `Files` | **Replaced.** Nothing is opened. |
| Pearl-C4's device dump to transcript v0 | `benchmarks/pouw/pearl_c4/replay.py` (342 lines) | **Replaced.** |
| Staging statements for C-Flock: circuit, instances, public inputs and pin; the anchors file and its controls; loopback sessions | `hidden_zk/stage.py` (182 lines), `fast_stage.py` (368), `job.sh`'s `session()` (on #1034) | **Replaced** by the service's `session` and `prove_zk`. The controls (wrong or prover-chosen anchor, tampered row, flipped bit) become the service's own tests. |

### Custody and records

| What | Where | Under the service |
|---|---|---|
| What a pass publishes before any draw | `pouw/serving.py` `PassCommitment` | **Replaced** by the registration record and the service's hashes and roots. |
| Pearl-C's per-call declaration: real rows, kept width, excluded and voluntary rows, splits | `pearl_c_work.UnitRecord`, `Split`, `records_root`, `check_records`, `declare`, `volunteer` | **The content stays (protocol semantics: part of what is committed); the root goes.** It is committed through the service before the draw. `records_root`'s SHA-256 becomes a `commit`. |
| The audit's outcome: `Audit`, `Verdict`; the replay's `verify.json` | `pouw/audit.py`; `benchmarks/pouw/pearl_c_vllm/verify_run.py`, `verify.sh` (22 lines) | **Replaced** by the service's audit record (`one_stage/audit.py`, format `verity/one-stage/audit/v0`). |
| `WorkProfile`: certified work (1 − γ)(1 − ε_s)·W, δ_s, the certificate | `pouw/audit.py` `WorkProfile` | **Stays: protocol semantics**, as PoUW's reading of the service's `IntegrityProfile` together with its certificate. Its `delta_s` should come from the service's profile, not from `(1 − ε)^t` over its own draw. |
| The proof's identifier v1: scheme, salt, workload | `pouw/identifier.py` (75 lines) | **Stays: protocol semantics** (the statement's context). The service must bind it into the session's record (R10). |
| The verdict plumbing: per-config summaries, Lean checks judged against expected verdicts | `hidden_zk/summarize.py` (114 lines), `timed.py` (19), `scope.sh` (23) | **Replaced** by the service's verdict record. |

### Verifiers

| What | Where | Under the service |
|---|---|---|
| Replay as verdict: openings, then `encode`, `admissible`, `checked` and `digest` | `pouw/audit.py` `Verifier`, `check_tile`, `audit` | **Replaced** as the verdict, and kept only as a labelled diagnostic (consolidation ruling 5). |
| Pearl-C's replayed work law: filler zero, kept width, per-row rules, R1, the debit against ρ·credit | `pearl_c_work.audit`, `audit_replay`, `_audit`, `check_drawn`, `check_opened`, `_debit_cap` | **The rules stay (protocol semantics), but they must move into the Program.** The cap is in `circuit/cap.py` as opt-in. R1, filler and kept width are not in `pc8` yet (PROTOCOL.md: "Not in it yet: the debit and the cap, R1, D-24"). Until they are, the service can't replace this check. |
| The served replay: about 11 CPU-s per tile per 1,024 of k, batch forms | `benchmarks/pouw/pearl_c_vllm/verify_run.py` (243 lines), `verify.sh` (22), `fast_tile.py` (333) | **Replaced.** |
| `ncp-v2`'s replay check | `integrations/vllm/verity_vllm/check/replay/pouw_circuit.py` (377 lines) | **Replaced** by the service's verify (*unverified* that nothing else uses it). |
| The CPU reference: `schemes/pearl_c.py`, `pearl_c_work.py`, `pearl_c4.py`, `ncp.py`, `circuit/reference.py` | `pouw/schemes/`, `pouw/circuit/` | **Stays: protocol semantics.** It is the Programs' spec and their vectors. |
| Rust `verify --zk` and Lean `flock-verify verify --zk` on staged units, plus building both | `hidden_zk/job.sh` (256 lines: `build_circuit`, `build_lean`, the Lean pool) | **Replaced** by the service's `verify` (Lean, the verifier of record). |
| Development C-Flock pieces for core primitives and the Keccak words | `hidden_zk/core3_scratch.py` (24 lines), `hash_scratch.py` (57) | **The backend's** (registered lowerings, `cursor/pouw-zk4096-reg-e3fa`), not PoUW's. |
| PoUW's Lean: `TileCheck.Accepts`, `GγSampled`, `GγHidden`, `EndToEnd`, γ | `verity/Security/{Definitions,Specs,Proofs}/Pouw/` | **Stays: protocol semantics.** The C-Flock Lean verifier is the service's. |

### Gateways

PoUW has none. Three pieces stand in for one:
- for coins, the drand check (`Epoch.start`) and `anchors.Ledger`, a verifier-gateway stand-in inside the verifier
  process;
- for the prover side, vLLM's `PearlCDeviceRun` and its retain directory;
- for egress, nothing.

All of this becomes the service's prover gateway and verifier gateway.

## (b) PoUW written as a service user

### Pearl-C on sm_120 (the served scheme)

**1. What is committed.**

| When | Rows | Role and format |
|---|---|---|
| Per epoch, before the coins (the precommitted circuit) | The declared workload W: every matmul's index, (m, k, n) and weight id (`identifier.workload_json`). Each weight's rows B_j as `pouw/row-fp32/v1` (k FP32 words; BF16 widened exactly) | W, `sha512/row/v2` |
| Per epoch, after the coins: the weight side | B̃_j ‖ P_B,j (`pouw/row-fp8-p/v1`) and B's ok row | W, row/v2 |
| Per call, in serving | A_i as `pouw/row-fp32/v1`, one leaf per row and one tree per call (the matmul index) | X, `sha512/row-seg/v1` |
| Per call, after the draw (if R6 holds) or in serving | A′_i ‖ P_A,i (`fp8-p`) and ok; the tile digest (`pouw/tile-h0/v1`); at served k, `rowk`'s pc8-head, pc8-carry and fp8-codes | X; v2 except fp8-p (seg) |
| Per call, before the draw | The call's `UnitRecord` | — |

Notes on the table:
- All of it is hm96-sha512 in frame-v3-sha512 trees. Each tree's registration domain binds (schema id, word count,
  role) (`leaves.py` docstring).
- The weight side would be committed through the service's registered values (`one_stage/registered.py`), except that
  those are `hm96-sha512/row/v1` today (R3).
- At served k, the row cut is required: a `Pc8RowA` of A past k = 2,560 outgrows C-Flock's 2^27-bit block
  (PROTOCOL.md), and the cut deploys row_k = 2,048.
- The cap rows (`sd`, `cap-word` per word, and so on) are interiors. Committing one cap-word row per output word in
  serving is 32 × 43,008 × 32 ≈ 44M rows per decode step (*estimate*), so they must be post-draw (R6).
- Pearl-C commits A as FP32 words, twice the bytes of the BF16 x it widens. `pc4` already commits `row-bf16/v1` and
  widens in gates. Doing the same for `pc8` halves commit volume, and moves `pc8`'s digests (PoUW's call).

**2. Which units need proofs.** These are PoUW's parameters; the service draws.
- **Law:** `work:K` over the call's tile strata: k_s = min(n_s, max(f_s, ⌈K·w_s·n_s/W⌉)).
  - K = 27,713 at ε = 0.1% and δ = 2⁻⁴⁰ (`plan.record_k`).
  - K is per window, shared as K_c = ⌈K·W_c/W⌉ per call (`plan.window_laws`).
  - y's floors are as `ncp-v2`'s.
  - Whole and short tile rows are separate strata (`check_work_strata`, the guarantee's `hone`). Decode's m = 32 is one
    short tile row and prefill's m = 8,192 whole ones.
- **Work table:**
  - w is `draw_wref`: `wrefDevRev1K` at `Prices.sm120Loop` with the cast at 8.72, over the tile's credited cells
    (`pearl_c_work.tile_weight`);
  - zero-work templates take floor 1.
- **Closure:** a drawn tile is proved with the following, each once per plan (`plan.tile_layout`, `Plan.proved_b`):
  - its TM (or r) `Pc8RowA` units, or their `rowk` pieces;
  - its TN `Pc8RowB` units in the weight's Program;
  - under the cap, its strip, word, row-digest and tally units.
- **Deterministic additions:** one tile per excluded row (`exclusion_tiles`).
- **Epoch:** the salt every ~15 min from the service's epoch coins. The audit window (the draw's receipt) need not be
  the salt epoch; see the scale requirement.

**3. The check.**
- **The Program:** `pc8`'s hiding Program `Pc8CheckHidden{M,K,N,TM,TN,DEV=sm120}`, which is `Pc8Weight` plus
  `Pc8CallHidden` (`pouw/circuit/pc8.py`; ``Shape.hidden``, ``Shape.row_k = 2048``, and ``Shape.cap`` for rev1's
  `capOK`).
- **Its templates:** `Pc8RowB{K,sm120}`, `Pc8RowA{K,sm120}`, `Pc8TileHidden{K,TM,TN,sm120}`, and under the cap
  `Pc8RowACap` through `Pc8CapTally`.
- **Partition and units:** `pc8.query(shape)` (`Q_template_instances`), with `pc8.units` and `unit_cut`.
- **Public input regions:** `pc8.DERIVATIONS` valued by the verifier's `TileAnchors.public_inputs`.
- **Acceptance:** a drawn tile is accepted when every unit's proof accepts, its rows' ok words are ok, and under the
  cap its tally's verdict word is ok.
- **What the Program still lacks** before it can be the whole check: R1, filler zero, the kept width, and voluntary and
  excluded rows' rules (`pearl_c_work.check_opened`). A cap run isn't in it either (PROTOCOL.md "Not in it yet").
- No C-Flock statement stages a PoUW unit's own gates with these rows yet. `hidden_zk` does this for `pc4` only, with
  scratch pieces on #1034 and registered lowerings on the reg branch.

**4. What PoUW does with the outcome.**
- **On accept:**
  - each accepted unit is credited (1 − ρ)·`credit_of` over its credited cells, with ρ = 1/1,000 (`Device.cap`);
  - the window's certified work is (1 − γ)(1 − ε_s)·W, with γ = 0.36949% at 8192³ per audit tile.
- **The composition chain:**
  - The service's audit gives `Pr[accept ∧ unsound W_ref > ε_s·W] ≤ δ_s`. Here δ_s is the work law's escape
    (1 − ε)^K, plus ε_ks and δ_link (`audit_window_split_of_record`, #418), plus the per-unit proof error.
  - PoUW's `Theorem1` (`Specs/Pouw/Guarantees/Game.lean`) takes any audit with such a δ_s and gives
    `Pr[accept ∧ T < (1 − γ)(1 − ε_s)·W] ≤ δ_s + η`. So the sampling half composes through `Theorem1`, not through
    `WorkWeightedSampling`, whose with-replacement tickets are not the service's law.
  - The proof half is `GγHidden` through `gammaHidden_of_sampled_all`. Its obligation `TileProofSoundAll` at ηzk is
    what `RecursiveSound` discharges: ηzk is the outer error, plus the inner error, plus the binding term.
  - `HiddenAudit`'s `Bounded` must be the service's own per-finder class, not one that reads tile goodness (the
    docstring in `Definitions/Pouw/PearlC/Hidden.lean`).
  - `RecursiveZK` adds that the auditor's view is simulable from the public inputs. That is all it adds: aborts and
    timing are outside it (the network warden's subject).
- **On reject:** the window earns no credit.
- **The lottery** (`Lottery`) is not a service outcome: it reads public digests, and the service has nothing to draw
  or verify for it.

### `ncp-v2`, briefly

`ncp-v2` is already a Program under sampled proofs (`pouw/circuit/`; vLLM `protocol_options/pouw_circuit.py`).
- **Committed:**
  - A's int7 rows, one leaf per row;
  - B's rows, registered;
  - the weight Program's Y strips and c₀, once per run and weight;
  - per call, every unit's outputs.
- **Selected:** `work:K`, with the closure of X, the strip digest, the path nodes, the key and Y, and y's floors at
  K_y = K (`plan.window_laws`).
- **The check:** `NcpLinear_v1{M,K,N,PERM}` and `NcpWeight_v1{K,N,PERM}` (`traced_as`), with the width rule's pinned
  separator Z.
- **The outcome:** a `Stratified` profile whose `harm_bound` bounds unsound work, and γ from `TTNCP_U`
  (`GammaFromTTNCP_U_v1`).
- **What the service changes:**
  - vLLM's unsalted SHA-256 leaves become `commit`;
  - `anchors.Ledger` and `plan.draw` go;
  - the replay check goes.
- Nothing in its four statements changes. Its noise is in gates, so it has no seed_A problem.

### Requirements the service doesn't meet yet

**R1. The served commitment format, and its speed.**
- **Today the formats differ.** The served kernel (`pearl-c-sm120-v1-h2`) commits `frame-b3s` BLAKE3 trees, with a
  BLAKE3-keyed tile leaf, on the GPU. The statement opens hm96-sha512 rows and the h0 TurboSHAKE leaf.
- **The volume, from the served decode's call shapes** (*estimate*):
  - The model is Llama-3.1-8B at TP 1 (`benchmarks/pouw/pearl_c_vllm/e2e.py`). It has 32 layers × 4 linears:
    qkv k 4,096 → n 6,144; o 4,096 → 4,096; gate_up 4,096 → 28,672; down 14,336 → 4,096.
  - At decode m = 32, that is 128 calls a step. A's FP32 rows are 32 × 26,624 × 4 B × 32 = **109 MB a step**, and
    55 MB as BF16.
  - The fp8-p rows add 27.8 MB, and each step has 21,504 tiles (672 a layer).
  - In all that is about 34k hm96 leaves and about 1.2M SHA-512 compressions a step.
  - At the served step (22.98 ms Pearl-C, graphed FP8 7.42 ms; served window 1, `note:20261001T0210Z-report-pouw-served`),
    commit needs **5–6 GB/s** (at Pearl-C's step) to **15–19 GB/s** (at FP8's) and **1.5–4.6M leaves/s**.
  - Prefill at m = 8,192 is 27.9 GB of A rows and 2,752,512 tiles per pass. The tile count matches the e2e note's.
- **Throughput is not the binding constraint; latency is.**
  - A GPU's SHA-512 rate is of order 10⁹–10¹⁰ compressions/s (*unverified* on sm_120), so the throughput is a few
    percent of the GPU if overlapped.
  - Latency binds wherever something waits on a root. Today forming waits on A's root in every call: -h2's A
    commitment alone is 17.9 µs a call at m = 32, k = 8,192 (panel attempt 38, `r20260930-100805-67d6`), about 2.3 ms
    a step over 128 calls.
- **The salt can't be on the GPU.** The service's trust model keeps salts off the GPUs. So `commit` splits:
  - The GPU computes the unsalted digest x (64 B a leaf, `sha512/row-seg/v1`).
  - The gateway computes b = x ⊕ M·y and the leaf. M·y and c = H(y) depend on the salt alone, so they are
    precomputable.
  - That is about 2.2 MB a step over PCIe, and about 1 µs of CPU a leaf, 35 ms of CPU a step: 1.5–5 cores per GPU at
    decode (*estimate*). Leaves batch per pass, off the critical path.
- **Recommendation:**
  - The service's `commit` takes digests from the producer and returns roots asynchronously, batched per pass.
  - PoUW removes every in-call dependency on a commitment root (question 1).
  - Compute accounting's served-zk lane's measurement settles the GPU side.

**R2. Granularity.** PoUW needs one leaf per row and one tree per call, with each call's root listed in the window's
receipt (C1: every call's commitment precedes the key). The service's `commit` must expose per-call roots, not just one
root per pass.

**R3. Registered rows are row/v1 in the service and row/v2 in PoUW.** `one_stage/registered.py` commits registered
values as `hm96-sha512/row/v1`, zero-padded to whole blocks. PoUW's role-W rows are `sha512/row/v2` by Daniel's ruling
(no row is `sha512/row/v1`; `leaves.py`). **Recommendation:** the service's registered values adopt row/v2. It's a
service format change, so it's for proofs.

**R4. Public outputs.** The statement must let a protocol declare a unit's public outputs, and the simulator in
`RecursiveZK` must take them as public inputs. PoUW has two candidates: the cap tally's verdict word (already a public
output in `cap.PORTS`), and the tile digest if the lottery stays.

**R5. Epoch coins before work: the precommitted circuit.**
- **The flow:** the prover registers W and `weights_root` (its circuit of public matmul subcircuits). The verifier
  gateway then issues the epoch's coins, the prover expands them into per-matmul noise, and this repeats about every
  15 minutes.
- **What the service needs:**
  - coins on request, bound to a registered commitment's digest (`derive(coins, "verity/pouw/salt/v1", {weights,
    workload})`);
  - recorded with arrival order, so a third party sees that the commitment preceded the coins;
  - kept separate from the per-session proof coins and from the window's draw coins.
- **The service has only per-session live coins today.** The coin record (Goldreich–Kahan) is on the lean-drives lane.

**R6. Two-stage: interiors after the draw.** At serve time, commit only A's rows, the tile digests and the records.
The prover regenerates and commits A′, ok, the `rowk` carries and the cap rows only for drawn closures. This is
`sampled_proofs`' two-stage law (replay units; its README says the driver is "not built yet"). Without it, serve-time
commit volume roughly triples at k = 4,096, and the cap is infeasible.

**R7. Per-unit work.**
- **The mismatch:** the work law needs every unit of a template credited the same work (`one_stage/draw.py` docstring).
  Pearl-C credits a tile its credited cells, which filler, excluded and voluntary rows vary.
- **The options:**
  - the service accepts a per-unit work vector, with the escape bound needing only inclusion ≥ K·w_u/W;
  - or PoUW splits each call's tiles into strata of equal credit before the law is derived.
- The Lean side is open (PROTOCOL.md "Not here yet", red team #1014).

**R8. Protocol-supplied selections.** These are units the protocol adds beside the random draw, such as exclusion tiles
and lottery winners. They are proved and recorded like drawn ones, without entering the law's escape bound.

**R9. Verifier-derived public input regions.** The service's `verify` takes the protocol's regions file (C-Flock
`verity/flock-public-inputs/v1`, from `TileAnchors.public_inputs`) computed by the verifier. It refuses a
prover-supplied one, as `hidden_zk`'s honest-chosen control does today.

**R10. Context binding.** The session record must bind PoUW's identifier v1 (scheme, salt, workload), so a proof
answers to one epoch. With live coins there is no `pub.sha`-seeded Fiat-Shamir. The binding is the record's.

**R11. Verification latency against the epoch.**
- **The measured verify costs:**
  - Outer Lean verify: 449 s for ten sessions, not like for like (#1246, at K = 4,096 and m = 35; my reading is that
    this is a BF16 coordinate statement, not a PoUW unit).
  - `hidden_zk` direct `--zk` Lean verify: 4,777 s (`Pc4RowA`) and 5,841 s (`Pc4RowB`) for one 16-instance session.
    Rust: 20 s.
- **The load per window** (*estimate*):
  - Draws: 27,713 tiles a window, nearly all on distinct calls, since a 15-minute epoch serves about 840M decode tiles.
  - Closure size: about 130 units per drawn decode tile (32 A rows × 4 `rowk` pieces + the tile), or about 290 for
    `down` at k = 14,336.
  - Weight side: almost every B row is proved once per epoch, 1.38M rows × pieces.
  - In all, about 4–9M units a window.
  - At `hidden_zk`'s CPU rate (`Pc4RowA`, 27 s per 16 instances on 32 threads, `pc4` not `pc8`), that is far beyond
    any CPU pool.
- **Recommendations:**
  - Verification need not finish inside the 15-minute epoch, only keep pace (credit settles later).
  - The draw count is per window and independent of served volume, so decouple the audit window from the coin epoch
    (for example, daily) and/or raise ε. ε = 1% gives K ≈ 2,760.
  - The service proves a window's drawn units as one session per template class, as `one_stage`'s "the drawn units are
    proved in one session".

**R12. Recursion or direct ZK.**
- **At #1246's size, direct ZK is cheaper:** `--zk` prove 1.88 s and session 3.74 s at K = 4,096 (proofs' zk-cpu-steps
  lane, `internal/proofs/state.md`), against recursion's 0.875 + 7.90 s.
- **But direct ZK's trusted gateway work grows with the statement:** 20–50 core-s per session at today's sizes (the
  architecture note). PoUW's per-window statement is millions of units, so **recursion fits PoUW and direct ZK doesn't**.
- **This holds only if sessions are large.** Outer prove and verify must be per session class, not per unit.
- **Recommendation:** PoUW asks for recursion, and the service sizes inner sessions to the block limit.

**R13. Egress and the GPU kernel.** PoUW's kernel sends only unsalted digests to the gateway and keeps the witness
local. The "GPUs reach only the gateway" premise is the deployment's; PoUW states it as an assumption of its served
claim.

## (c) What PoUW deletes, and the migration order

Approximate lines, read from `wc` on `origin/main` unless marked #1034. "Part" means a share of the file, estimated
from its symbols.

| Lines | What |
|---:|---|
| ~190 of 360 | `pouw/audit.py`: `commitment_hash` … `transcript_domain`, `Transcript`, `TileOpening`, `Prover`'s commitments and opening, `Sampled`, `Verifier`, `Audit`, `Verdict`, and `Epoch.start`'s beacon path |
| ~75 of 313 | `pouw/serving.py`: `HashFormat`, `HASH_FORMATS`, `hash_format`, `PassCommitment`, `MANIFEST_SCHEMA(S_READ)`. Schedules and gate records move to the kernel package (consolidation change 11) |
| ~30 | `pouw/schemes/pearl_c.py`: the h1/h2 keys and branches |
| ~140 of 583 | `pouw/schemes/pearl_c_work.py`: `Beacon`, `draw`, `WorkAudit`, `check_drawn`, `audit`, `audit_replay`, `_audit`. `check_opened` (~50) goes once its rules are in gates |
| ~250 of 398 | `pouw/circuit/plan.py`: the laws, sampler, plan and profile |
| ~165 of 465 | `pouw/circuit/anchors.py`: `_frame`, `Receipt`, `_fresh_source`, `Ledger`, `replay_key` |
| ~70 of 394 | `pouw/circuit/leaves.py`: `row_digest`, `commit`, `tree_leaf`, `statement_rows` |
| ~50 | `pouw/circuit/__init__.py`: `Traced.draw`, `check_openings`, `check_link` |
| ~250 of 798 | vLLM `pouw_pearl_c_device.py`: keys, trees, retain, manifest |
| ~150 of 470 | vLLM `pouw_circuit.py`: leaves and roots |
| 377 | vLLM `check/replay/pouw_circuit.py` |
| 598 | `benchmarks/pouw/pearl_c_vllm/verify_run.py` (243), `verify.sh` (22), `fast_tile.py` (333) |
| 342 | `benchmarks/pouw/pearl_c4/replay.py` |
| 935 | `benchmarks/pouw/pearl_c/hash.cuh`, `hash_h2.cuh`, `hash_sm120.cuh`; `pearl_c_sm120/h2_rows_stats.cuh`. The TurboSHAKE leaf in `hash.cuh` stays if the tile digest does |
| 2,483 | `benchmarks/pouw/pouw_hash/` (already dead per the consolidation note) |
| 1,043, plus ~100 of tests | `hidden_zk/` on #1034. Its controls survive as the service's tests |
| 502 | core `verity/primitives/crypto/beacon.py` (111) and `bls12_381.py` (391), if no protocol keeps the drand path (question 3) |
| part | core `commitments/merkle.py`'s `frame-b3` and `frame-b3s` (`experimental/.../multiproof.py` also uses them) |

**Total:** about 7.5k lines of code, 4k of them benchmarks and kernels. Tests and the h1/h2 vectors in
`pearl_c.json`/`pearl_c_vectors.py` follow, as do the -h1/-h2 Lean pins (counted in the consolidation note).

**The migration order:**

1. **served-zk's prototype (the first call).** One served request:
   - its A rows committed in the statement's format by a prototype `commit`: GPU digests salted on the host, as
     `verity_flock.rec_live` does (*not on main*);
   - one drawn tile's `pc8` closure at served k (row_k = 2,048) proved by the `hidden_zk` job on those commitments;
   - Lean's verdict.

   This proves R1 end to end, without touching vectors.
2. **The draw goes to `one_stage`.** For `pc8` calls, register a v2 record and take the receipt and the Lean draw.
   Delete `anchors.Ledger` and `plan`'s sampler, and keep the work table and closure map. Settle R7 here.
3. **The salt from the service's epoch coins.** Workload plus `weights_root` registered, then coins (R5). Retire
   `Epoch.start`'s drand path, subject to question 3.
4. **Profiles only from the service** (consolidation ruling 5). Demote `Verifier.check_tile`, `pearl_c_work.audit`,
   `verify_run` and `fast_tile` to labelled diagnostics, then delete the served-replay pipeline. This needs R1, R1-in-gates
   and the cap in `pc8` first.
5. **The kernel.**
   - Drop -h2 trees for the service's digest kernel.
   - Land the noise-seed change (question 1) with it, since it moves every Pearl-C vector, digest and pin
     (consolidation change 3).
   - BF16 A rows, if adopted, land here too.
6. **Lean.**
   - Instantiate `HiddenAudit` with the service's per-tile game.
   - Discharge `TileProofSoundAll` from `RecursiveSound`.
   - State the sampling half through `Theorem1` over the service's δ_s.
7. **`ncp-v2`'s serving commit to `commit`.** Optionally replace D_A and the key units with the service's root as an
   anchor; that moves digests.

## (d) Open questions for Daniel

1. **Where Pearl-C's per-call noise seed comes from.**
   - **The problem:** `seed_A` reads A's commitment root in the call (`unit_seed_a`). Under the service that root is
     the gateway's salted root, and the gateways can't sit in decode's per-call path. An unsalted public root leaks A
     to a dictionary attack, since seed_A is a public anchor.
   - **The options:**
     - (a) E_A from the epoch's coins and the matmul's index alone, your precommitted variant. A could then be chosen
       knowing E_A, as it already knows F and E_B.
     - (b) seed_A derived in gates from an unpublished digest of A, `ncp-v2`'s pattern. It costs gates per call, and
       E_A stops being a public input.
     - (c) The gateway in the critical path.
   - **Recommendation:** (a) if theory confirms TT_OUT's γ with A chosen after the epoch coins; otherwise (b). Not (c).
2. **The lottery on served work.**
   - **The problem:** a published tile digest is an unsalted, deterministic function of (A, B, salt). With public
     weights, it confirms a guessed prompt, so it is outside what ZK can hide.
   - **Recommendation:** served accounting uses `Sampled` only and publishes no tile digest. The lottery stays for a
     mining mode on synthetic inputs, with the published digests named outside `RecursiveZK`'s claim.
3. **The salt's source.**
   - **The tradeoff:** drand is third-party checkable. Live coins are the designated verifier's: a colluding verifier
     could pick them, as `Ledger.record`'s docstring says of today's draw. Your 4:21 PM ruling says live coins only
     for the ZK layer.
   - **Recommendation:** live coins for the salt too. Delete the beacon and BLS code unless a third-party-checkable
     mining mode is wanted.
4. **What PoUW publishes on purpose besides the verdict.**
   - **What it is:** W's per-call shapes (m is the batch size per step) and the records (real rows, excluded and
     voluntary row indices). They reveal traffic and which rows fail the per-row rules.
   - **Recommendation:** publish shapes and counts, which the work table needs, and commit row indices through the
     service, proving their rules in gates. Name the traffic side channel as the network warden's.
5. **The audit window and ε.**
   - **The problem:** K = 27,713 per window at ε = 0.1% puts millions of units a window into proving, whatever is
     served (R11).
   - **Recommendation:** decouple the audit window from the 15-minute coin epoch (for example, one window a day at
     ε = 0.1%), and set ε per deployment from the proving budget, not by default.
6. **Two-stage as the service's default for PoUW (R6).** **Recommendation:** yes. Serve-time commitment is A's rows,
   the tile digests and the records; interiors are committed after the draw. This needs the service's two-stage driver,
   which proofs has to own.
7. **Registered values' row schema (R3).** **Recommendation:** the service moves to `sha512/row/v2`, per your earlier
   ruling. For proofs to confirm, since it changes `one_stage`'s registered root.
