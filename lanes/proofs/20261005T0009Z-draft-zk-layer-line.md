---
id: proofs/20261005T0009Z-draft-zk-layer-line
campaign: verity
lane: proofs
kind: draft
status: open
repo: danielreuter/verity
origin: bc-b848b76d-faea-58b9-a5eb-32d339fbb293 (zk-layer-line, for the proofs coordinator bc-8416bc72)
---

# The ZK layer's line in C-Flock's prover

This draft draws Daniel's 4:19 PM PDT ruling (4 Oct) through C-Flock's prover code. Under that ruling only the prover's
zero-knowledge layer is trusted (soundness for the auditor, ZK for the developer), it stays in `verity/` under C-Flock's
verification protocol, and every kernel goes to a top-level `kernels/`. It was read at `origin/main` `5049de02f`. Nothing
was run and no repository file was changed. Every citation is a path under `backends/flock/` plus a function name at that
commit. The rows use the move map's format (`note:20261004T2125Z-draft-move-map-backends-integrations-tools`, section 1)
and refine its rows 1b, 1c and 1d.

The four classes:

- **ZK layer.** Code whose wrong output can leak the witness or the pads with nothing downstream to catch it, or code that
  decides what goes on the wire.
- **Kernel.** Witness kernels and the prover's arithmetic. Their wrong output either stays under the pads or makes the proof
  fail, so soundness is not at stake and completeness failures are loud.
- **Verifier.**
- **Other.** The prover's copy of the statement, tests, benchmarks and superseded forms.

The destinations proposed below:

- `verity/protocols/verification/flock/zk/`, written "ZK layer".
- `kernels/flock-cuda/`, the move map's CUDA entry.
- `kernels/flock-cpu/`, a proposed entry for the CPU witness builders and upstream's CPU arithmetic as patched.
- The move map's destinations for the rest.

## The line in short

**The ZK layer:**

- `zk_hooks.rs`, whole.
- The prover half of `zk_veil.rs`.
- The prover half of `coin_tree.rs`.
- The wire in `lib.rs`: framing, `Req`/`Resp`, transports and `LiveChallenger`.
- The host side of the device interface in `gpu.rs` (`Rounds`, `rounds_cb`, `link_cb`).
- The ZK adapter in `gpu_circuit::prove_circuit`.
- The ZK orchestration and the session driver now inside `bin/flock-circuit.rs`.
- The `zk` module and `commit_zk` that `flock-zk-b684b12.patch` adds to upstream.
- The hm96 code wherever it lives (`flock-merkle/src/hm96.rs` from the sha512 patch, `cuda/sha512.cuh`'s hm96 section).
- On the device: level 0's leaf hashing and tree, and the level-0 blind in `cuda/ligerito_zk.cuh`.

**Kernels:**

- `circuit.rs`'s witness fill, and the witness parts of `typed`, `lookup`, `ir_block`, `ir_tail` and `sha512_native`.
- `tables`/`glue`.
- The rest of `gpu_circuit.rs` and the shared FFI plumbing in `gpu.rs`.
- `prove_circuit.cuh`'s witness and fold kernels, and `prove_chunk.cuh`.
- The SHA-512 trees of levels 1 and up.
- Upstream's zerocheck, lincheck and Ligerito, and the patch hunks that thread ZK arguments through them.

**The open edge:** I recommend the leaf hashing stays and the padded encoding moves to `kernels/flock-cuda/`. The encoding
moves behind a pre-send check costing milliseconds per rep, plus a refusal of level-0 lane coins in {0, 1}. That
recommendation assumes "untrusted" means buggy kernels. If it means adversarial kernels, the line moves much further (open
question 1).

## Move-map rows

### Rust library (`live/src/`)

| Current path | Destination | Principle | Confidence | Open question |
|---|---|---|---|---|
| `zk_hooks.rs`, whole: `ProverSeed::from_os`, `ProverRng` (`from_os`, `for_table`, `f128s`), `LeafSalts` (`expand`, `next_id`, `level0_id`), `coin_nonce`, `ZeroOnDrop`, `chacha20_block`, the `STREAM_*` numbers, `Hooks`, `NoMask` (whose `rng` draws the mask slot's words) | ZK layer | coins and salts from the OS; the mask slot's words are pads | high | none |
| `zk_veil.rs`, prover half: `Layout`, `Pads::draw`, `Masking`, `Lin`, `exposed_values`, `from_exposed`, `mask_proof`, `mask_ligerito`, `ligerito_exposed`, `set_ligerito_exposed`, `Code`, `InnerCommit`, `tau_commitment`, `batch`, `query_positions`, `prove_inner`, `mask_rank_ok`, `failing`, `level0_t_pad`, `level0_queries`, `level0_bits`, `Tape`, `Logging` | ZK layer | the pads and adding them; the inner proof's padded encoding (`Code`, rate 1/8, K_PAD = 192), its hm96 commitment (`InnerCommit`) and which of its columns open (`queries`, Q = 168) | high | `prove_inner` sends τ's commitment and `Y` without checking `batch`'s `_t` (see the wire) |
| `zk_veil.rs`, shared checks: `replay`, `points_from_coins`, `ring_switch_constraint`, `point_parts`, `triple_constraints`, `ligerito_constraints`, `eq_word` | ZK layer, shared with the verifier | checks before it speaks: `zk_finish` builds from these the constraints the pads must satisfy | high | none |
| `zk_veil.rs`: `verify_inner` | verifier (beside `zk_constraints`) | verifier | high | none |
| `zk_veil.rs`: `simulate_inner`, `gk_estimate`, `gk_rewinds` | the layer's tests (the simulator behind `zkrewind` and `zkgk`) | test | high | none |
| `coin_tree.rs`: `Spec`, `Rules`, `hello_nonce`, `check`, `Checked` | ZK layer | the coin commitment at Hello: the prover checks every coin against the committed tree before using it | high | none |
| `coin_tree.rs`: `CoinTree` (`draw`, `open`, `root`), `flat_tree`, `path` | verifier | the verifier commits its coins | high | none |
| `coin_seed.rs` | verifier | M0's non-ZK seed commitment; not on the ZK path | high | none |
| `lib.rs`, the wire: `OP_*`, `push_header`, `push_padded`, `frame_domain`, `replay_round`, `framed_challenger!`, `Req`, `Resp` and their codec, `Transport`, `SharedTransport`, `TcpTransport`, `InProc`, `LiveChallenger` (`new`, `round`, `squeeze`, `open_child`) | ZK layer | it owns the wire: every byte a session sends is framed and sent here | high | `LiveChallenger::tamper` (`Tamper::Alter`, `Tamper::Defer`) is a test hook inside the send path and must stay test-only |
| `lib.rs`: `Server` (the coin server and its record), `ReplayChallenger`, `RecordingChallenger`, `unit_draw` | verifier | verifier (`unit_draw` is the verifier's draw at registration) | medium | they stay in the crate until the crate split |
| `gpu.rs`: `Rounds`, `rounds_cb`, `ProveParams::with_rounds`, `live_cb`, `link_cb` | ZK layer (the host side of the device interface) | owns the wire: a refused round gets zero coins and nothing more is sent (`rounds_cb`); the device's root reaches `Req::Commit` only through `link_cb` and the layer's hook | medium | none |
| `gpu.rs`: `device_count`, `ProveParams`, `ChunkParams`, `csc_from_rows`, `statics_for`, `sched`, `prove_params`, `run`, `decode`, `decode_with` | `kernels/flock-cuda/` | the prover's arithmetic (FFI plumbing) | high | This corrects the move map's 1c ("`gpu.rs` serves only the superseded chunk, pure and vLLM bins"): `gpu_circuit.rs` imports nine items from it (`ChunkParams`, `ProveParams`, `Rounds`, `csc_from_rows`, `decode_with`, `link_cb`, `prove_params`, `sched`, `statics_for`). |
| `gpu.rs`: `prove_chunk`, `prove_pure`, `prove_vllm`, `prove_units`, `prove_slots`, `SlotStmt`, `Reader`, `statics`, `statics_with` | `archive/flock/` | superseded (P8) | high | none |
| `chunk.rs`: `comp` (read by `gpu_circuit`), `log2ceil` (read by `circuit.rs`) | `kernels/flock-cuda/` and the statement code | the prover's arithmetic | high | the rest of `chunk.rs` is the BLAKE3 chunk form and goes to the archive once these two are cut out |
| `gpu_circuit.rs`, the ZK part of `prove_circuit`: setting `zk_on`, `zk_rep`, `zk_t_pad`, `zk_pads`, `zk_extra`, the hm96 key (from a `ZeroOnDrop` copy) and `hm96_tree`; refusing on `rounds.failed` and on rc 240; `CircuitParams`' ZK fields; `Live::Zk` | ZK layer, as a thin adapter | the pads and the hm96 commitments: this is where the layer hands its secrets to the device | medium | none |
| `gpu_circuit.rs`: `device_salts` (the `flock_cuda_hm96_salts` vector) | the layer's tests | hm96 commitments | high | none |
| `gpu_circuit.rs`, the rest: `mid_cb`, `MidCtx`, `Reuse`, `kept`, `native_plan`, `deep_unit`, `HostBuf`, `DevBuf`, `HostSlots`, `host_slots`, `device_inputs`, `UnitSched`, `schedule`, `Types`, `CircuitSrc`, the FFI declarations | `kernels/flock-cuda/` | witness kernels and the prover's arithmetic | high | `host_slots` carries the mask slot's words into the device witness (`fc_host_slots`), so a kernel writes pads (open question 4) |
| `circuit.rs`, the statement: `Circuit`, `Range`, `Kind` (with `Kind::Mask`), parsing and ranges, `leaf_scheme`, `unit`, `regions`, `region_s_hat_v`, the R1CS build, `extra_points`, `sizes_per_vu` | `verity/protocols/verification/flock/prover/` (statement code) | neither trusted for soundness (Lean's statement is the verifier's) nor a kernel; the layer reads it (`zk_layout`, `mask_words`, `region_s_hat_v`) | medium | a parse error that moves the mask slot is silent, not loud; the mask-slot readback (open question 4) covers it |
| `circuit.rs`, the witness: `witness`, `witness_with` (it fills `Kind::Mask` from the layer's closure), `slot_zab` and the fillers | `kernels/flock-cpu/` | witness kernels | medium | open question 3 (the CPU path as reference or kernel) |
| `typed.rs`, `lookup.rs`, `ir_block.rs` (`IrUnitNet`), `ir_tail.rs`, `sha512_native.rs` | split like `circuit.rs`: derivation to the statement code, witness fill to `kernels/flock-cpu/` | witness kernels; `sha512_native` computes the witness of the statement's own SHA-512 and hm96 rows, not the layer's commitments | medium | the split inside each file isn't drawn function by function here |
| `tables.rs`, `glue.rs` | `kernels/flock-cpu/` (the glue sumcheck); the union's statement goes to the statement code | the prover's arithmetic | medium | none |
| `session_verify.rs` | `benchmarks/flock/` (move map 1c) | verifier, not of record | high | none |
| `pure_block.rs`, `ir_frame.rs`, `ir_sampling.rs`, `vllm_block.rs` | as the move map's 1c | superseded | high | none |

### `bin/flock-circuit.rs` (4,223 lines), by function group

| Current path | Destination | Principle | Confidence | Open question |
|---|---|---|---|---|
| ZK orchestration: `zk_mode`, `is_zk`, `zk_layout`, `zk_queries0`, `zk_t_pad`, `zk_shape_ok`, `RANK_POINTS`, `RANK_SLACK`, `level0_zk`, `zk_identity`, `ZkRep`, `make_zkrep`, `zk_prepare`, `level0_root`, `mask_words`, `claim_word_points`, `zk_masking`, `prove_cpu_zk`, `zk_finish`, `gpu_zk_device`, `Framer`, `ByRef`, and `wit`'s mask closure | ZK layer, extracted from the bin into a library module | the pads and adding them; checks before it speaks (`zk_finish`); the padded encoding's parameters (`zk_t_pad` = 2·q0, `zk_queries0`) | high | `zk_finish` records `constraints_failing_on_pads` and sends anyway; `level0_root` panics on a device witness |
| session driver: `session_proved` (Hello and its coin check; the later tables' level-0 roots; the hook's level-0 root check, Commit and Link; the rep loop), `session_finish` (the barrier, `Req::Proof`, `Req::Finish`), `session`, `call`, `SharedCall` | ZK layer | it owns the wire: the order of sends, the refusals and the barrier | medium | the rep loop interleaves kernel calls (witness build, `prove_gpu`, `gpu_zk_device`) with the layer's sends; the sends and refusals move into the layer and the scheduling goes with them |
| statement and session setup: `params`, `domain`, `domain_of`, `identity`, `sigma`, `session_sigma`, `Table`, `Tables`, `session_tables`, `table_names`, `config`, `config_of`, `config_with`, `drawn`, `Plan` | statement code | not trusted | medium | none |
| verifier: `CircuitVerifier`, `zk_constraints`, `verify_zk_with`, `server`, `server_tables`, `serving`, `server_of`, `with_draw`, `coin_spec_of`, `check_coin_seed` | verifier, with `session_verify.rs` (`benchmarks/flock/`) | verifier | medium | `zk_constraints` is the body of a full pre-send verify if one is wanted (it costs the verifier's time; see the open edge) |
| witness and kernel calls: `Wit`, `WitData`, `witness`, `witness_uploaded`, `witness_mode`, `prebuild`, `Prebuilt`, `wit` (without its mask closure), `prove_cpu`, `prove_gpu`, `with_gpu_src`, `gpu_buckets` | the kernels' callers, with the driver | witness kernels | medium | none |
| `zkaudit` with `parse_items`, `Item`, `classify`, `INNER_CLASSES`; `zk_audit_inner_case` | the layer's tests; `parse_items` and `classify` become the send-time classifier (see the wire) | checked as it is sent (today after the fact, feature `seed-injection`) | high | none |
| other tests and diagnostics: `zkstat`, `zkrewind`, `zkgk`, `VStar`, `rewind`, `gk_simulate`, `fresh_dummy`, `simulate_full`, `session_relations`, `CASES`, `run_case`, `false_statement`, `flip_salt`, `forged_instance`, `forged_stages`, `determinism_case`, `lincheck_modes_case`, `tables_randomness_case`, `Order`, `barrier_holds`, `fix_verifier_coins`, `final_c_shift`, `Logged` | the layer's tests | test | high | the dishonest plans (`zk_pad_mismatch`, `zk_final_c_solved`, `salt_flip`, `substitute`) send what a send-time guard refuses; they need a test-only bypass |
| the other bins (`flock-pure`, `flock-pure-gpu`, `flock-link`, `flock-gpu-link`, `flock-live`, `flock-ir-block`, `flock-ir-frame`, `flock-ir-sampling`, `flock-vllm-v1`) | as the move map's 1c | superseded; none has a ZK path | high | none |

### CUDA (`cuda/*.cuh`)

| Current path | Destination | Principle | Confidence | Open question |
|---|---|---|---|---|
| `prove_circuit.cuh`: `fc_zk_lane_input` (adds `c·p[pos]` below `t_pad` and `p[pos−l]` from `l` to `l + t_pad`), `fc_zk_interleave`, and `fc_commit_l0_zk`'s `launch_ntt` calls over the w lanes and the 4 extra lanes | `kernels/flock-cuda/` under the recommendation; the ZK layer if the edge stays | the padded encoding of committed rows | medium | the open edge |
| `prove_circuit.cuh`: `fc_commit_l0_zk`'s `launch_merkle` and `merkle_cap_layer_device` on the level-0 tree; `fc_write_zk` | ZK layer | hm96 commitments; `fc_write_zk` writes level 0's ZK messages into the output | medium | the open edge |
| `prove_circuit.cuh`: `FlockCircuitParams` | `kernels/flock-cuda/`, mirrored by the layer's `CircuitParams` | the interface | high | none |
| `prove_circuit.cuh`: `fc_hm96_salts`, `flock_cuda_hm96_salts` | the layer's tests | hm96 commitments | high | none |
| `prove_circuit.cuh`: `fc_comp_scatter`, `fc_unit_witness`, `fc_sha_tape`, `fc_sha_rows`, `fc_witness`, `fc_fold`, `fc_bad_shape`, the body of `flock_cuda_prove_circuit` | `kernels/flock-cuda/` | witness kernels and the prover's arithmetic | high | none |
| `prove_circuit.cuh`: `fc_host_slots` | `kernels/flock-cuda/` | witness kernel | medium | it writes the mask slot's words (open question 4) |
| `sha512.cuh`, the hm96 section: `Hm96Key`, `chacha20_block`, `hm96_salt`, `Hm96Ctx g_hm96`, `hm96_midstates`, `hm96_finish_leaves`, `hm96_opened_salts`, `Hm96Guard`, `launch_merkle512`'s nonce rule (nonce 0 only for a tree of level-0 size) | ZK layer | salts and the hm96 commitments | high | none |
| `sha512.cuh`: the SHA-512 leaf, level and cap kernels | split by call site: on the level-0 tree, ZK layer; on levels 1 and up, `kernels/flock-cuda/` | levels 1+ hold functions of the blinded table, so a wrong leaf there reveals nothing about the witness as long as the blind is right | medium | one source serves both sides, so the split is by call, not by file |
| `ligerito_zk.cuh`: `lf_zk_blind_partial`, `lf_zk_lane_phase` | ZK layer | adding the pads (the blind `f += ρ0R0 + ρ1R1`) | medium | none |
| `ligerito_zk.cuh`: `lf_zk_ybar`, `lf_zk_rho_independent`, `lf_zk_sums_partial`, `lf_zk_observe256`, `lf_zk_open` | ZK layer, or moved to the host | ybar and ρ's independence depend on the pads and coins alone, and are cheap on the host (ybar is about 68 × 436 multiplications); e reads 2 × 2^22 words per rep | medium | whether to compute ybar and e on the host and only compare with the device |
| `prove_chunk.cuh` | `kernels/flock-cuda/` while `prove_circuit.cuh` includes it (move map 1c) | the prover's arithmetic | high | none |
| `pure_sha256.cuh` | `archive/flock/` | superseded | high | none |

### Patch scripts and patches (upstream Flock `b684b12`)

| Current path | Destination | Principle | Confidence | Open question |
|---|---|---|---|---|
| `cuda_sha512_patch.py`: edits upstream `merkle.cuh`, `merkle_open.hpp`, `merkle_open_device.cuh` and `prove_ffi.cu`; ours `prove_chunk.cuh` and `prove_circuit.cuh` (`Hm96Guard`, the salts after the path); upstream `ligerito_f256.cuh` (`open.salts = hm96_opened_salts(...)`) | split: the hm96 insertions (`Hm96Guard`, the opened salts) to the ZK layer, the SHA-512 Merkle plumbing to `kernels/flock-cuda/` | hm96 commitments | medium | none |
| `cuda_circuit_patch.py`: derives `flock_cuda_prove_circuit` from `flock_cuda_prove_chunk`'s body (`prove_chunk.cuh`), cutting in `fc_bad_shape`, `fc_witness`, `fc_fold`; adds the M1 insertions (`fc_commit_l0_zk`, the folded comb, `fc_write_zk`); edits upstream `ligerito_f256.cuh` (includes `ligerito_zk.cuh`, adds `run_ligerito_f256`'s ZK argument and five call points including `query_phase(0, …)`, and the OOD eq halves), `prove_ffi.cu` (include) and `introduce_glue.cuh` | `kernels/flock-cuda/`, with the five ZK call points as the layer's interface into the kernel | the prover's arithmetic | medium | `query_phase(0, …)` is where level 0's opened columns are chosen on the device, so "which columns open" is inside a kernel today |
| `cuda_live_patch.py`: upstream `challenger.hpp` (`FsChallenger`'s `live_cb`/`live_ctx`, which buffers absorbed bytes and hands them over at each squeeze), `pow_grind.cuh` (no search when live), `prove_ffi.cu` (`live_cb`/`live_ctx`), `tests/gpu_roundtrip.rs` | `kernels/flock-cuda/` | the device's transcript buffer; nothing in it reaches the wire except through `rounds_cb`, `replay_round`, `Masking` and `LiveChallenger` | high | none |
| `cuda_chunk_patch.py` (installs `prove_chunk.cuh` and the live hook) | `kernels/flock-cuda/` | the prover's arithmetic | high | none |
| `flock-zk-b684b12.patch`: `flock-core/src/pcs/ligerito.rs`'s new `pub mod zk` (`LABEL_OPEN`, `LABEL_CLOSE`, `EXTRA_LANES`, `Level0Zk`, `Level0ZkProof`, `Level0ZkRecord`, `Level0Params`, `rep_lanes`, `prover_config`, `rho_independent`, `lane_codeword`, `pad_codeword`, `ybar`) and `pcs/commit.rs`'s `commit_zk` | ZK layer | the padded encoding (its definition, and the CPU's level 0) | medium | none |
| same patch: `pcs/ligerito/extension.rs`, `SumcheckProver256::zk_extra_sums`, `zk_blind` and the lane phase inside `recursive_prover_with_basis_impl` (e, ρ, the blind, T', ybar between `LABEL_OPEN` and `LABEL_CLOSE`) | ZK layer | adding the pads | medium | none |
| same patch, the threading: `pcs.rs`'s `open_batch_mixed_ligerito_with_precomputed_s_hat_v_and_grinding_zk`; `ligerito.rs`'s `recursive_prover_with_basis*`, `recursive_prover_inner` and `LigeritoProof`'s `zk_level0`/`zk_record`; `lincheck.rs`'s `LincheckProof` field and `column_sumcheck_prove`; `flock-prover/src/prover.rs`'s `prove_fast_ligerito_from_witness_extra_zk` and `prove_fast_core_hooked` | `kernels/flock-cpu/` | the prover's arithmetic | medium | none |
| same patch, the verifier side: `pcs.rs`'s `verify_opening_batch_ligerito_mixed_with_grinding_zk`, `extension.rs`'s `recursive_verifier_with_basis_succinct` (`enforced_0`), `zk::enforced_extra`, `zk::verifier_config` | verifier | verifier | high | none |
| `flock-sha512-b684b12.patch`: the new `flock-merkle/src/hm96.rs` (the hm96 leaf, `salt_of`, the `begin`/`end` salt context); `flock-core`'s `ligerito.rs` (`RecursiveProof`/`FinalProof` opened salts, `recursive_prover_inner`'s salt opening) | ZK layer | hm96 commitments | medium | none |
| same patch, the rest: `flock-merkle`'s `hashing.rs` (`hash_leaves`, `hash_leaf`, `hash_pair`, `Sha256MerkleHash`), `lib.rs` (`merkle_tree`, `merkle_root`, `verify_merkle_proof*`), `merkle/{x86_64,aarch64}.rs`; `flock-hash`'s `HashKind`; `flock-prover`'s `tower/{child_walker,gates_blake3,geometry,query,real_walker}.rs`, `r1cs_hashes/{blake3,sha2}.rs`, `bin/dump_commit_vectors.rs` and five tests; `genus95_curve_code/{rng,sampling}.rs` (`FsRng`, `nonce_seed`); `flock-transcript`'s `challenger.rs`; `proof.rs`'s `bind_statement`, `union.rs`'s `publics_digest`, `element_r1cs.rs` | `kernels/flock-cpu/` (hashing, tower) and the statement code (binding, publics digest) | the prover's arithmetic | medium | the CPU's level-0 tree is built by `merkle_tree` under `commit_zk`, so on the CPU path those functions sit on the open edge |
| `flock-glue-b684b12.patch`: `prover.rs`'s `prove_union_with_binding_zerocheck`, `prove_union_with_binding_zerocheck_link`, `prove_fast_ligerito_union_circuit_linked`; `verifier.rs`'s `verify_ligerito_union`, `FlockVerifyError` | `kernels/flock-cpu/` plus the verifier | the prover's arithmetic | high | none |
| `flock-vtime-b684b12.patch` (timing in `verify_opening_batch_ligerito_mixed_with_grinding_zk` and `recursive_prover_inner`) | `benchmarks/flock/` | benchmark | high | none |
| `flock-link-b684b12.patch`, `flock-gpu-link-b684b12.patch` | `archive/flock/` (move map 1c) | superseded | high | none |

### Prover-side Python (`python/verity_flock/`)

| Current path | Destination | Principle | Confidence | Open question |
|---|---|---|---|---|
| `circuit.py`'s `stage_salts` without a key (row salts from `os.urandom`) | the committer's draw: `verity.commitments.hm96`'s `fresh_salt`, already in `verity/` | salts from the OS | medium | `stage_salts` with a key derives every row salt by SHAKE-256 of the key, the set and the row, so the salts are public; that path should be refused outside a benchmark |
| `circuit.py`'s `_commit_strings`, `statement`, `write`, `stage`; `typed_statement.py`'s `stage`; `class_statement.py`'s `stage` and `stage_tiled` (each passes `salt_key`) | statement staging (move map 1b) | not trusted; the rows and salts are the witness | high | none |
| `circuit_bench.py`'s `salt_key` and `STAGE_SALTS` | `benchmarks/flock/` | benchmark; public salts by design | high | none |
| the rest of `verity_flock` | as the move map's 1b | not on the ZK path | high | none |

## Where the layer calls a kernel

1. **CPU prove.** `prove_cpu_zk` calls upstream's `prove_fast_ligerito_from_witness_extra_zk` with
   `Masking<ByRef<LiveChallenger>>` as its challenger, or `Framer` under `FC_ZK_FRAMED`.
   - Every value the kernel absorbs passes through `Masking` through the `Challenger` trait.
   - The level-0 pads and extra lanes cross into the kernel as `Level0Zk`.
   - The VEIL pads `h` never do.
   - The kernel returns an unmasked `R1csProofLigerito` with `zk_record`.
2. **GPU prove.** `gpu_zk_device` calls `gpu_circuit::prove_circuit`, which calls `flock_cuda_prove_circuit` through the C ABI
   `CircuitParams`.
   - Into device memory go `zk_pads`, `zk_extra` and the hm96 key (a kernel parameter); the mask slot's words go in as host
     slots.
   - Back come three callbacks:
     - `rounds_cb`, whose handler runs `replay_round` into `Masking`;
     - `link_cb`, which carries the layer's hook with the level-0 cap;
     - `hm96_tree`, which returns salt-tree ids: 0 for level 0, then `LeafSalts::next_id()`.
   - `decode_with` returns the same unmasked proof and record as the CPU path.
3. **After either prove.** `zk_finish` takes the kernel's unmasked proof and record, masks them (`mask_proof`,
   `mask_ligerito`), replays its own constraints and runs `prove_inner`.
4. **Witness.** `wit`'s mask closure (the layer's draw, `ProverRng::f128s(STREAM_MASK, …)`) is called by the witness kernels:
   `Stmt::witness_with` on the CPU, `host_slots` and `fc_host_slots` on the device.
5. **Later tables' roots.** In a several-table session, `level0_root` calls upstream's `commit_zk` on the CPU for each later
   table, and that table's device reps must reproduce the root (the hook in `session_proved`).

## What in the ruling's list has no single home

- **"Checked as it is sent."** Nothing checks at send time. `zkaudit` checks one session after the fact, in a test build.
- **"Checks before it speaks."** Several sends go out unchecked:
  - `zk_finish` computes `failing` and sends anyway.
  - `prove_inner` never compares `batch`'s `_t`.
  - Nothing verifies a proof before `Req::Proof`.
  - `Masking` passes bytes, and values outside its padded windows, through unclassified.
- **"The padded encoding of committed rows."** It has three homes: `zk_veil::Code` (the inner commitment), the patch's
  `zk::lane_codeword` with `commit_zk` (the CPU's level 0), and `fc_commit_l0_zk` (the device's level 0).
- **"The hm96 commitments."** It has five homes: `flock-merkle/src/hm96.rs`, `sha512.cuh`'s hm96 section,
  `zk_veil::InnerCommit` with `tau_commitment`, the coin tree, and `verity.commitments.hm96` for the Python row commitments.
- **"Which columns open."** Level 0's and the later levels' positions are chosen inside upstream's query phase, on the CPU
  and in `ligerito_f256.cuh`'s `query_phase`. The layer neither derives them nor checks the proof's opened set against the
  coins. Only the inner proof's positions (`zk_veil::queries`) are the layer's.
- **"The pads and adding them."** This is split four ways:
  - `Masking` on the host;
  - `fc_zk_lane_input` (level-0 padding) and `lf_zk_blind_partial` (the blind) on the device;
  - the mask slot's words, which witness kernels write.
- **The orchestration.** All of it lives in the 4,223-line bin, not in a library a kernel entry could link against.

The coins and salts from the OS (`zk_hooks`) and the coin commitment at Hello (`coin_tree`'s prover half) do have homes.
But the Hello reply check (`Resp::Coins(c) if c.len() == 20`) sits in `session_proved`.

## The wire

**Where messages are written.** Every live round goes out through `LiveChallenger::round` as
`Req::Round { stream, content, n }`, where `content` is everything absorbed since the previous squeeze, framed by
`framed_challenger!` (`push_header`, `push_padded`). The other sends:

- `LiveChallenger::new` and `open_child` send `Req::Open`.
- `session_proved` sends:
  - `Req::Hello`;
  - `Req::Commit { root_f, roots, publics }` from the hook, once per session, carrying table 0's device root and every
    later table's CPU root;
  - `Req::Link` with zeros.
- `session_finish` sends each `Req::Proof` (bincode of the commitment, the masked `R1csProofLigerito` and the
  `InnerProof`) after the session's last coin, then `Req::Finish`.

On the device path, the device's `FsChallenger` never writes the wire. It hands each round to `rounds_cb`, whose handler
re-absorbs the round through `replay_round` into `Masking`, and `LiveChallenger` frames it again. So the CPU and the device
share one send point.

**Where `zkaudit` checks after the fact.** `zkaudit` (feature `seed-injection`) runs a real session and a control session
with zero pads and a zero mask slot, both against one fixed verifier coin seed. Its checks:

- It parses every round the verifier recorded (`Server::record_json`, `parse_items`).
- It attributes each item to a class by phase (`classify`: Pre, R1cs, Zc, Pads, Pcs, Rs, LigPre, L0, L0Post, Lig1, Inner).
- Masked values must differ from the control's.
- The region claims' `s_hat_v` must equal `region_s_hat_v` recomputed from the public file.
- Nothing may be unattributed or in a CLEAR class.
- It deserializes each proof and attributes its parts: level-0 rows, level-1+ rows, paths and salts, the inner proof's
  columns, τ, zero batching nonces and the parameters.

It doesn't look at `Hello`, `Open`, `Commit` or `Link`.

**What moving the check to send time touches:**

1. **A stateful classifier before `LiveChallenger::round`'s call.** Port `parse_items` and `classify`'s phase machine to run
   incrementally on each round's content, and refuse on an unattributed or CLEAR item. On the device path the refusal goes
   through `rounds_cb`, which already stops all later sends. Inside `Masking`, the classifier also checks the values
   `Masking` passes through:
   - Region `s_hat_v` against `region_s_hat_v`, which needs only the public file and the points.
   - At `L0_CLOSE`, ybar against the host's own `zk::ybar` over its pads, the lane challenges and ρ. `Masking` already
     logs those coins in `coins_l0`.
   - T' against the level-0 constraint (`ligerito_constraints` evaluated on `h`). Today that function reads the
     `Level0ZkRecord` the device returns only at the end, so it would read `Masking`'s view instead: e as absorbed before
     padding, the OOD values, and the coins.
2. **A guard on the other sends.** A `Guarded` transport wrapper beside `coin_tree::Checked` and `Logged` would check the
   shapes: Hello's nonce, Open's labels equal to the domains, Commit's 64-byte roots with no publics, Link all zero, and
   the order Hello, Commit, rounds, Proofs, Finish.
3. **Refusals in `zk_finish` and `prove_inner`.**
   - `zk_finish` refuses when `fails` is non-empty.
   - `prove_inner` refuses unless `⟨c, h⟩ = _t` before τ's commitment is absorbed.
   - Today a failing constraint leaks: the verifier computes `⟨c, Y⟩ − β·τ = ⟨c, h⟩`, so it learns the batched residual,
     a function of the kernel's wrong output.
4. **A pre-send check in `session_finish`.** Before the `Req::Proof` loop, run `zkaudit`'s proof attribution as a structural
   check, plus the cheap check under the open edge.
5. **A test-only bypass.** The dishonest plans need one under `seed-injection`.

What can't move: the comparison against a zero-pad control needs a second session, so it stays a test.

## The open edge: the padded encoding and the leaf hashing

**Sizes at m = 35.** This is the top size; both K values run there (`MAX_STATEMENT_BITS` = 2^35).

- Level 0 has 2^6 witness lanes plus 4 uniform extra lanes, so 68 lanes.
- Each lane is a message of L = 2^22 F128 values, encoded at rate 1/2 (codeword length 2^23).
- q0 = 218 opened rows per rep. Both reps open the one level-0 codeword, so t_pad = 2·q0 = 436.
- There are 2^23 leaves, each a 1,088-byte row under a 192-byte salt.

The measured costs are per statement, from the dense rollup `art:c343ae88d618f9b5ffc8699951fb2a7bf0e36f151a450a671305c88c7bee1996`:

| Size | Run | Units per statement | Prove (s) | Session (s) | Verify (s) |
|---|---|---|---|---|---|
| K=4096 | r20261002-062836-96bb | 2,048 | 1.063 | 3.05 | 5.72 |
| K=14,336 | r20261002-122853-c740 | 512 | 1.071 | 4.85 | 11.75 |

For the K=4096 run, the device's `t.encoding_commitment` is 0.134 s per rep and proofs are 1,179,202 bytes per rep
(`art:6154fc6d5aeb0576f2daca4ceff260708d54309d7ae452dd6e2bbe3a4f629e5e`).

**(a) How a wrong output leaks.**

- *The encoding.* If the padding is missing, has the wrong c, is offset wrongly or is reused across lanes, the opened level-0
  rows (2·q0 positions, 68 values each) become evaluations of the bare witness lanes. Omitting c alone leaks half the
  positions, because X_L vanishes on half of them and X_L + c on none.
- *The hashing.* A missing or wrong salt (the wrong ChaCha20 counter or tree nonce, zero salts), a raw row in place of a
  digest, or stale device memory makes the unopened leaves deterministic functions of their rows. A verifier who can guess
  a row can then test the guess against a sibling in an opened path or against the root. The root goes out at Commit,
  before anything opens.
- *Levels 1 and up.* Their trees hold functions of the blinded table, so their hashing doesn't matter for ZK. The blind
  does: without it, the level-1 sumcheck rounds go out live, before any pre-send check, and leak the folded witness.
- *Device memory.* The pads, the extra lanes and the hm96 key sit in device global memory. Any kernel in the process can
  read them; that only matters if kernels are adversarial.

**(b) Can the prover check before opening?** Yes for the openings, no for the root. The root leaves at Commit, mid-proof,
through `link_cb`. The openings leave at `Req::Proof`, after the session's last coin, so everything opened can be checked
in between. The cheap check:

- Derive level 0's positions from the coins, as the verifier does, and compare them with the opened set. This covers
  "which columns open".
- Recompute each opened salt on the host (`hm96_opened_salts`, from the key and tree nonce 0), each opened leaf from its
  row and salt (`flock_merkle::hm96::leaf`), and each path up to the root already sent.
- Recompute ybar from the layer's own pads.
- Check each opened row's fold against the next level plus `pad_codeword(ybar)` at that position (`zk::enforced_extra`),
  evaluating `pad_codeword` at the q0 positions only, not by a full transform.
- Recompute e from the layer's own extra lanes, then check T' and the inner constraint.

Recomputing e matters: a kernel that computes e wrong but consistently (for example over zero lanes) satisfies the T'
constraint and still leaks the claim through T'. Recomputing each opened column from scratch, as the ruling suggests,
costs more than this: one column needs 68 evaluations of a degree-2^22 polynomial, about 6e10 multiplications per rep,
which is more than re-encoding everything.

**(c) Cost.**

- *The cheap check.* Per rep at m = 35:
  - 436 leaves of 1,088 bytes;
  - about 5,000 node hashes (218 paths of 23 nodes);
  - on the order of 1e6 F128 multiplications for `pad_codeword` at 218 points and the folds;
  - e at 2 × 2^22 words.

  That's an estimate of a few milliseconds plus tens of milliseconds for e, against 1.06 s of prove per statement. It
  needs measuring.
- *The full recompute.* This is the only check that covers the root:
  - 68 NTTs of size 2^23, about 6.6e9 F128 multiplications;
  - SHA-512 over 9.1 GB of rows;
  - 2^23 salt expansions (1.6 GB of ChaCha20) with their hm96 finishes, about 1.3e10 64-bit XORs for the keyed matrix;
  - 2^23 node hashes.

  I estimate that from operation counts at 20 to 50 core-seconds per statement (the reps share one level-0 tree),
  unmeasured. It sits on the critical path before Commit, because the coins need the root. It also needs a 4.6 GB host
  copy of the witness: today `level0_root` panics on a device witness.
- *What exists already.* A several-table session does this recompute for every table after the first. Table 0's device
  root is checked only against rep 1's, which runs the same kernel on the same inputs.
- *Small sizes.* At m = 25 to 27, level 0 is 68 lanes of 2^12 to 2^14 values, and the full recompute is milliseconds.

**(d) Does the check cover everything?**

- *Unopened positions.* The encoding there never leaves the prover except inside salted leaves. So once the hashing is
  right, an encoding error there reveals nothing.
- *Opened positions.* There the fold check ties every lane's padding to the layer's own pads. A lane's error δ_i(q) shows
  up as Σ r_i δ_i(q) with r = `build_eq_table256(&lane_challenges)` (in `recursive_prover_with_basis_impl`). So a lane is
  covered only if its coefficient is nonzero. The coins are the verifier's, and a malicious verifier can zero a
  coefficient by choosing a lane challenge in {0, 1}. The layer has to refuse those coins, as it refuses r_j = 1 at the
  zerocheck. With that refusal, an error that involves the secret pads is caught except with negligible probability over
  them.
- *The extra lanes.* Each rep's fold excludes the other rep's extra pair, so each pair is covered only by its own rep's
  check.
- *What it misses:*
  - the root's hiding;
  - the unopened leaves, and every sibling digest in a path, since a path only has to hash up;
  - the cap layer;
  - colluding encode and fold kernels that keep the opened relation consistent, which I haven't settled.
- *A spot check of the hashing.* Read back s unopened rows chosen by the layer's own randomness, rehash them with their
  salts and paths at the link hook before Commit. That costs tens of milliseconds at s = 1,000 and catches a hashing bug
  that touches a fraction f of leaves with probability 1 − (1 − f)^s. It's a guard on the layer's own CUDA, not grounds to
  move it.

**Recommendation (the coordinator decides):**

- *The leaf hashing stays in the ZK layer.* That covers:
  - level 0's salt expansion (`hm96_salt`), leaf finishing (`hm96_finish_leaves`), tree and cap (`launch_merkle512`,
    `sha512_merkle_level`, `merkle_cap_layer_device` as called on the level-0 tree);
  - the CPU equivalents (`flock-merkle/src/hm96.rs`, and `merkle_tree` as `commit_zk` calls it);
  - the blind (`lf_zk_blind_partial`, `zk_blind`).

  No check short of the full recompute covers the root and the unopened leaves, and that costs about 20 to 50 core-seconds
  per statement on the critical path, against 1.06 s of prove.
- *The padded encoding moves to `kernels/flock-cuda/`* (`fc_zk_lane_input`, `fc_zk_interleave`, and `launch_ntt` as
  `fc_commit_l0_zk` calls it). Three conditions: the cheap pre-send check lands, the layer refuses level-0 lane coins in
  {0, 1}, and "untrusted" means buggy kernels.
- *Optional.* Enable the full recompute below a size threshold (m ≤ 27), where it costs milliseconds. Add the spot check
  either way.

## Open questions

1. **Buggy or adversarial kernels?** "Their wrong outputs stay hidden under the pads" holds for padded values against both.
   Against an adversarial kernel, every unpadded message is a channel, and so is every root the layer can't predict
   (level 0's, the later levels', the level-1 sumcheck rounds). Closing those needs a live run of the verifier's own round
   checks and a recompute of every root, which is roughly the verifier plus the commitments.
2. **The move map's 1c is wrong about `gpu.rs`.** `gpu_circuit.rs` imports nine items from `gpu.rs` and uses `chunk::comp`,
   and `circuit.rs` uses `chunk::log2ceil`. The superseded forms can't take `gpu.rs` or `chunk.rs` to the archive whole.
3. **The CPU prover: reference or kernel?** The move map's answered row puts the Rust CPU prover in `verity/` as the
   reference the GPU must match byte for byte (`gpu_proofs_match_cpu`). The ruling puts its arithmetic and witness fill in
   `kernels/`. I propose `kernels/flock-cpu/`, with the byte-for-byte test kept between the two kernel entries.
4. **The mask slot.** Witness kernels write the slot (`Stmt::witness_with`, `fc_host_slots`). If one zeroes or overwrites
   it, the claims' `s_hat_v` go out unmasked and the verifier still accepts. A readback of the slot's words, compared with
   the drawn words before the opening's label (`Masking::at_open`), is cheap and belongs in the layer.
5. **Device witnesses.** A several-table GPU session with device witnesses panics in `level0_root`, so the existing
   cross-check is CPU-only.
6. **Measure the cheap check** at K=4096 and K=14,336 before relying on the estimates here.
7. **Extract the ZK orchestration** and the session driver from `bin/flock-circuit.rs` into a library module. That's the
   first PR, since no line can be enforced while the layer lives in a bin.
8. **CUDA in `verity/`.** Any CUDA the layer keeps (the level-0 hashing, the blind) is an exception to "every kernel lives
   outside `verity/`". The ruling should name it, or the layer's CUDA should be an entry of its own that `verity/` vendors
   by hash.
