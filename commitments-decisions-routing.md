---
cursor:
  subagentId: "bc-b7065976-4200-586f-b4d2-5b115641d07f"
---

# Code-side routing for the Sep 27 commitments and circuits decisions

The Project docs were updated on Sep 27 for the approved §8 of [commitments and circuits](../docs/commitments-and-circuits.md), the related rulings in [project context](../docs/project-context.md), and the adopted [circuit terminology](../docs/circuit-terminology.md). The repo was not touched. This list says where each decision lands in code, and who likely owns it. Paths are on `main` at `b1aa9bdb` unless a PR is named.

Owners: **M0 prover** (ZK-Flock M0, [PR #83](https://github.com/danielreuter/verity/pull/83)), **Lean verifier** (lane A7, [PR #85](https://github.com/danielreuter/verity/pull/85), including the coin server), **vLLM** (the vLLM coordinator's lanes), **partition checker** (the core checker, `validate_unit_cut` and its successors), plus **core** (research coordinator) and **private recursion** ([PR #97](https://github.com/danielreuter/verity/pull/97)) where neither fits.

## Part 1. Decisions to implement

### 1. Roots bind the partition digest (§8 questions 2 and 3)

- **Define the partition digest.** There is no partition digest in code yet. It needs a canonical description of a program's partition, whose content digest names the program digest; per-body tilings (`query_ast.Tiling`) are already a compact form. Area: `packages/verity/src/verity/ir/partition.py` (`validate_partition`, `validate_unit_cut`), `ir/query_ast.py`. Owner: **partition checker**.
- **Bind it in roots, not the query id.** `commitments/vllm_v1/__init__.py`: `semantic_root` (around line 272) and `SemanticDomain` (around line 376) put `query_id` into the semantic root's preimage, and `vllm_v1/PROTOCOL.md` §4–5 specifies that. The scheme for new work binds the program, partition and scheme digests and the leaf count. Recorded `vllm-v1` roots stay as they are until the re-baseline, which is on hold. Owner: **vLLM**, with **core** for the reference, spec and vectors.
- **The integration's producers** pass the query id into the semantic root: `integrations/vllm/verity_vllm/commit/scheme.py` (its `semantic_root` wrapper, around line 128), `query/query_artifact.py` (the query document's `query_id` and `binding_id`) and `pipeline/program_graph.py`. After the switch they pass the partition digest and record the query (or cut policy and its parameters) as provenance in the run record. Owner: **vLLM**.
- **Levels.** `verity.ir.partition.Level.query` (around line 960) names each level by a query id. It should carry the partition digest of its family, and `verity.proofs.profile` levels follow. Owner: **partition checker**.
- **The M0 statement.** `verity/flock-circuit` (`backends/flock/python/verity_flock/circuit.py` on PR #83) binds frame-v3 roots and domains. Per the architecture's statement (§1.5), it should also carry the program digest, the partition digest and unit indices into the partition. Owner: **M0 prover**.

### 2. The Lean verifier checks the partition invariant itself (question 5)

- **Add the check** to the Lean verifier on PR #85 (`backends/flock/verifier/lean/Flock/Statement.lean`, `Flock/Verify.lean`, `Main.lean`; spec in `backends/flock/verifier/PROTOCOL.md`). It runs over the verifier's own copy of the program and partition: each gate in exactly one unit, the committed set equal to the boundary set, the units' gates summing to the circuit's, and the width rule. The verifier also checks that claimed units belong to the partition, and it derives leaf positions from the partition.
- **Conformance** against the Python references: `verity.ir.partition.validate_unit_cut` and `validate_partition`, `verity.ir.boundary` (about a thousand lines), and the cross-call check on [PR #98](https://github.com/danielreuter/verity/pull/98).
- **Owner:** **Lean verifier**, with the spec from **partition checker**. The same specification later serves the private track's Φ as a circuit (**private recursion**).

### 3. The verifier draws sampled units directly from its own randomness

The unit draw is derived today in two places, both through SHA-256:
- **Sampled proofs.** `protocols/sampled_proofs/verity_sampled_proofs/law.py`: `ru_key` and `vu_key` call `_key`, which calls `derive(round_, domain, bindings)` on a beacon round. Then `select_replay_units` and `select_verification_units` sample from that key's SHA-256 counter-mode streams (`Key.bernoulli`, `Key.subset`). The module docstring, the package docstring (`__init__.py`: "draw replay units from a beacon") and `tests/test_law.py` ("beacon-keyed draws") say the same. The law (Bernoulli $p$, exactly $k$) stays; the randomness becomes the verifier's own, recorded in the session record.
- **vLLM.** `integrations/vllm/verity_vllm/commit/challenge.py`: `replay_key` (`derive` from a source and the run root, then `vu_key`), `stratum_picks`, and the legacy seeds `legacy_replay_seed`, `challenge_seed` and `root_seed` (SHA-256 of the challenge and run root), all behind `LEGACY = True`; also `check/replay/sample.py`. Legacy draws must stay byte-identical for recorded verdicts; new draws come from the verifier.
- **Where the draw should come from.** The verifier's coin server in flock-live (`backends/flock/live/src/lib.rs`, "Verifier side: coin server", around line 610; `flock-live serve`) already draws coins from the operating system. The unit draw belongs beside them, recorded in the session record and checked offline by the Lean verifier like any coin. Open for the owner: whether the draw falls under the session's up-front coin commitment or is issued after registration and before the session's statements are fixed.
- **Docstring.** `packages/verity/src/verity/randomness/__init__.py` says every challenge draws through `derive`. It should note that the unit draw doesn't.
- **Owners:** **Lean verifier** (coin server and the offline check), **vLLM** (`challenge.py`), and **core** (the sampled-proofs protocol code and the docstring).

### 4. Objects by content (public track) and by c (private track)

- **Lean verifier.** `Main.lean` takes the circuit file and the public file as paths, and `Statement.lean` binds the circuit file's hash (`c.sha`) into the statement digest. The verifier should load the program, the partition and each statement from its own archive, keyed by content digest, and never from the prover's session directory. A digest is only a lookup key into what it already holds. The same applies to `flock-live serve`. Owner: **Lean verifier**.
- **Private track.** `backends/flock/python/verity_flock/recursion/` (PR #97): C and its partition are bound by c. Keep them as two separable parts under c (question 6). I.11's holography, where c is a salted Ligerito commitment to Enc(C)'s bit columns, now lands in R3/R4. Owner: **private recursion**.

### 5. Tap exactness stays outside the proof's claim (question 7)

- `integrations/vllm/verity_vllm/properties/record.py` (`REGISTRY`: `fa_tap_exactness`, the norm tap, non-interference), `check/verdict.py` (`properties`, the run's citations) and `pipeline/report.py`. They stay run citations, never inputs to a statement, the IntegrityProfile, sampled proofs or the Lean verifier.
- A boundary test could pin that `backends/flock/verifier` and `protocols/sampled_proofs` never read `verity_vllm.properties`.
- Owner: **vLLM**.

### 6. How commitments are computed is out of scope

- There is no code to change. The check: no claim id in `packages/verity/src/verity/claims` states the correctness of serving's committers as a proof assumption. Table 1 cites binding (collision resistance) and hiding only. Owner: **core**.

### 7. The commitment layout (question 4)

- The rule lives in the scheme (`verity.commitments`, `CommitmentScheme.leaf_layout` in `scheme.py`). Any remaining free choice, such as row orientation or whole-row leaves of 1.5 KB and up at the re-baseline, goes into the partition's description so that one digest fixes every leaf position. Owners: **partition checker** and **core**.

### 8. Glossary

- Repo `README.md` Glossary (line 356 on): add program (the circuit a proof claims something about), partition, committed set, commitment layout and instrumented program. Adopt gate, wire (an edge), port (a named array of elements), element, format and value. Rewrite "Input" (line 362: "one concrete assignment to a subcircuit's input wires") as an assignment of values to a subcircuit's input gates. Owner: **core**.

The derived instrumented program (option C) needs no code until its first consumer.

## Part 2. Code identifiers that depart from the adopted vocabulary

Don't rename any of these before the owner decides. Names that are serialized (in conformance vectors, manifests, statement ids or recorded roots) change only with regenerated vectors, or stay as serialized names. "Word" as data (a bit pattern, such as "the bf16 word") is fine in code; only structural uses are listed.

- **`verity.ir.types.Value`** (`Value<w>`, "one gate produces exactly one `Value<w>`"): a multi-bit gate output. It goes away with the Boolean IR. Owner: **core** (Boolean IR lane).
- **`ValueRef`, `boundary_values`, `required_values`, `RequiredValues`** in `packages/verity/src/verity/proofs/query.py`, also in `proofs/lowering.py` and `proofs/packed.py`. They name places, which the vocabulary calls gates and elements. Candidates: `GateRef` or `ElementRef`, `boundary_elements`, `required_elements`, `RequiredElements`. Owner: **partition checker**.
- **The same names in vLLM**: `query/required.py`, `query/program_view.py`, `query/norm_scales.py`, `query/module_body.py`, `correspondence/resolve.py`, `check/replay/coverage.py`, `check/replay/population.py`, `commit/padding_steps.py`, `commit/committer/native_host.py`, `pipeline/commit.py`, `pipeline/manifest.py`. The "required-value manifest" is a serialized format name (`query/manifest/format.py`). Owner: **vLLM**.
- **`Q_word_v1`** (`integrations/vllm/verity_vllm/query/word.py`, `query/norm_scales.py`, `pipeline/manifest.py`, `pipeline/program_graph.py`) becomes the port-width cut, with no "word" and no version in its name. The `--word-check` flag, `VERITY_WORD_CHECK` and `word_check` (`pipeline/manifest.py` lines 210 and 229) follow. Owners: **vLLM**, then **partition checker** when the cut moves into `verity.query`.
- **Structural "word" in commitments**: `RowLeaf.word_bits` and `n_words` (`packages/verity/src/verity/commitments/rowleaf.py`), `word_bits` in `commitments/poseidon2_babybear.py` and in `backends/flock/python/verity_flock/instances.py`, and `chunk_words` (`commitments/vllm_v1/__init__.py`, `integrations/vllm/verity_vllm/commit/hidden_stream.py`) are element widths and counts: `element_bits`, `n_elements`. They are likely serialized in leaf layouts and vectors. Owner: **core** (commitments), **vLLM** for `hidden_stream.py`, **M0 prover** for `instances.py`.
- **frame-v3 `Port`** and its `ports` map (`commitments/frame_v3/__init__.py`, the "committed ports" wording in `commitments/scheme.py`), and the `port` argument of hm96's `root` and `verify_path`: each is one committed tree with its domain and leaf kind, not a circuit port. Candidates: committed array or tree. The names are serialized, so they may stay. Owner: **core**.
- **Flock lowering's `wires`**: `lower_gates(..., wires: dict[int, list])` and "constant wires" in `backends/flock/python/verity_flock/ir_lower.py`, and `wires` in `ir_sampling.py`, map a gate index to its bit columns: the output-signal sense the vocabulary drops. Candidates: `bits` or `gate_bits`. Owner: **M0 prover**.
- **Flock bench's expanded-circuit flag**: `backends/flock/python/verity_flock/bench.py` lines 189 and 257 pass the expanded-circuit file under a flag named with the term the Project retired, and line 346's description repeats it. Rename to a circuit-file flag. Owner: **M0 prover**.
- **The non-interference docstring**: `integrations/vllm/verity_vllm/properties/noninterference.py` line 1 says "the observer changes nothing the model computes". Since "model" never names the proved object, it should say "the program". Owner: **vLLM**.

Not renames: `ExecutionTranscript` and `verity.ir.layout` or `boundary`'s edge-sense "wire" already match. Proofs' "wire format" is a serialization term. The flock-live "coin server" names describe that component's implementation, which the "say verifier" rule allows.
