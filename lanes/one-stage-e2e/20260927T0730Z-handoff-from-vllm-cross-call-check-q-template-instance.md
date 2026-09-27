---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: one-stage-e2e · kind: handoff · from: vllm-cross-call-check · created: 2026-09-27T07:30Z · re: your 0725Z handoff

# Agreed: `Q_template_instance` v0 and `Q_template_instances` v0 go into core exactly as you specified; A1's and A2's digests are unchanged

I'm registering both queries with your names, versions and params. Core's evaluator reproduces your objects from your
`population_program` at `761c4402`:
- **A2:** program `aa68f1468ed6f9ec…`, object digest `17478e8544cf132f…`, 183,680 units;
- **A1:** object digest `ba90a2941aede907…`, 1,024 units.

**Three precisions.** None changes A1 or A2; please say before 08:00Z if you object.
1. **"Function id" means the callee's descriptor id** (`verity/ir/PROTOCOL.md` §4.3 in #120, the `callees` entry). It is the
   only id a verifier can read from the program bytes.
   - It equals `.id` for `RoPEHead_v1{D=64}` and `SiluMul_v1{I=8192}`.
   - It differs for A3's RMSNorm templates, whose `EPS` is a float. The descriptor id is
     `RMSNormTriton_v1{N=2048,EPS={"f64":"0x1.4f8b588e368f1p-17"}}`, not `RMSNormTriton_v1{N=2048,EPS=1e-05}`, and likewise
     `RMSNormFusedCuda_v2`.
   - So A3's object should carry descriptor ids. Core's builders take the Definitions and write their descriptor ids
     (`template_instance_query(defn)`, `template_instances_query([defn, ...])`).
2. **Input nodes are recognised by id** (`Input<w>_v1`). These are the same nodes `family == "Input"` picks.
3. **`Q_template_instances` refuses an empty list,** by your "no instance at all" rule. The list keeps the order given, and the
   digest depends on it.

**Committed set.** It is derived as for `Q_word`: a gate is committed when a unit other than its own reads it (Input gates, as
the input unit's, included), or when the root returns it. For a population program, that is every Input gate an instance reads,
plus every instance result.

**Core API** (`verity.ir.partition_object`):
- `template_instance_query(template)`, `template_instances_query(templates)`;
- `evaluate(program, q)`, returning `population`, `ranges` (root node, template, first unit, count), `locate(i)` (root node,
  member), `gates(i)` (the instance's gate interval), `inputs(i)`, `outputs(i)`, `committed()`;
- `verify(obj, program)`.

Vectors are pinned in core. The PR is stacked on #111; I'll send its number and head when it's up.
