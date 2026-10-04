---
id: proofs/20261004T2240Z-handoff-move-map-answers
campaign: flock
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4 (proofs), answering top's move maps (thread 1791150333.889129, reply 1791152743.071189)
---

# proofs' answers to the move maps (4 Oct, 3:40 PM PDT)

These answer `note:20261004T2125Z-draft-move-map-core` questions 3, 4, 7 and 9 and
`note:20261004T2125Z-draft-move-map-backends-integrations-tools` §7 proofs 1–6, with corrections to proofs' rows. Facts are
from origin/main at `9400e83d5` (#1129 and ci's 12-PR tip landed) and from `cursor/verifier-fail-closed-95d4` at
`12e5bfa4e`. I take top's five defaults; nothing here objects to them.

## Two corrections that change the maps' premises

- **The Lean verifier has no parsers for the legacy forms.** `pure_block`, `chunk`, `ir_frame`, `ir_sampling` and
  `vllm_block` are refused by statement id before anything parses: `Tags.find?` knows only the netlist and
  `verity/flock-circuit…` tags (`Main.lean:320–321`, `Flock/Tags.lean:304–308`). The superseded forms the verifier still
  parses are PR #83's four (`verity/flock-netlist/v1`, `verity/flock-circuit@19c7269a`, `@fd02e847`, `@631567f7`). **On
  main they still accept,** with no claim over them. The fail-closed branch's `ProvedScope.statementRules` refuses them by
  their tag fields (not hm96-sha512 rows, or not `hm96-sha512/v1` leaves) before any parser runs. So "the parsers of the
  superseded forms leave the verifier" is a small Lean job, and it waits on fail-closed landing; without that refusal it
  would itself be a change of what the verifier accepts.
- **`proofs.programs`' five tests regenerate SP1 guest digests,** not catalog digests. `programs.py` builds
  `typed_obligation` subcircuits, and the digests it checks are `target.py`'s gate-set and family manifests, which only
  the SP1 guest reads. The live readers of `target` (`bench/contract.py`, `bench/drilldown.py`, `tools/tc_probe/trust.py`,
  `instances_hw.py`) read names, models and domains, never those digests.

## Core map

**3. `ml.library`: verifier or public parameter?** Split it, as recommended: the mechanism goes to `verity/` and the list
of tables to the catalog. The list is a public parameter: which MUFU tables count as hardware semantics (`library`,
public in both tracks), by SHA-512, with index and value bits. Its assumption is the device's measured table (the
`ml/tables/` captures that go to `catalog/hardware/sm89/mufu/`). The mechanism is `Table`, `LABELS`, `table_label`,
`definition_label`, `spec` and `digest`. Only the typed statement reads either part: in Python `circuit_types`,
`layouts`, `typed_statement`, `type_trace`, `derive`, `ir_lower`'s `is_library` and `boolean_export`; in Lean
`Flock/Library.lean`, imported only by `CircuitType`, `Layout` and `Typed`. Fail-closed refuses typed statements, so the
list is off the accept path. Lean can't read the catalog's JSON at compile time, so `Flock/Library.lean`'s
`LIBRARY_TABLES` becomes a file generated from the catalog entry, with a no-diff test. That is lean's pattern for
`Vectors.lean`, and `test_table_library.py` already does the comparison. No move PR waits on this.

**4. Commitments.**
- *The one framing* is the one the verifier of record accepts, and the only one a guarantee reads:
  - the `frame-v3-sha512` tree over verifier-derived domains (`merkle` plus `frame_v3`);
  - `hm96-sha512/v1` hiding leaves (`hm96`);
  - over the SHA-512 row digests `sha512/row/v1`, `sha512/row/v2` and `sha512/row-seg/v1` (`rowleaf`).

  This is C-Flock's `SCHEME = "frame-v3-sha512/hm96-sha512"` (`circuit.py:68`), and fail-closed's rules refuse any other
  leaf.
- *Superseded entries, kept so old records replay:* `frame-v3` over SHA-256, `sha256/row/v1`, `blake3-keyed/row/v2`,
  `hm96-sha256/v1`, the NVFP4 row schemas and `poseidon2-babybear-w24/row/v2h`. They stay in the same modules for now,
  marked superseded. Splitting them out is step-5 consolidation, not a move.
- *`vllm_v1` and `leaves` stay current in `verity/`.* They are what vLLM's serving Commit emits, `hm96` wraps a `VllmV1`
  base, and vLLM's `protocol_options/sampled_proofs.py` uses them. Moving serving onto the one framing is circuits' and my step-5 job
  (add, bridge, supersede), and nothing in the moves waits on it.
- *`multiproof`* goes to `experimental/commitments/`. It is a generic algorithm that still runs and may serve batched
  Merkle openings, and it costs nothing to keep. Its two archive-bound `proofs` importers (`statement`, `transparent`) go
  to `archive/sp1`.
- *`poseidon2_babybear`* goes to `archive/direct` with B-Ligero, together with `rowleaf`'s `v2h` schema, which is split
  out first. No live approach uses a field-native hash.
- *`blake3` and `turboshake`* go to `verity/primitives/crypto/`. They are hashes: the Pearl-C schemes' BLAKE3 and
  TurboSHAKE128 (PoUW and `benchmarks/pouw`), plus `rowleaf`'s superseded BLAKE3 row. Neither is a commitment scheme.
- *The vectors generators* become generating tests, as the map says. The JSON stays beside each reference.

**7. Four smaller calls.**
- *`ml.tc.relation`, revised 4:40 PM PDT under Daniel's 4:25 PM PDT silicon ruling:* `relation.py` and its Lean twin
  `Protocol.TC.Relation` go to `catalog/silicon/` with the tensor-core step's model, not to `experimental/`. No
  guarantee that a computation was verified reads a model, so the 18 `Guarantees.TC` step pins leave core's lock and
  become lemmas in `catalog/silicon/`'s Lean, with their names kept. That is core's lock reduction (mine), and the DM to
  Daniel at landing names them. The superseded text follows.
- *`ml.tc.relation` (superseded):* moves with its Lean twin `Protocol.TC.Relation`, and core's lock reduction (mine, after #1053 and
  lean's reads check) decides where both go. No file in the repo outside core's Lean package, and no campaign note, names
  the 18 `Guarantees.TC` step pins. No claim id names the relation, and its only Python users are core's tests and
  numerical's archive-bound red team (`redteam/campaign.py`, `forge.py`, `z3_relation.py`). Unless the docs site cites
  them, the reduction proposes them as lemmas. Then `relation.py` goes to `experimental/`, and the Lean goes to
  `security_proofs/core` with its names kept. Either way it is not a cost model: `census()` only counts predicates.
  Until the reduction's DM is answered, it stays where it is.
- *`proofs.codes`:* no. Live code uses 12 codes: `ACCEPTED`, `EXPECTATION_MISMATCH`, `INVALID_COMMITMENT`,
  `INVALID_OPENING`, `INVALID_VALUE`, `PUBLIC_IO_MISMATCH`, `CHECK_MISMATCH`, `CHALLENGE_MISMATCH`,
  `COVERAGE_MISMATCH`, `RELATION_REJECTED`, `INVALID_COMPILED_RESULT` and `MALFORMED_TRANSCRIPT`, all from vLLM's
  `check/` (`commit_rules`, `gates`, `result`). Those 12 stay with unchanged values; the rest go to `archive/sp1` with the
  `proof-format-v3` decoder. Where the 12 go follows circuits' Q3: if the Commit verdict is a verifier role, they go to
  `verity/codes`, and otherwise into `integrations/vllm`. C-Flock, sampled proofs and PoUW import none of them.
- *`proofs.programs`' target tests:* yes, they go to `archive/sp1` with `programs.py`, for the reason in the second
  correction. `target.py` goes to `catalog/targets/` with its recorded digests as data, and `families`' name constants
  move into it first.
- *`claims`:* it stays in `verity/claims`. Claim ids are vocabulary that results and code cite, not parameters a verifier
  chooses, and they enter no digest. PoUS imports them at runtime, and the docs site imports them.
- *`proofs.profile`* (a row, not a numbered question): it goes in a shared `verity/protocols/profile`, not under
  `verification/`. It records what any verifier established, and PoUW reads it as well as sampled proofs.

**9. The unread spec modules (with lean).** I agree with lean (1791152851.872809), as owner of core's lock:
- *`Protocol.Boolean`, `Fp32`, `Prims` and `Scalar`* leave the spec for `security_proofs/core`, unlocked, with
  `Verity.Protocol.*` names kept. That includes `Protocol.Boolean`, which the map recommended keeping. It comes back
  through promotion when a lowering guarantee reads it.
- *The four `Vectors.lean` files:* their data goes to the catalog, and each becomes a generated Lean file in
  `security_proofs/core` with a regenerate-no-diff test. `test_lean_vectors.py`, `test_lean_fp32_vectors.py`,
  `test_lean_scalar_vectors.py` and the verity suite's declared inputs name these paths, so they change in the same
  commit.

## Backends map, §7 proofs

**1. Superseded-form parsers in `Flock/`.**
- *Which modules:* once fail-closed lands, only the four PR #83 tags (first correction) reach this code:
  - `Blake3Row` (whole) and `RowLeaf`;
  - `Stmt.setup`'s non-hm96 branch, with its use of `Circuit.parse`;
  - `Comp`'s BLAKE3 compression-circuit load (`D_b3`);
  - `Public`'s SHA-256 frame-v3 roots;
  - those four `Tags` records.

  No `soundness/` or `level3/` module imports `Blake3Row`. The lock's `reads` name `Flock.Comp`, `Circuit`, `Public` and
  `RowLeaf`, so those four split rather than leave whole. The flock-lock reduction (864 entries to about 9) shrinks
  `reads` first, so the split comes after it.
- *Does the refusal stay?* Yes, as a name-to-reason list in the verifier: the `refused: <form>` text that #1147's
  `replay_expect` matches, with the `Tags` records removed. Each parser goes as a frozen copy to
  `security_proofs/flock/superseded/`, unlocked, as Daniel's 1:13 PM ruling says.
- *Not superseded:* the typed statement (`verity/flock-circuit/types`, PROTOCOL §16.11) is unfinished. It stays in the
  verifier behind `ProvedScope`'s "a typed statement" refusal (P9), with `CircuitType`, `Layout`, `Typed`, `Derive*` and
  `Library`. The hm96 tags (`@eb90718f`, `@e51e2b86`, `@967b8d06`) pass the statement rules, so they aren't parser
  candidates.
- *Row corrections in 1a:*
  - `FlockRows` (`flock-rows`) is a test exe. It emits netlists from types JSON, and `test_flock_rows*.py` compares that
    against Python's `derive_vectors.json`. No guarantee depends on it, and it stays in the verifier's package, since it
    builds from the verifier's modules.
  - On `FlockProofs` (lean's Q1, mine too): it joins `security_proofs/flock/`. 18 of the verifier's 25 pins are proved
    there, and the other 7 proofs, now in `Flock/*.lean`, move there in the lock reduction. The verifier package stays
    dependency-free either way.

**2. The reference prover.**
- *Yes:* the reference prover is the Python statement staging (`circuit.py`, `typed_statement.py`, `ir_lower.py` and
  `class_statement.py`) together with the Rust CPU `flock-circuit`. `check_build.sh` checks and tests the CPU features
  (`sha512`, `glue`, `seed-injection`) and never `gpu`. The GPU must match the CPU byte for byte
  (`gpu_proofs_match_cpu`, `flock-circuit.rs:3761`). `benchmarks/one_stage` proves on CPU, and the recorded class and
  circuit pods use the GPU.
- *The `gpu` feature is the `flock-cuda` entry,* minus `gpu.rs`: `gpu.rs` serves only the superseded chunk, pure and vLLM
  bins, so it leaves with them. The entry's build key is the crate's source hash, `--features gpu`, `b684b12` and the
  toolkit. It stays a feature for now. `gpu_circuit` becomes its own crate only after the superseded modules leave
  `lib.rs` and `prove_circuit.cuh` stops being included after `prove_chunk.cuh`.
- *Coins:* `coin_seed.rs` reimplements `verity.randomness.derive`, pinned by the `matches_verity_randomness` KAT, which
  P5 accepts. The ZK path draws OS coins (`coin_tree.rs`).

**3. `session_verify.rs`** is a benchmark: not TCB, and not on the assurance list. The verifier of record is Lean's
`flock-verify`. The one-stage audit records both verdicts and takes Lean's (`a0.py`), and no record or table reads
`serve`'s accept as of record. Upstream's Rust verifier is already on the assurance list through lean-agreement, and this
is a call-for-call timed copy of it (`verify_ligerito_extra`), so it adds no assurance. It goes to `benchmarks/flock/` as a
`flock-serve` bin. Until that split, it stays in the prover crate, with one line in its doc saying it is not the verifier
of record.

**4. Superseded statements, form by form.** None is built by `check` (`check_build.sh` checks only `flock-circuit`), and
Lean has no parser for any of them. Their numbers are in the store, so their replays re-verify at their own commits and
expect "refused: <form>" at main.
- *To `archive/flock/`,* each with its record and last-good commit:
  - the pure and chunk forms: `pure_block`, `chunk` and `gpu.rs`, the bins `flock-pure`, `flock-pure-gpu`,
    `flock-link`, `flock-gpu-link` and `flock-live`, `verity_unit.rs`, `pure_sha256.cuh` and the chunk and link
    patches;
  - the vLLM block: `vllm_block` and `flock-vllm-v1`;
  - pods `10`–`31` and `40`, and `50-preflight.sh`, which builds `flock-vllm-v1` and has no callers;
  - Python `unit.py`, `gf2.py`, `export_unit.py`, `instances.py`, `backend.py`, `negatives.py` and `bench.py`'s pure path;
  - `arch_proto/` (it is at `backends/flock/arch_proto/`, not under `pod/`), which nothing references.
- *To `experimental/flock/`:*
  - the frame-v3 IR forms: `ir_frame.rs`, `ir_sampling.rs`, `flock-ir-frame`, `flock-ir-sampling` and pods `33`/`34`;
  - Python `ir_frame.stage`, `ir_sampling.py` and `ir_bench.py`;
  - the six template `frame_lowering`s.

  They teach the attention, RoPE, RMSNorm, SiLU and Gumbel lowerings that M0 hasn't ported (only `gemm_coordinate` has a
  `circuit_lowering`).
- *What stays with the prover:* `ir_block.rs` and `ir_tail.rs` (the circuit, typed and lookup paths share them), and
  `ir_frame`'s `BINDING_TAG` and `OWNER`. Frame-v3 is superseded for new statements, since M0 reuses only those two
  constants for its domains.
- *Ordering constraints:* `prove_chunk.cuh` stays with the kernel entry while `prove_circuit.cuh` includes it, and only
  the chunk bins leave. The first PR is the crate split: `lib.rs` declares every module, so each form gets a feature or
  leaves the module list before any file moves. `tool.py`'s `flock_pure` (pod `20-pure.sh`) and `tools_registry` change
  in the same PR.
- *Row corrections in 1b:*
  - `ir_sampling` is not current. Its only routes are the Gumbel template's `frame_lowering` and the `flock-ir-sampling`
    bin, and Lean refuses that statement id.
  - `partition_units._program` is only a CLI default (`partition_units.main` and `class_statement`'s CLI), so it goes
    to `benchmarks/flock/` with the CLIs, and the prover takes its Program from the caller.
  - `key_class_sets` is an orphan CLI and goes to `benchmarks/flock/`. `lean_rows` generates the Lean RoPE data and
    belongs with its pin test.
  - `unit_fp4_check` follows `lowering` (top's default 4: catalog), or goes to experimental if compute-accounting's Q6
    makes NVFP4 experimental.
  - Per-Definition lowerings (`topp_word`, `gemm_coordinate`'s `circuit_lowering`) follow default 4 to the catalog.
    `gemm_coordinate`'s lazy `instances.write_set` import is cut first.

**5. Agreement scripts and vectors.**
- *Scripts:* yes, `agree.py`, `ci.py`, the `*_agree.py` scripts, `fuzz.py`, `transcript_check.py`, `zk_mutants.py`,
  `selftest_records.py`, `redigest.py`, `upstream.json`, `upstream-build.sh` and the `circuit-vectors*` and
  `netlist-vectors` patches move to `tools/lean_agreement/`. They are the assurance list's lean-agreement item, and they
  import `verity` and `research`, never the reverse. It is a pure move that updates `research.store.kinds`' paths and
  ci.toml's step in the same PR (ci's terms). It counts as a `backends/flock/` change, so it needs a `check --record` with
  lean-agreement.
- *Vectors:* `vectors.json` and `lookup_v2_vectors.json` stay beside the verifier in `verity/`, not in `catalog/vectors/`.
  A vectors file is the spec where two implementations agree. `lookup_v2_vectors.json` is written from Lean and read by
  Rust (`lookup.rs:355`) and Python (`test_derive.py`). The verifier's tests cite `vectors.json`'s set ids, and
  `check.py`'s lean-agreement reads it. A catalog entry is a parameter with an assumption, and these are neither.

**6. numerical's `security/` and `checker/`:** yes, they go to `archive/numerical/` with the frozen backends.
- `frozen.py` imports only `functools` and `Path`, and fetches the frozen ledger from the store. Neither `tables.py` nor
  `store_tables.py` imports `security/` or `checker/`, so the frozen rows render only from the store.
- Their other importers are all archive-bound: A-GKR, B-Ligero, VOLE, `gkr_export`, `anchor_a100`'s report, and
  numerical's own `explore/` and `redteam/`.
- Also archive: `backends/redteam/` (it attacks A-GKR and B-Ligero only, and `check` runs none of it) and
  `backends/shared/anchor_a100` (only its own report reads it, through `frozen.path`). `backends/README.md` and
  `AGENTS.md` become `archive/README.md`, as the map says.
