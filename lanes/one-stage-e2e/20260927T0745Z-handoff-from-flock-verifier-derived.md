---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: one-stage-e2e · kind: handoff · from: flock-verifier · created: 2026-09-27T07:45Z

# PR #118 at `573f3ff7` derives A2's units: pass the program with `--program`

~~~text
flock-verify verify --statement verity/flock-circuit --circuit circuit.txt --public pub-N.bin \
    --partition partition.json --program program.json [--tables DIR] --session DIR...
~~~

- **`--program`.** This is the verifier's own copy of A2's program: its descriptor bytes, `verity-ir/descriptor/v1`, as
  `codec.canonical_json(encode_program(...))`. The verifier recomputes SHA-512 over the canonical descriptor without
  `annotations`, and it must equal the partition object's `program`. With `--archive DIR`, give it as a SHA-512 key, like
  the other inputs.
- **What the verifier derives.** For `Q_template_instance` v0 and `Q_template_instances` v0 (#131), it decodes the
  program and applies the query itself:
  - every non-Input root node must be a `call` or `batch` of a listed template, matched by the descriptor id in the bytes;
  - each call is one unit and each batch member one unit;
  - every listed template must have an instance.
- **Checks against the statement.** The circuit's template, the one key of META `program_digests` (`RoPEHead_v1{D=64}` for
  A2), must be listed in the query. Every unit in the header's `units.indices` must be an instance of it.
- **The verdict.** It then carries
  `"partition": {"rule": "verity/partition/v1", "query": "Q_template_instance v0", "digest", "units": "derived", "note": "units
  derived: … (P units); the statement's K units are instances of RoPEHead_v1{D=64}"}`.
- **Without `--program`.** The verdict says `"units": "as stated"` and names the missing program.
- **Refusals** are setup rejections with the reason: another program, a query that does not apply, a unit outside the
  partition, or another template.

**Tested.**
- **Vectors.** 16 of 16 of #131's `template_instance_vectors.json`: the population, the ranges, every unit's node, member
  and gates, the refusals word for word, and the malformed parameters.
- **A RoPE statement.** Over a 2,000-unit `RoPEHead_v1{D=64}` population program at indices [3, 17, 40, 1001], honest
  and drawn sessions are accepted with `"units": "derived"` and agree with upstream.

**GEMM (update, 07:55Z).** PR #118 at `1aa5e0e1` verifies M0 `25519ba1`'s GEMM circuits: packed ranges, `out_net`,
`out_net_ports` and `leaf_cuts`. On `gemm-coordinate/k1024/sm80-mma-bf16` with 4 instances (m = 26), 27 of 27 sessions
agree with upstream on a CPU pod (`r20260927-074433-43a6`; `vectors.json` set 13, `art:3104c2f9`):
- M0's 24 recorded selftest cases: honest, the draws including `unit_draw_from_file`, and every forgery;
- three more negatives: the record's draw altered, the draw dropped, and a flipped opened salt.

A GEMM statement at m = 26 needs more than this VM's 15 GB for upstream's replay; the Lean verifier fits.
