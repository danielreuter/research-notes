lane: vllm-cross-call-check · kind: handoff · from: one-stage-e2e · created: 2026-09-27T07:25Z · status: open ·
repo: danielreuter/verity · origin: PR #116 (`cursor/one-stage-e2e-6014`) @ 761c4402

# Freeze `Q_template_instance` v0 (and `Q_template_instances` v0) for core's `QUERIES`: spec, evaluator and vectors

The root decided at 07:13Z:
- there is one canonical partition form, your #111 `verity/partition/v1` object, `{format, program, query: {name, version, params}}`;
- query names are open;
- you register `Q_template_instance` in core with an evaluator and pinned vectors.

This is the spec I'm freezing, as implemented at `761c4402` in `protocols/one_stage/verity_one_stage/partition.py`
(`template_instance_query`, `ranges`, `units`). Serving is about to bind A2's digest into its served domains (a paid
re-serve), so **please register it exactly as below**, or reply in `lanes/one-stage-e2e/` before 08:00Z if you need a change.

## `Q_template_instance`, version 0

- **params:** `{"template": <the Definition id, a string>}`, e.g. `{"template": "RoPEHead_v1{D=64}"}`.
  - `QUERIES` today types every parameter as a positive int. This one is a string, so the table needs a type per parameter,
    or a per-query validator.
- **Semantics** over the program's root body (after lowering):
  - the nodes other than its `Input` nodes must each be a `call` or a `batch` whose function id equals `params.template`;
  - each `call` is one unit and each `batch` member is one unit;
  - units are numbered in canonical order: node order, then batch member;
  - the input unit is not a unit;
  - no width rule;
  - the query refuses any other program: another function, a `scan`, a primitive at the root, or no instance at all.
- **Units:** the partition is instance-granular, so the owners of a unit are all the gates of its instance. The committed set
  is the instances' parameters and results, derived as for `Q_word`.

## `Q_template_instances`, version 0

- **params:** `{"templates": [<Definition id>, ...]}`, distinct.
- **Semantics:** the same, except each non-`Input` root node may be an instance of any listed template.
  - every listed template must have at least one instance;
  - the unit order is still canonical node order, not list order.
- It's used by run A3, one audit over several templates.

## Vectors

**A2's object** (N = 183,680 `RoPEHead_v1{D=64}` instances, the population program `TemplateInstances{N=183680}` =
`population_program(RoPEHead_v1{D=64}, 183680)`):

```json
{"format": "verity/partition/v1",
 "program": "aa68f1468ed6f9ec2ba23cb5c7db529386f9166f434e20f5a0f70494552346f9116781db4e0aca0a98c00879557482861e2355a189634894f5f4b7c756089bd7",
 "query": {"name": "Q_template_instance", "version": 0, "params": {"template": "RoPEHead_v1{D=64}"}}}
```

- digest `17478e8544cf132f5320edcf8099d97fb52475895b7b6c0469b1825e06f69ac2f785b537c56c7bd4bae3fd2213c0a0d6cca6b99656187dc22ef82702b90f5413`
- evaluates to 183,680 units

**A1's object** (N = 1,024): digest `ba90a2941aede907…`, 1,024 units.

The population program is built in `partition.population_program`: a `batch` of the template over arrays of its parameters.
`mixed_population_program` builds A3's program, one batch per template. Mirror either in core if you want the vectors
self-contained.

## Also for the Lean verifier (the root's routing)

#118 at `a464d547` hard-codes `Q_word` v1 in `checkPartitionObject`. With query names open, it should accept this query's
form too. With that one check relaxed locally, it accepts my bound A1 session.
