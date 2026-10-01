---
id: 20261001T2322Z-reply-from-red-team-proofs-554-registered-inputs-pr-723
campaign: overnight
lane: proofs
kind: reply
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

# #723 (registered inputs, `program_data`) at `51069d4a2`: DENY, one small fix to grant

Reviewed head `51069d4a2372910cb5cc9f4655b13168fee2a70c`. The head moved while I worked: `68f4f081c` gained the #717 R1–R3
commit. I reviewed both. Evidence (probes, outputs, `tests/ir` log, the R1–R3 diff):
`art:bc517027f24c3d5f56fdc96196a683f5ddf94ae94fc2f31e935891abb6c35707`.

Label: `finding` on `pr:723@51069d4a2372910cb5cc9f4655b13168fee2a70c` ("DENY by red-team: …"), with no `grant`. The
vocabulary has no `deny` key, and the store refused `deny red-team`. A denial is the absence of `grant red-team` on the head,
which keeps the merge queue closed. The `finding` label says why.

The deny is for one finding, L1: an input node inside a Definition's body. The fix is small, and it breaks nothing in the
catalog. Additivity, fail-closed behaviour and binding for root parameters all hold. With L1 fixed, I would grant.

## R1–R3 commit (`68f4f081c..51069d4a2`)

The commit does what its message says:

- `evaluate_call` starts every owner at -1 and raises on a gate in two units or in none. The monkeypatched test covers both
  cases. `gaps` reports local gate indices through `keep`.
- PROTOCOL §11 says a work-crediting consumer (PoUW) does not take `Q_call` v1.
- The Glossary's committed set is now "every computing gate a Call returns", which matches `call_committed` and §11.

`tests/ir`: 285 passed at the head.

## 1. Additive and fail-closed

**Additive: yes.**

- `format_vectors.json` only gains `binding_ids` and `registered_program`. No existing key changes.
- No other vector file changes.
- A program with no registered parameter has the same bytes and digests as before.

**Python decoder: closed.** `codec._lookup_primitive` (`codec.py:509`) materializes both input families from the id. Every
mutation I tried is refused:

- the key aliased to `Input32_v1`: "a primitive is keyed by its id";
- a parameter added: "signature differs from the registry";
- the width changed: "signature differs from the registry".

**Lean: closed, for a reason other than the PR says.** The Lean *decoder* accepts `RegisteredInput32_v1` as an ordinary
parameterless primitive. `inputWidth?` (`Program.lean:303`) matches only ids starting with `Input`. The refusal comes later,
in query derivation:

- `Q_word`: `Prog.calls` (`Program.lean:707`) keeps the registered batch as a Call. `Extract.lean:257` then refuses it with
  "query-inapplicable: root node k has form 'batch'". This happens on every registered subset; the all-run program is cut.
- Template query: `TemplateQuery.isInput` (`TemplateQuery.lean:41`) doesn't skip it, so Lean answers "query-refused: root
  node 1 is a batch of 'RegisteredInput32_v1'". Python accepts the same program with population 2.

So Lean and Python disagree on `Q_template_instance` for a registered program. It fails closed, but no agreement vector covers
it (`tq.json`).

**Consumers that match by family (`family == "Input"`): safe.**

- `ir_lower`, `boolean_export` (gates), the IR evaluator, `liveness`, `query_ast`;
- `proofs/lowering.py:807`, which feeds `typed_obligation`'s `INPUT` op;
- `circuit_check`, `sampled_proofs/plan`;
- vLLM's `boolean`, `lifted`, `dump`, `provenance`, and `workload.py:40` (family or prefix).

**Consumers that match by id prefix:**

- `verity_flock/partition_units.py:99` does `startswith(("Const","Input"))`. A `RegisteredInput` is reported as a primitive
  with no piece, which is closed.
- `verity_vllm/check/match/program_compare.py:90,106` does `fid.startswith("Input")`. A registered batch becomes an instruction
  (`batch:RegisteredInput…`), not an input, so weight fields and seed canonicalisation never see it. Against a run-input
  program this is a structural mismatch, which is closed. No vLLM path builds a registered program yet, so this goes under
  item 7 of section 4.
- `verity_flock/boolean_export.py:1455-1460` (`_roles`) still writes `bind: "run"` for a root constant. That is the
  pre-ruling model. It is metadata only.
- `verity_flock/circuit_types.py:25` has a stale docstring: "Every constant inside a type is bound at registration
  (`verity.ir.constants`)".

## 2. Binding: yes, for root parameters

I built every registered subset of a 3-parameter root (`RgTop`, parameters x, w, b): 8 subsets.

- All 8 have distinct SHA-256 and SHA-512 program digests.
- The root key is `Root[RgTop_v1]_v1` in all 8. The binding lives in the root body's callee ids, which the digest covers.
- Layout, gates and Calls are identical across the 8. `Q_call` owners are identical, and so is the `Q_word` verdict.

Moving a value between registration and run therefore changes the digest. The decoder refuses the alias, the parameter
and the width mutations listed in section 1.

## 3. Leaks

- **Root inputs: F1 holds.** Data reaches a Call as parameter leaves, `("i", leaf)` (`cut.py:612`).
- **Constants:** the remaining `("c", prim id)` tokens (`cut.py:610`) are operation bits once a program is converted, which
  the ruling makes public.
- **Recompute report:** for root inputs it reveals only which leaves a gate reads.

Three gaps remain:

**L1 (the deny): an input node inside a Definition's body is accepted, and nothing binds it.**

The counterexample is `RgInner(x) = (x + RegisteredInput32, x + RegisteredInput32)`, called from a root with one run
parameter x. The Builder, the encoder, `decode_program` and Lean's `qword-program` all accept it.

- `constants.inputs` gives `{registration: [], run: [0]}`. Yet `constants.binding_time` labels gates 1 and 2 `registration`.
  The two disagree inside the PR's own module.
- `program_data` returns `{}`.
- The reference evaluator raises `MissingValue: Input gate 1 has no prescribed value` when given the listed inputs. Its value
  is whatever the transcript writer, the prover, supplies:
  - prescribing (1, 1) returns (6, 6);
  - prescribing (2, 9) returns (7, 14).
- `Q_call` keys both inner gates as `("c", "RegisteredInput32_v1")`, so `verify` reports `recomputed_across [[1,0]]`. Lean's
  `qword-program` reports the same `recomputed [[1,0]]`. The report calls 7 and 14 equal.
- `Q_word` treats them as structure (`free = 2`).

This contradicts the PR's own claims:

- "A value enters a Program only as an input gate, of one of two binding times" (`constants.py:5`);
- "a Program holds no data" (PROTOCOL §5.3, line 271);
- "data reaches a Call only through its parameters … compared by leaf, never by value" (§11, lines 460-461; `cut.py:100`).

The fault already existed for `Input<w>`. #723's guarantees, though, depend on it being impossible.

Fix, which I recommend:

- Refuse an input node outside the Program root, in `Program.__init__` (or the Builder) and in `decode_program`.
- Add a `REJECT` vector for it in `test_format_spec.py`.
- Refuse it in Lean's decoder in the same change. `qword_program_agree.py:96-103` requires Lean to refuse every `REJECT`, so
  `lean-agreement` must run (the change touches `backends/flock/`).

This breaks nothing: 0 inner input nodes in the 856 bodies reachable from circuit-check's catalog (`inner_scan.json`).

The alternative is to make every input gate, wherever it is, a committed input keyed by its position, so that `inputs`,
`program_data` and both recompute keys see it. That is more work for no use case.

**L2 (a condition for conversion, not for this PR): binding records hold program data in clear.**

- `EPS=1e-05`: `RMSNormTriton_v1`, `RMSNormFusedCuda_v1/v2`, `RMSNormArgCuda_v1`, `LayerNormAten/Ref_v1`.
- `CAP=30.0/50.0`: `AttentionHeadSoftcap_v1/v2/v3`.
- `C=0.5/1.0/1e-6`: `AddScalarF32/Bf16`.
- The vector program's `TRow_v1{…,C=1.5,…}`.

`program_data` reads gates, not binding records. A converted program can therefore show `program_data == {}` while its
descriptor still discloses the value. A conversion check has to look at binding records too, or such statics have to leave the
binding.

**L3 (also conversion): tables a primitive reads by index are invisible.** `program_data`'s docstring says so. C-Flock circuit
types name tables by SHA-512, which is deterministic and unsalted: anyone holding a list of candidate tables can tell from
the digest which one a program uses.
`gelu_tanh_bf16` and `tanh_rn` need to become registered inputs read through a lookup over a hidden committed table.

**`program_data` on today's roots:** `Serve_v1/v2/v4` give 16 Definitions with 246 constant gates (7 distinct); `Serve_v3`
gives 20 with 251, one of them a root constant. Passing the library as `operation` changes nothing, because the library names
only 7 primitives and 5 MUFU tables. No list of operations exists yet (Boolean FP ops, SHA-512), so conversion can't be
certified. The roots' parameters are `prompt` and `weights`, both still run inputs.

## 4. What's missing before a converted program is proved and verified end to end

1. The L1 refusal, in Python and Lean, with its `REJECT` vector.
2. Lean recognising `RegisteredInput` in `inputWidth?` / `isInputId` and `TemplateQuery.isInput`, with agreement vectors on
   registered programs: `registered_program` through `qword-program` and `template-query`. Lean doesn't evaluate `Q_call` at
   all yet.
3. The registration commitment and registered reads. That is the protocol half on `cursor/registered-values-95d4`, which I
   have not reviewed.
4. An `operation` list that `program_data` can take: which Definitions are operations.
5. Value statics (L2) converted, plus a check over binding records.
6. Program tables (L3) as registered inputs, removed from C-Flock circuit types, and the `circuit_types.py:25` docstring fixed.
7. vLLM building Programs with `registered=("weights", …)`, `program_compare` using `is_input`, and `boolean_export._roles`
   following the new binding times.
8. "Always hidden" needs C-Flock ZK. M0 reveals a drawn unit's witness, registered values included.
9. A `DecodedProgram` has no `.bindings`, so consumers must use `constants.inputs`. That is fine once L1 holds.

No staging run is needed: everything here ran on CPU from a detached worktree.
